import numpy as np
import pandas as pd
from .signals import etf_targets, schedule, vol_scale

def simulate(returns,rf,targets,start=None,cost_bps=10,buy_hold=False):
    if start is None: start=targets.index[0]
    dates=returns.index[returns.index>=start]
    assets=list(returns.columns)+['CASH']; n=len(assets)
    r=returns.reindex(dates).copy();r['CASH']=rf.reindex(dates)
    if r.isna().any().any(): raise ValueError('Missing eligible asset/cash returns')
    values=r.to_numpy(); w=np.zeros(n);w[-1]=1;nav=1.; rows=[]; holdings=[]; trades=[]
    target_map={d:targets.loc[d].reindex(assets).to_numpy(float) for d in targets.index if d>=start}
    for j,d in enumerate(dates):
        before=nav; old=w.copy()
        # At inception there are no overnight positions; initial order executes at close.
        gross=0. if j==0 else float(w@values[j])
        if gross<=-1: raise ValueError('Insolvent ETF NAV')
        nav*=1+gross
        pre=w.copy() if j==0 else w*(1+values[j])/(1+gross)
        turn=0.;cost=0.;pretrade_nav=nav
        if d in target_map and (not buy_hold or j==0):
            target=target_map[d]
            if target.min()<-1e-12 or abs(target.sum()-1)>1e-10: raise ValueError('Invalid long-only target')
            delta=target-pre;turn=np.abs(delta[:-1]).sum();cost=cost_bps/10000*turn
            if cost>=1:raise ValueError('Insolvent cost')
            for i,a in enumerate(assets):
                trades.append(dict(execution_date=d,ticker=a,pretrade_weight=pre[i],target_weight=target[i],delta_weight=delta[i],pretrade_nav=pretrade_nav,trade_notional=pretrade_nav*delta[i],cost_nav=pretrade_nav*cost,cost_fraction=cost,turnover=turn))
            nav*=1-cost;w=target.copy()
        else:w=pre
        if not np.isclose(w.sum(),1) or w.min()<-1e-12:raise ValueError('Drift accounting failure')
        net=nav/before-1
        rows.append(dict(date=d,return_net=net,return_before_cost=gross,RF=0. if j==0 else rf.loc[d],nav=nav,turnover=turn,cost_fraction=cost,cost_nav=pretrade_nav*cost,risky_weight_start=1-old[-1],cash_weight_end=w[-1],equity_weight_end=sum(w[assets.index(x)] for x in ['SPY','EFA','EEM','VNQ'] if x in assets),duration_weight_end=sum(w[assets.index(x)] for x in ['IEF','TLT'] if x in assets),concentration_end=np.square(w[:-1]).sum()))
        holdings.append(dict(date=d,**dict(zip(assets,w))))
    return {'daily':pd.DataFrame(rows).set_index('date'),'holdings':pd.DataFrame(holdings).set_index('date'),'trades':pd.DataFrame(trades)}

def make_b3(prices,rf,cfg,targets):
    """Gross B2 historical excess path, starting at its first eligible execution."""
    returns=prices.pct_change(fill_method=None)
    b2=simulate(returns,rf,targets['B2'],cost_bps=0)['daily']
    sc=schedule(prices.index).set_index('execution_date'); out={}; sizing=[]
    for e,w in targets['B2'].iterrows():
        s=sc.loc[e,'signal_date']
        hist=(b2.return_net-b2.RF).loc[:s]
        # Exclude inception execution, which has no strategy overnight return.
        hist=hist.iloc[1:]
        q=vol_scale(hist,cfg['volatility_days'],cfg['risk_cap_annual_volatility'],cfg['annual_volatility_floor'],cfg['risk_scale_cap'])
        if not np.isfinite(q):continue
        z=w.copy();z.iloc[:-1]*=q;z['CASH']=1-z.iloc[:-1].sum();out[e]=z
        sizing.append(dict(execution_date=e,signal_date=s,q=q,volatility=hist.iloc[-cfg['volatility_days']:].std(ddof=1)*np.sqrt(252),gross_B2_history_start=hist.index[0],observations=len(hist)))
    if not out: raise ValueError('Insufficient B3 warmup')
    return pd.DataFrame(out).T.rename_axis('execution_date'),pd.DataFrame(sizing)

def run_etf(prices,rf,cfg,start=None,delay=0):
    targets,signals=etf_targets(prices,rf,cfg)
    targets['B3'],sizing=make_b3(prices,rf,cfg,targets)
    common=targets['B3'].index[0] if start is None else start
    if delay:
        for k,t in targets.items():
            idx=[prices.index[prices.index.get_loc(d)+delay] if prices.index.get_loc(d)+delay<len(prices.index) else pd.NaT for d in t.index]
            z=t.copy();z.index=idx;targets[k]=z.loc[z.index.notna()]
        # Fixed primary start: initial fill delayed too; initial day remains cash.
    returns=prices.pct_change(fill_method=None)
    result={}
    for label,t in targets.items():
        result[label]=simulate(returns,rf,t,start=common,cost_bps=cfg['cost_bps_per_traded_dollar'],buy_hold=label=='SPY')
        result[label]['targets']=t
    return result,signals,sizing
