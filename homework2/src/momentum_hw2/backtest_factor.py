import numpy as np
import pandas as pd
from .signals import schedule,vol_scale

def factor_decisions(data,cfg,with_vix=True):
    sc=schedule(data.index); mkt=(1+data['Mkt-RF']+data.RF).cumprod(); rows=[]
    look=cfg['bear_lookback_months']
    for j,row in sc.iterrows():
        s=row.signal_date
        a=vol_scale(data.Mom.loc[:s],cfg['volatility_days'],cfg['target_annual_volatility'],cfg['annual_volatility_floor'],cfg['scale_cap'])
        if not np.isfinite(a):continue
        if with_vix:
            if j<look or pd.isna(data.loc[s,'VIX']):continue
            old=sc.iloc[j-look].signal_date;mk=mkt.loc[s]/mkt.loc[old]-1
            bear=int(mk<0);high=int(data.loc[s,'VIX']>cfg['vix_threshold_points']);g=[1.,.5,0.][bear+high]
        else:old=pd.NaT;mk=np.nan;bear=high=0;g=1.
        rows.append({**row.to_dict(),'bear_start':old,'market_lookback':mk,'VIX':data.loc[s,'VIX'] if 'VIX' in data else np.nan,'bear':bear,'high_vix':high,'regime_scale':g,'vol_scale':a,'sigma':data.Mom.loc[:s].iloc[-cfg['volatility_days']:].std(ddof=1)*np.sqrt(252),'A0':1.,'A1':a,'A2':g,'A3':a*g})
    return pd.DataFrame(rows).set_index('execution_date')

def run_factor(data,cfg,start=None,with_vix=True,cost_bps=0,annual_drag=0):
    decisions=factor_decisions(data,cfg,with_vix)
    if start is None:start=decisions.index[0]
    dates=data.index[data.index>=start];out={}
    for label in ['A0','A1','A2','A3'] if with_vix else ['A0','A1']:
        a=0.;nav=1.;rows=[]
        for j,d in enumerate(dates):
            exposure=a;cost=0.;change=0.
            excess=0. if j==0 else exposure*data.loc[d,'Mom']
            rf=0. if j==0 else data.loc[d,'RF']
            if d in decisions.index:
                new=decisions.loc[d,label];change=2*abs(new-a);cost=cost_bps/10000*change;a=new
            drag=annual_drag*exposure/252 if j else 0.
            ret=rf+excess-cost-drag
            if ret<=-1:raise ValueError('Factor capital ruined; CAGR undefined')
            nav*=1+ret
            rows.append(dict(date=d,return_net=ret,RF=rf,excess_component=excess,nav=nav,exposure_start=exposure,exposure_end=a,gross_notional_start=2*exposure,cost_fraction=cost+drag,turnover=change))
        out[label]={'daily':pd.DataFrame(rows).set_index('date')}
    return out,decisions
