from pathlib import Path
import copy,json,hashlib,datetime,platform,importlib.metadata
import numpy as np
import pandas as pd
from .data_sources import ROOT,sha
from .data_validation import load
from .backtest_factor import run_factor,factor_decisions
from .backtest_etf import run_etf,make_b3
from .signals import schedule,etf_targets
from .metrics import summary,monthly,regression
from .robustness import bootstrap,partitions

def csv(df,path,index=False):df.to_csv(ROOT/path,index=index,float_format='%.15g')

def run(config):
    a,p,rf,raw=load(config)
    fa,dec=run_factor(a,config['factor'])
    eb,signals,sizing=run_etf(p,rf,config['etf'])
    bstart=eb['B3']['daily'].index[0]
    astart=fa['A0']['daily'].index[0]
    performance=[];ledger=[];reg=[];stress=[];boot=[]
    ffm=pd.read_csv(ROOT/'data/processed/ff_monthly.csv',index_col=0,parse_dates=True)
    official=pd.read_csv(ROOT/'data/processed/mom_monthly.csv',index_col=0,parse_dates=True)
    csv(official,'results/tables/official_monthly_mom_context.csv',True)
    csv(dec,'results/audits/factor_decisions.csv',True)
    csv(signals,'results/audits/etf_signals.csv')
    csv(sizing,'results/audits/etf_risk_sizing.csv')
    sc=schedule(p.index).set_index('execution_date')
    for proto,results in [('A',fa),('B',eb)]:
        for label,z in results.items():
            daily=z['daily'];basis='synthetic cash-plus-factor gross' if proto=='A' else 'modeled net 10bps per risky dollar'
            csv(daily,f'results/tables/{label}_daily.csv',True)
            csv(monthly(daily),f'results/tables/{label}_monthly.csv',True)
            if proto=='B':
                csv(z['holdings'],f'results/audits/{label}_holdings_daily.csv',True)
                trades=z['trades'].merge(sc.reset_index(),on='execution_date',how='left')
                csv(trades,f'results/audits/{label}_trades.csv')
                csv(z['targets'],f'results/audits/{label}_targets.csv',True)
            for sample,start,end in [('full',None,None)]+partitions():
                d=daily.loc[start:end];met=summary(d)
                if met:performance.append(dict(prototype=proto,variant=label,sample=sample,basis=basis,**met))
            m=monthly(daily)
            mom=monthly(fa['A0']['daily']).excess if proto=='A' else None
            reg.extend([dict(variant=label,Mom_regressor='daily-derived static capital excess' if proto=='A' else 'none',**x) for x in regression(m,ffm,mom)])
            years=[('2008_2009','2008-01-01','2009-12-31'),('2009_rebound','2009-03-01','2009-05-31'),('2020','2020-01-01','2020-12-31')] if proto=='A' else [('2020','2020-01-01','2020-12-31'),('2022','2022-01-01','2022-12-31')]
            for period,start,end in years:
                d=daily.loc[start:end]
                if len(d):stress.append(dict(variant=label,period=period,cumulative_return=(1+d.return_net).prod()-1,**summary(d)))
            for date,value in m['return'].nsmallest(3).items():stress.append(dict(variant=label,period='mechanically_worst_month_'+str(date.date()),cumulative_return=value))
            ledger.append(dict(prototype=proto,variant=label,kind='primary',configuration='frozen defaults',start=daily.index[0],end=daily.index[-1]))
        pairs=[('A1','A0'),('A2','A0'),('A3','A0'),('A3','A1')] if proto=='A' else [('B1','B0'),('B2','B1'),('B3','B2'),('B2','B0'),('B2','60_40'),('B3','60_40')]
        for left,right in pairs:
            for sample,start,end in [('full',None,None),('historical_holdout','2020-01-01',None)]:
                l=monthly(results[left]['daily']).excess.loc[start:end];r=monthly(results[right]['daily']).excess.loc[start:end]
                boot.append(dict(prototype=proto,left=left,right=right,sample=sample,**bootstrap(l,r,config['research_seed'],config['validation']['bootstrap_replications'],config['validation']['bootstrap_block_months'])))
    # Independently re-run every ETF portfolio gross on the identical common sample.
    gross_cfg=copy.deepcopy(config['etf']);gross_cfg['cost_bps_per_traded_dollar']=0
    gross,_,_=run_etf(p,rf,gross_cfg,start=bstart)
    for label,z in gross.items():
        csv(z['daily'],f'results/tables/{label}_gross_daily.csv',True)
        csv(monthly(z['daily']),f'results/tables/{label}_gross_monthly.csv',True)
        performance.append(dict(prototype='B',variant=label,sample='full',basis='gross zero modeled trading costs',**summary(z['daily'])))
        ledger.append(dict(prototype='B',variant=label+'_gross',kind='gross attribution',configuration='0bps',start=bstart,end=p.index[-1]))
    # State diagnostics use observable lagged state active during each return interval.
    state=dec[['bear','high_vix','regime_scale','vol_scale']].reindex(a.index).ffill().shift(1).loc[astart:]
    state=state.join(fa['A0']['daily'].return_net.rename('A0_return'))
    st=state.groupby(['bear','high_vix']).agg(observations=('A0_return','count'),mean_daily_return=('A0_return','mean'),mean_vol_scale=('vol_scale','mean'))
    csv(st,'results/tables/factor_state_diagnostics.csv',True)
    pd.DataFrame({'metric':['capped_vol_scale_frequency','both_stress_frequency','any_stress_frequency'],'value':[(dec.vol_scale>=config['factor']['scale_cap']-1e-12).mean(),((dec.bear+dec.high_vix)==2).mean(),((dec.bear+dec.high_vix)>0).mean()]}).to_csv(ROOT/'results/tables/factor_sizing_diagnostics.csv',index=False)
    # Fixed one-at-a-time A sensitivities. Reuse common start after all eligibility requirements.
    aset=[('primary',config['factor'])]
    for key,vals in [('volatility_days',[63,252]),('target_annual_volatility',[.08,.12]),('vix_threshold_points',[20,30]),('bear_lookback_months',[12,36]),('scale_cap',[1.])]:
        for value in vals:
            cfg=copy.deepcopy(config['factor']);cfg[key]=value;aset.append((f'{key}_{value}',cfg))
    acommon=max(factor_decisions(a,cfg).index[0] for _,cfg in aset)
    sensitivity=[]
    for name,cfg in aset:
        results,_=run_factor(a,cfg,start=acommon)
        z=results['A3']['daily']
        sensitivity.append(dict(prototype='A',variant=name,component='A3',**summary(z)))
        csv(z,f'results/tables/sensitivity_A_{name}_daily.csv',True)
        ledger.append(dict(prototype='A',variant=name,kind='sensitivity',configuration=json.dumps(cfg,sort_keys=True),start=acommon,end=a.index[-1]))
    # Incomplete factor cost scenarios; no claim to internal Mom turnover or borrow costs.
    for c,drag in [(10,0),(25,0),(0,.01),(0,.02)]:
        results,_=run_factor(a,config['factor'],start=astart,cost_bps=c,annual_drag=drag)
        for label,z in results.items():
            name=f'{label}_incomplete_cost_{c}bps_drag_{drag}'
            sensitivity.append(dict(prototype='A',variant=name,component=label,**summary(z['daily'])))
            csv(z['daily'],f'results/tables/{name}_daily.csv',True)
            ledger.append(dict(prototype='A',variant=name,kind='incomplete_cost_sensitivity',configuration=f'2*abs(delta exposure)*{c}bps; annual exposure drag {drag}',start=astart,end=a.index[-1]))
    long,_=run_factor(a,config['factor'],with_vix=False)
    for label,z in long.items():
        csv(z['daily'],f'results/tables/{label}_long_history_daily.csv',True)
        performance.append(dict(prototype='A',variant=label,sample='long_history_without_VIX',basis='synthetic cash-plus-factor gross',**summary(z['daily'])))
        ledger.append(dict(prototype='A',variant=label+'_long',kind='long history without VIX',configuration='frozen volatility settings',start=z['daily'].index[0],end=a.index[-1]))
    bsets=[('primary',config['etf'],p,0)]
    for key,vals in [('lookback_months',[6,9]),('top_k',[2,4]),('skip_latest_month',[True]),('cost_bps_per_traded_dollar',[0,5,25,50])]:
        for value in vals:
            cfg=copy.deepcopy(config['etf']);cfg[key]=value;bsets.append((f'{key}_{value}',cfg,p,0))
    for t in p.columns:bsets.append((f'remove_{t}',config['etf'],p.drop(columns=t),0))
    bsets.append(('execution_delay_one_session',config['etf'],p,1))
    bcommon=max(make_b3(prices,rf,cfg,etf_targets(prices,rf,cfg)[0])[0].index[0] for _,cfg,prices,_ in bsets)
    for name,cfg,prices,delay in bsets:
        # Benchmarks need SPY/IEF; exclusion diagnostic only changes selection universe.
        if 'SPY' not in prices or 'IEF' not in prices:
            # Generate selections using smaller universe, retain benchmark columns at zero.
            results,_,_=run_etf(prices,rf,cfg,start=bcommon,delay=delay)
        else:results,_,_=run_etf(prices,rf,cfg,start=bcommon,delay=delay)
        for label in ['B2','B3']:
            z=results[label]['daily'];sensitivity.append(dict(prototype='B',variant=name,component=label,**summary(z)))
            csv(z,f'results/tables/sensitivity_B_{label}_{name}_daily.csv',True)
            ledger.append(dict(prototype='B',variant=f'{label}_{name}',kind='sensitivity',configuration=json.dumps(cfg,sort_keys=True)+' universe '+','.join(prices.columns),start=bcommon,end=p.index[-1]))
    # Capacity on B2/B3 actual traded weight changes, evolving pretrade NAV.
    participation=[]
    for label in ['B2','B3']:
        z=eb[label];tr=z['trades']
        for _,row in tr.loc[tr.ticker!='CASH'].iterrows():
            s=sc.loc[row.execution_date,'signal_date'];t=row.ticker
            adv=(raw[t]['Close']*raw[t]['Volume']).loc[:s].iloc[-20:].mean()
            for initial in config['capacity']['initial_aum_usd']:
                dollars=initial*row.pretrade_nav*abs(row.delta_weight)
                participation.append(dict(variant=label,ticker=t,execution_date=row.execution_date,signal_date=s,initial_aum=initial,pretrade_aum=initial*row.pretrade_nav,trade_dollars=dollars,ADV20=adv,participation=dollars/adv,illustrative_max_aum_1pct_ADV=.01*adv/abs(row.delta_weight) if abs(row.delta_weight)>1e-12 else np.nan,illustrative_max_aum_5pct_ADV=.05*adv/abs(row.delta_weight) if abs(row.delta_weight)>1e-12 else np.nan))
    pt=pd.DataFrame(participation);csv(pt,'results/tables/capacity_trades.csv')
    cap=pt.groupby(['variant','ticker','initial_aum']).participation.agg(maximum='max',p95=lambda x:x.quantile(.95),fraction_above_1pct=lambda x:(x>.01).mean(),fraction_above_5pct=lambda x:(x>.05).mean()).reset_index();csv(cap,'results/tables/capacity_summary.csv')
    active=pt.loc[pt.trade_dollars>1e-6].groupby(['variant','ticker','initial_aum']).participation.agg(trades='count',maximum='max',p95=lambda x:x.quantile(.95),fraction_above_1pct=lambda x:(x>.01).mean(),fraction_above_5pct=lambda x:(x>.05).mean()).reset_index()
    csv(active,'results/tables/capacity_active_trades_summary.csv')
    csv(pd.DataFrame(performance),'results/tables/performance.csv')
    csv(pd.DataFrame(sensitivity),'results/tables/sensitivities.csv')
    csv(pd.DataFrame(ledger),'results/tables/variant_ledger.csv')
    csv(pd.DataFrame(reg),'results/tables/regressions_HAC3.csv')
    csv(pd.DataFrame(boot),'results/tables/bootstrap.csv')
    csv(pd.DataFrame(stress),'results/tables/stress_periods.csv')
    metadata=dict(run_id=datetime.datetime.now(datetime.timezone.utc).isoformat(),config_sha256=sha(ROOT/'config/base.yaml'),python=platform.python_version(),dependencies={x:importlib.metadata.version(x) for x in ['pandas','numpy','yfinance','scipy','statsmodels']},input_hashes={str(x.relative_to(ROOT)):sha(x) for x in (ROOT/'data/raw').glob('*')},code_snapshot_hash=hashlib.sha256(b''.join(x.read_bytes() for x in sorted((ROOT/'src').rglob('*.py')))).hexdigest(),factor_execution_start=str(astart.date()),etf_execution_start=str(bstart.date()),factor_first_return=str(fa['A0']['daily'].index[1].date()),etf_first_return=str(eb['B3']['daily'].index[1].date()),endpoint=str(p.index[-1].date()),warnings=['Historical holdout inspected; no future validation','September prices unused: daily RF ends August','Primary factor results gross, capital convention synthetic','ETF costs assumed; capacity provisional','First execution stub cost assigned to first holding month for monthly statistics'])
    (ROOT/'results/audits/run_metadata.json').write_text(json.dumps(metadata,indent=2))
    print(pd.DataFrame(performance).query("sample=='full' and basis!='gross zero modeled trading costs'")[['variant','start','end','CAGR','Sharpe','max_daily_drawdown','average_exposure']].to_string(index=False))
