import json
import pandas as pd
import numpy as np
from .data_sources import ROOT

def load(config):
    def read(x):return pd.read_csv(ROOT/'data/processed'/f'{x}.csv',index_col=0,parse_dates=True)
    ff=read('ff_daily');mom=read('mom_daily');vix=read('vix')
    a=ff.join(mom,how='inner')
    # Backward/as-of only; preserve source date and staleness for inspection.
    v=vix.reset_index().rename(columns={vix.index.name or 'index':'vix_date'})
    a=pd.merge_asof(a.reset_index().sort_values('date'),v.sort_values('vix_date'),left_on='date',right_on='vix_date',direction='backward').set_index('date')
    a['vix_staleness_days']=(pd.Series(a.index,index=a.index)-a.vix_date).dt.days
    a.loc[a.vix_staleness_days>7,'VIX']=np.nan
    raw={t:pd.read_csv(ROOT/'data/raw'/f'yahoo_{t}.csv',index_col=0,parse_dates=True) for t in config['etf']['tickers']}
    prices=pd.DataFrame({t:d['Adj Close'] for t,d in raw.items()})
    first=max(d['Adj Close'].first_valid_index() for d in raw.values()); last=min(prices.index.max(),ff.index.max(),pd.Timestamp(config['data_cutoff']))
    # Keep factor sessions, explicitly test missing ETF values on every market session.
    idx=ff.index[(ff.index>=first)&(ff.index<=last)]
    prices=prices.reindex(idx)
    if prices.isna().any().any():raise ValueError('Unresolved ETF missingness on factor market calendar')
    return a,prices,ff.RF.reindex(prices.index),raw

def validate(config):
    a,p,rf,raw=load(config);rows=[]; actions=[];extremes=[]
    for name,d in [('factor',a[['Mom','Mkt-RF','RF']]),('etf_prices',p)]+list(raw.items()):
        if d.index.has_duplicates or not d.index.is_monotonic_increasing:raise ValueError(name+' duplicate/unsorted')
        if name.startswith('etf') or name in raw:
            pr=d if name=='etf_prices' else d[['Close','Adj Close']]
            if (pr<=0).any().any():raise ValueError('Nonpositive prices')
        rows.append(dict(dataset=name,start=d.index.min(),end=d.index.max(),rows=len(d),missing=int(d.isna().sum().sum()),duplicates=int(d.index.duplicated().sum())))
    for t,d in raw.items():
        missing=p[t].isna().sum()
        act=d.loc[(d.get('Dividends',0)!=0)|(d.get('Stock Splits',0)!=0)]
        selected=pd.concat([act.head(3),act.tail(3),act.loc[act['Stock Splits']!=0]]).loc[lambda x:~x.index.duplicated()].sort_index()
        for date,row in selected.iterrows():
            i=d.index.get_loc(date)
            if i==0:continue
            prev=d.iloc[i-1]
            # Reinvestment reconciliation: overnight close + cash distribution.
            total=row['Adj Close']/prev['Adj Close']-1
            direct=(row['Close']+row.get('Dividends',0)+row.get('Capital Gains',0))/prev['Close']-1
            actions.append(dict(ticker=t,date=date,adjusted_return=total,close_plus_distribution_return=direct,difference=total-direct,dividend=row.get('Dividends',0),split=row.get('Stock Splits',0)))
        rets=d['Adj Close'].pct_change(fill_method=None)
        for date,r in rets.loc[rets.abs()>.2].items():extremes.append(dict(dataset=t,date=date,return_value=r,status='flag_for_review_not_clipped'))
    stale=a.loc[a.VIX.notna(),'vix_staleness_days']
    if stale.max()>7:raise ValueError('Unexplained stale VIX')
    if a[['Mom','Mkt-RF','RF']].isna().any().any():raise ValueError('Missing factor returns')
    pd.DataFrame(rows).to_csv(ROOT/'outputs/tables/data_coverage.csv',index=False)
    pd.DataFrame(actions).to_csv(ROOT/'outputs/audits/corporate_action_reconciliation.csv',index=False)
    pd.DataFrame(extremes,columns=['dataset','date','return_value','status']).to_csv(ROOT/'outputs/audits/extreme_returns.csv',index=False)
    a[['VIX','vix_date','vix_staleness_days']].to_csv(ROOT/'outputs/audits/vix_alignment.csv')
    p.to_csv(ROOT/'data/processed/etf_adjclose.csv');rf.to_csv(ROOT/'data/processed/etf_cash.csv')
    text='# Data quality and coverage\n\n'+pd.DataFrame(rows).to_markdown(index=False)+'\n\n'
    text+=f'No duplicate dates. No missing ETF observations on the common factor-session calendar {p.index[0].date()} to {p.index[-1].date()}. No missing French daily inputs. VIX backward join only; max accepted staleness {stale.max():.0f} calendar days. Pre-1990 VIX remains missing, never extended. '+f'{len(extremes)} >20% daily ETF moves flagged and retained for review.\n\n'
    text+='Yahoo Adj Close includes distributions: no cash dividend is added again. Corporate-action checks compare adjusted returns with (close + distribution)/previous close, including every supplied split event and first/last distributions. Differences reflect Yahoo backward adjustment/reinvestment convention and precision; these are internal return reconciliations. EFA2005 and EEM2005/2008 split events are preserved. Provider Close is historical split-adjusted, distinct from dividend-adjusted Adj Close; it must not be called original pre-split transaction price. Capacity uses provider Close*Volume as a vendor dollar-volume proxy. Historical volume split normalization, consolidated venue scope and closing-auction volume are not independently certified; safe capacity is therefore provisional. Targeted issuer/venue event checks are documented separately in research/corporate_actions.md; a complete independent adjusted-price/month-end return reconciliation remains unavailable. All cached input files are for authorized personal academic use; no publication/redistribution license is inferred. Databento was unnecessary and unused.\n\n'
    text+='French files are CIZ-era snapshots; current historical values may be revised. Daily size/momentum portfolios are formed daily; monthly Mom portfolios are formed monthly. RF and market data differ in aggregation conventions across frequencies; official monthly series are not used to substitute daily cash. Primary endpoints follow French daily RF/Mom August 31, 2026; September ETF/VIX observations are unused.\n'
    (ROOT/'research/data_quality.md').write_text(text)
    print(pd.DataFrame(rows).to_string(index=False))
    return a,p,rf,raw
