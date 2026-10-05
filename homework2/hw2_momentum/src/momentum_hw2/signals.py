import numpy as np
import pandas as pd

def schedule(index):
    """US session dates supplied by observed factor/ETF calendar, never business-day padding."""
    out=[]
    for period, group in pd.Series(index,index=index).groupby(index.to_period('M')):
        if len(group)<2: continue
        s,e=group.iloc[-2],group.iloc[-1]
        j=index.get_loc(e)
        out.append(dict(month=str(period),signal_date=s,decision_date=s,execution_date=e,first_return_date=index[j+1] if j+1<len(index) else pd.NaT))
    return pd.DataFrame(out)

def vol_scale(series,days=126,target=.10,floor=.05,cap=1.5):
    if len(series)<days or series.iloc[-days:].isna().any(): return np.nan
    vol=series.iloc[-days:].std(ddof=1)*np.sqrt(252)
    return min(cap,target/max(vol,floor))

def slots(momentum,cash,k=3,absolute=True):
    if momentum.isna().any(): raise ValueError('Cannot rank missing data')
    selected=sorted(momentum.index,key=lambda x:(-momentum[x],x))[:k]
    w=pd.Series(0.,index=list(momentum.index)+['CASH'])
    for x in selected:
        w[x if (not absolute or momentum[x]>cash) else 'CASH']+=1/k
    return w,selected

def etf_targets(prices,rf,cfg):
    sc=schedule(prices.index); look=cfg['lookback_months']; skip=int(cfg.get('skip_latest_month',False))
    cash_nav=(1+rf).cumprod()
    weights={x:{} for x in ['B0','B1','B2','SPY','60_40','CASH']}; audit=[]
    for j,row in sc.iterrows():
        if j<look+skip: continue
        end=sc.iloc[j-skip].signal_date; start=sc.iloc[j-skip-look].signal_date
        mom=prices.loc[end]/prices.loc[start]-1
        c=cash_nav.loc[end]/cash_nav.loc[start]-1
        w1,sel=slots(mom,c,cfg['top_k'],False);w2,_=slots(mom,c,cfg['top_k'],True)
        w0=w1*0;w0.loc[prices.columns]=1/len(prices.columns)
        spy=w1*0;spy['SPY' if 'SPY' in prices else 'CASH']=1
        bal=w1*0
        for x,v in [('SPY',.6),('IEF',.4)]:bal[x if x in prices else 'CASH']+=v
        cash=w1*0;cash['CASH']=1
        for label,w in zip(weights,[w0,w1,w2,spy,bal,cash]): weights[label][row.execution_date]=w
        for x in prices:
            audit.append({**row.to_dict(),'ticker':x,'lookback_start':start,'lookback_end':end,'momentum':mom[x],'cash_hurdle':c,'selected':x in sel,'passes_absolute':mom[x]>c,'B1_target':w1[x],'B2_target':w2[x]})
    return {x:pd.DataFrame(w).T.rename_axis('execution_date') for x,w in weights.items()},pd.DataFrame(audit)
