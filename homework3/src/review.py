"""Independent NumPy/standard-library reconstruction; no production finance imports.

Run with the shared course interpreter: -m src.review. pandas is used only for
CSV input/output and alignment. Weighting, accrual, quantiles, volatility,
performance moments and timing are recalculated here from the original CSV.
"""
from pathlib import Path
import csv,datetime as dt,math,json,hashlib,sys
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
CC=['EUR','JPY','GBP','CAD','AUD','NZD','CHF','NOK','SEK']
INV={'JPY','CAD','CHF','NOK','SEK'}
VV=['AY1wk','AY3M','AY6M','JPY3M','AUD3M','VIX']
A=252

def percentile(values,q):
    x=sorted(values);at=(len(x)-1)*q;i=int(math.floor(at));f=at-i
    return x[i]+f*(x[min(i+1,len(x)-1)]-x[i])

def moments(values):
    r=np.asarray(values,dtype=float);r=r[np.isfinite(r)];n=len(r)
    mu=math.fsum(r)/n;center=r-mu
    m2=math.fsum(center**2)/n;m3=math.fsum(center**3)/n;m4=math.fsum(center**4)/n
    sd=math.sqrt(m2*n/(n-1));q=percentile(r,.05)
    w=np.cumprod(1+r);peaks=np.maximum.accumulate(np.r_[1.,w])[1:]
    return dict(n=n,arithmetic=A*mu,geometric=math.expm1(math.fsum(math.log1p(v) for v in r)*A/n),
        volatility=math.sqrt(A)*sd,sharpe=math.sqrt(A)*mu/sd,
        skewness=math.sqrt(n*(n-1))/(n-2)*m3/m2**1.5,
        excess_kurtosis=(n-1)/((n-2)*(n-3))*((n+1)*(m4/m2**2-3)+6),
        max_drawdown=float(np.max(1-w/peaks)),worst_day=float(min(r)),
        var05=-q,es05=-float(np.mean(r[r<=q])),terminal_wealth=float(w[-1]))

def histories(raw):
    n=len(raw);filled=np.full(n,np.nan);th=np.full(n,np.nan);z=np.full(n,np.nan);reg=np.full(n,np.nan)
    seen=[];last=np.nan
    for t,value in enumerate(raw):
        if np.isfinite(value):last=value
        filled[t]=last
        if np.isfinite(last):
            if len(seen)>=252:
                history=seen[-252:];th[t]=percentile(history,.75);z[t]=float(last<=th[t])
                lo=percentile(history,1/3);hi=percentile(history,2/3)
                reg[t]=0 if last<=lo else (2 if last>hi else 1)
            seen.append(last)
    return filled,th,z,reg

def paired_sharpe_intervals(frame,pairs,reps=2000,block=20,seed=9339):
    """Percentile CIs for paired fixed realized series; not selection-adjusted."""
    x=frame.to_numpy();n=len(x);rng=np.random.default_rng(seed);nblocks=math.ceil(n/block)
    draws={label:[] for label in pairs}
    for first in range(0,reps,100):
        count=min(100,reps-first)
        starts=rng.integers(0,n-block+1,size=(count,nblocks))
        ix=(starts[:,:,None]+np.arange(block)).reshape(count,-1)[:,:n]
        samples=x[ix];sr=np.sqrt(252)*samples.mean(axis=1)/samples.std(axis=1,ddof=1)
        for label,(left,right) in pairs.items():draws[label].extend(sr[:,frame.columns.get_loc(left)]-sr[:,frame.columns.get_loc(right)])
    rows=[]
    for label,(left,right) in pairs.items():
        values=draws[label];rows.append(dict(comparison=label,delta_sharpe=moments(frame[left])['sharpe']-moments(frame[right])['sharpe'],
            ci_low=float(np.quantile(values,.025)),ci_high=float(np.quantile(values,.975)),replications=reps,block=block,seed=seed))
    return pd.DataFrame(rows).set_index('comparison')

def main():
    assert Path(sys.executable)==Path.home()/'.venvs/sys-inv/bin/python'
    out=ROOT/'results/audit';out.mkdir(parents=True,exist_ok=True)
    rows=list(csv.DictReader((ROOT/'data/raw/hw3.data.carry.FX.dly.csv').open(encoding='utf-8-sig')))
    dates=pd.DatetimeIndex([dt.datetime.strptime(v['Date'],'%m/%d/%y') for v in rows],name='Date');n=len(rows)
    rawspot=np.array([[float(row[c]) for c in CC] for row in rows]);spot=rawspot.copy()
    for j,c in enumerate(CC):
        if c in INV:spot[:,j]=1/spot[:,j]
    fx=np.full_like(spot,np.nan);fx[1:]=spot[1:]/spot[:-1]-1
    intervals=np.array([0]+[(dates[i]-dates[i-1]).days/365 for i in range(1,n)])
    rawvol=np.array([[float(row[v]) if row[v] not in ['', '#N/A'] else np.nan for v in VV] for row in rows])
    audit=[]
    def check(label,actual,expected,atol=2e-11,rtol=2e-10):
        a=np.asarray(actual,dtype=float);b=np.asarray(expected,dtype=float)
        assert a.shape==b.shape,(label,a.shape,b.shape)
        assert np.array_equal(np.isnan(a),np.isnan(b)),label+' missing alignment'
        assert np.allclose(a,b,equal_nan=True,atol=atol,rtol=rtol),label
        delta=np.abs(a-b);finite=delta[np.isfinite(delta)]
        audit.append(dict(check=label,values=int(a.size),max_absolute_difference=float(finite.max()) if len(finite) else 0.,passed=True))
    def series(name):return pd.read_csv(ROOT/'results/timeseries'/name,index_col=0,parse_dates=True)
    def metric_table(file,frame):
        saved=pd.read_csv(ROOT/'results/tables'/file,index_col=0)
        for name in frame:
            expected=moments(frame[name])
            check(file+': '+name,[float(saved.loc[name,k]) for k in expected],list(expected.values()),atol=2e-9)
    check('normalized USD-per-FCY spots',series('normalized_spots.csv').values,spot)
    supplied=np.array([[float(row[c+' ROR'].rstrip('%'))/100 if row[c+' ROR'] else np.nan for c in CC] for row in rows])
    check('supplied ROR quotation reconciliation',fx,supplied,atol=.000050001,rtol=0)
    allweights={};allreturns={};components={k:{} for k in ['spot','carry','interaction']};scalar=[]
    for tenor in ['1M','3M']:
        y=np.array([[float(row[c+' '+tenor])/100 for c in CC] for row in rows])
        usd=np.array([float(row['USD '+tenor])/100 for row in rows])
        exact=np.full_like(y,np.nan);carry=exact.copy();interaction=exact.copy()
        for i in range(1,n):
            for j in range(9):
                g=math.exp(y[i-1,j]*intervals[i]);u=math.exp(usd[i-1]*intervals[i])
                carry[i,j]=g-u;interaction[i,j]=math.expm1(y[i-1,j]*intervals[i])*fx[i,j]
                exact[i,j]=g*spot[i,j]/spot[i-1,j]-u
        for key,arr in [('spot',fx),('carry',carry),('interaction',interaction),('total',exact)]:
            check(f'{tenor} individual {key}',series(f'currency_{tenor}_{key}.csv').values,arr[1:])
        rank=np.empty_like(y)
        ordering=[]
        for i in range(n):
            order=sorted(range(9),key=lambda j:(-y[i,j],CC[j]));ordering.append(order)
            for place,j in enumerate(order,1):rank[i,j]=place
        check('rank '+tenor,series('rankings_'+tenor+'.csv').values,rank)
        for k in [2,3]:
            for method in ['equal','rank','spread']:
                name=f'{tenor}_{k}_{method}';w=np.zeros_like(y)
                for i in range(n):
                    center=sorted(y[i])[4]
                    for indices,sign in [(ordering[i][:k],1),(list(reversed(ordering[i][-k:])),-1)]:
                        a=[1.]*k if method=='equal' else (list(range(k,0,-1)) if method=='rank' else [sign*(y[i,j]-center) for j in indices])
                        assert min(a)>=0
                        if sum(a)==0:a=[1.]*k
                        for j,v in zip(indices,a):w[i,j]=sign*v/math.fsum(a)
                rr=np.full(n,np.nan)
                for i in range(1,n):rr[i]=math.fsum(w[i-1]*exact[i])
                allweights[name]=w;allreturns[name]=rr
                for label,arr in [('spot',fx),('carry',carry),('interaction',interaction)]:
                    v=np.full(n,np.nan);v[1:]=np.sum(w[:-1]*arr[1:],axis=1);components[label][name]=v
                for day in ['1999-01-04','2003-05-19','2008-09-15','2008-10-24','2010-06-04']:
                    i=dates.get_loc(day)
                    scalar.append(dict(strategy=name,decision_date=str(dates[i-1].date()),return_date=day,calendar_days=(dates[i]-dates[i-1]).days,
                        spot=float(np.dot(w[i-1],fx[i])),carry=float(np.dot(w[i-1],carry[i])),interaction=float(np.dot(w[i-1],interaction[i])),exact_return=rr[i]))
    r=pd.DataFrame(allreturns,index=dates).iloc[1:]
    saved=series('baseline_returns.csv');check('all 12 baseline returns',saved.values,r.values)
    held=pd.read_csv(ROOT/'results/timeseries/daily_weights.csv')
    for name,w in allweights.items():
        a=held[held.strategy==name].pivot(index='return_date',columns='currency',values='weight').reindex(columns=CC)
        assert list(a.index)==[str(v.date()) for v in dates[1:]]
        check('all weights '+name,a.values,w[:-1],atol=2e-12)
    for label,c in components.items():check('portfolio '+label,series('portfolio_'+label+'_contributions.csv').values,pd.DataFrame(c,index=dates).iloc[1:].values)
    metric_table('baseline_performance.csv',r);metric_table('baseline_2008.csv',r.loc['2008'])
    best=max(r,key=lambda name:(moments(r[name])['sharpe'],moments(r[name])['geometric'],-moments(r[name])['es05'],-moments(r[name])['max_drawdown']))
    assert best=='3M_3_equal';br=np.array(allreturns[best]);histories_map={};exposures={};filtered={};regimes_map={};thresholds={}
    for j,v in enumerate(VV):
        filled,th,z,reg=histories(rawvol[:,j]);histories_map[v]=filled;thresholds[v]=th;regimes_map[v]=reg
        heldz=np.r_[np.nan,z[:-1]];exposures[v]=heldz;filtered[v]=heldz*br
    check('as-of volatility',series('asof_volatility.csv').values,np.column_stack(list(histories_map.values())))
    check('all six thresholds',series('volatility_thresholds.csv').values,np.column_stack(list(thresholds.values())))
    rd=pd.DataFrame({'baseline':br,**filtered},index=dates).dropna();ed=pd.DataFrame(exposures,index=dates).loc[rd.index]
    assert series('conditioned_returns_common.csv').index.equals(rd.index)
    check('all six full filtered series',series('conditioned_returns_full.csv').values,pd.DataFrame(filtered,index=dates).iloc[1:].values)
    check('raw volatility missing flags',series('raw_volatility_missing.csv').values,np.isnan(rawvol))
    ages=np.full_like(rawvol,np.nan)
    for j in range(6):
        last=None
        for i in range(n):
            if np.isfinite(rawvol[i,j]):last=i
            if last is not None:ages[i,j]=i-last
    check('as-of signal ages',series('volatility_signal_age.csv').values,ages)
    check('all six conditioned returns',series('conditioned_returns_common.csv').values,rd.values)
    check('all six held exposure paths',series('conditioned_held_exposure.csv').values,ed.values)
    metric_table('conditioned_performance.csv',rd);metric_table('conditioned_2008.csv',rd.loc['2008'])
    for v in VV:
        t=pd.read_csv(ROOT/'results/tables/conditioned_performance.csv',index_col=0)
        check(v+' active percentage',t.loc[v,'active_fraction'],ed[v].mean())
    # Both contemporaneous and predictive regimes use the common part-(c) dates.
    preg=series('predictive_regimes.csv').replace({'low':0,'medium':1,'high':2}).to_numpy(dtype=float)
    expectedreg=np.column_stack([np.r_[np.nan,regimes_map[v][:-1]] for v in VV])
    check('daily predictive regime labels',preg,expectedreg[np.isin(dates,rd.index)])
    savedreg=pd.read_csv(ROOT/'results/tables/volatility_regimes.csv')
    for _,a in savedreg.iterrows():
        rg=np.array(regimes_map[a.indicator]);level={'low':0,'medium':1,'high':2}[a.regime]
        chosen=np.array([i for i in range(n) if dates[i] in rd.index and rg[i-1 if a.timing=='predictive' else i]==level])
        sr=br[chosen];expected=moments(sr)
        for key in ['geometric','max_drawdown','terminal_wealth']:expected.pop(key)
        expected.update(mean_daily=float(np.mean(sr)),prob_loss=float(np.mean(sr<0)),prob_below_minus2pct=float(np.mean(sr<-.02)))
        check('regime '+a.indicator+' '+a.timing+' '+a.regime,[a[k] for k in expected],list(expected.values()),atol=2e-9)
    # Level changes use actual raw observations; missing VIX differences are excluded.
    dv=np.full_like(rawvol,np.nan);dv[1:]=rawvol[1:]-rawvol[:-1]
    ok=np.isfinite(dv).all(axis=1)&np.isfinite(br)
    corr=pd.read_csv(ROOT/'results/tables/volatility_correlations.csv')
    def ranks(a):
        order=np.argsort(a,kind='stable');result=np.empty(len(a));i=0
        while i<len(a):
            end=i+1
            while end<len(a) and a[order[end]]==a[order[i]]:end+=1
            result[order[i:end]]=(i+1+end)/2;i=end
        return result
    for _,a in corr.iterrows():
        mask=ok & (np.array([v.year==2008 for v in dates]) if a.period=='2008' else True)
        x=br[mask];y=dv[mask,VV.index(a.indicator)]
        check('correlation '+a.indicator+' '+a.period,[a['n'],a.pearson,a.spearman],[len(x),np.corrcoef(x,y)[0,1],np.corrcoef(ranks(x),ranks(y))[0,1]])
    # Historical AUD/JPY: independently build yen per AUD and each 21-return variance.
    cross=rawspot[:,CC.index('AUD')]*rawspot[:,CC.index('JPY')];u=np.r_[np.nan,cross[1:]/cross[:-1]-1]
    rv=np.full(n,np.nan)
    for i in range(21,n):
        window=u[i-20:i+1];mean=math.fsum(window)/21;rv[i]=math.sqrt(math.fsum((window-mean)**2)/20)*math.sqrt(252)
    _,th,z,_=histories(rv);eh=np.r_[np.nan,z[:-1]];rh=br*eh
    hv=series('historical_volatility.csv');check('AUDJPY cross',hv.AUDJPY,cross);check('21-day realized volatility',hv.realized_volatility,rv)
    check('historical threshold',hv.threshold,th);check('historical held exposure',hv.held_exposure,eh)
    re=pd.DataFrame({'baseline':br,'FX_AY3M':filtered['AY3M'],'historical':rh},index=dates).dropna()
    assert series('historical_comparison_returns.csv').index.equals(re.index)
    check('historical common sample returns',series('historical_comparison_returns.csv').values,re.values)
    check('full historical filtered series',series('historical_conditioned_returns_full.csv').values,rh[1:,None])
    metric_table('historical_comparison.csv',re);metric_table('historical_2008.csv',re.loc['2008'])
    # Independent path check: later yield/IV inputs cannot change an earlier decision.
    # Histories are a forward state machine with explicit prior-only history; test a suffix perturbation.
    mutated=rawvol[:,1].copy();mutated[1500:]+=100
    for a,b in zip(histories(mutated),histories(rawvol[:,1])):check('future-suffix invariance',a[:1500],b[:1500])
    pd.DataFrame(audit).to_csv(out/'independent_checks.csv',index=False,float_format='%.15g')
    pd.DataFrame(scalar).to_csv(out/'manual_observations.csv',index=False,float_format='%.15g')
    # Exposure-only controls and all six individual filter diagnostics.
    controls=[];constant={};volmatched={}
    baseline=rd.baseline.to_numpy();base_stats=moments(baseline)
    for v in VV:
        z=ed[v].to_numpy();p=float(z.mean());cr=rd[v].to_numpy();st=moments(cr)
        c=p*baseline;scale=st['volatility']/base_stats['volatility'];vm=scale*baseline
        constant[v]=c;volmatched[v]=vm
        controls.append(dict(indicator=v,active_fraction=p,filtered_sharpe=st['sharpe'],constant_sharpe=moments(c)['sharpe'],
            filtered_drawdown=st['max_drawdown'],constant_drawdown=moments(c)['max_drawdown'],volmatched_drawdown=moments(vm)['max_drawdown'],
            filtered_arithmetic=st['arithmetic'],constant_arithmetic=moments(c)['arithmetic'],timing_covariance_annual=252*(np.mean(z*baseline)-p*np.mean(baseline)),
            active_mean_daily=float(np.mean(baseline[z==1])),inactive_mean_daily=float(np.mean(baseline[z==0])),active_es05=moments(baseline[z==1])['es05'],
            skipped_profit_days=int(np.sum((z==0)&(baseline>0))),skipped_gain_sum=float(np.sum(np.maximum(baseline[z==0],0))),skipped_loss_sum=float(-np.sum(np.minimum(baseline[z==0],0))),
            off_compound=float(np.prod(1+baseline[z==0])-1)))
    pd.DataFrame(controls).set_index('indicator').to_csv(out/'exposure_controls.csv',float_format='%.12g')
    pd.DataFrame(constant,index=rd.index).to_csv(out/'constant_exposure_returns.csv',float_format='%.12g')
    pd.DataFrame(volmatched,index=rd.index).to_csv(out/'volatility_matched_returns.csv',float_format='%.12g')
    ci=paired_sharpe_intervals(rd,{v:(v,'baseline') for v in VV});ci.to_csv(out/'filter_sharpe_intervals.csv',float_format='%.12g')
    cie=paired_sharpe_intervals(re,{'AY3M minus baseline':('FX_AY3M','baseline'),'historical minus baseline':('historical','baseline'),'AY3M minus historical':('FX_AY3M','historical')})
    cie.to_csv(out/'historical_sharpe_intervals.csv',float_format='%.12g')
    # One further observation of decision lag: lag BOTH currency selection and risk exposure.
    w=allweights[best];exact_3m= np.array([[math.exp(float(rows[i-1][c+' 3M'])/100*intervals[i])*spot[i,j]/spot[i-1,j]-math.exp(float(rows[i-1]['USD 3M'])/100*intervals[i]) for j,c in enumerate(CC)] if i else [np.nan]*9 for i in range(n)])
    delayed=np.full(n,np.nan)
    for i in range(2,n):delayed[i]=math.fsum(w[i-2]*exact_3m[i])
    lagged={'baseline_primary':br,'baseline_lagged':delayed}
    for j,v in enumerate(VV):
        _,_,zz,_=histories(rawvol[:,j]);lagz=np.r_[np.nan,np.nan,zz[:-2]]
        lagged[v+'_primary']=filtered[v];lagged[v+'_lagged']=delayed*lagz
    lagframe=pd.DataFrame(lagged,index=dates).dropna()
    lagtable=pd.DataFrame({v:moments(lagframe[v]) for v in lagframe}).T
    lagtable.to_csv(out/'additional_decision_lag.csv',float_format='%.12g');lagframe.to_csv(out/'additional_decision_lag_returns.csv',float_format='%.12g')
    periods=[]
    for label,part in [('pre2008',rd.loc[:'2007-12-31']),('2008',rd.loc['2008']),('2009on',rd.loc['2009-01-01':])]:
        for v in part:
            row=moments(part[v]);row.update(period=label,strategy=v,period_return=float(np.prod(1+part[v])-1));periods.append(row)
    pd.DataFrame(periods).to_csv(out/'fixed_subperiods.csv',index=False,float_format='%.12g')
    summary=dict(independent_engine='standard-library CSV parsing and NumPy; no production financial functions imported',
        input_rows=n,baseline_rows=len(r),d_rows=len(rd),e_rows=len(re),checks=len(audit),values_checked=sum(v['values'] for v in audit),all_checks_passed=True,
        selected_baseline=best,selected_filter=max(VV,key=lambda v:moments(rd[v])['sharpe']),
        extra_lag_start=str(lagframe.index[0].date()),extra_lag_n=len(lagframe),bootstrap=dict(block=20,replications=2000,seed=9339,scope='paired fixed-series pointwise 95% intervals; not selection-adjusted'),
        baseline_primary=base_stats,exposure_controls=controls)
    (out/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    verified=list((ROOT/'results/timeseries').glob('*.csv'))+list((ROOT/'results/tables').glob('*.csv'))+list(out.glob('*.csv'))
    verified += [ROOT/'data/raw/hw3.data.carry.FX.dly.csv',ROOT/'data/raw/hw3.data.carry.FX.dly.xlsx',out/'verification.json']
    verified += [ROOT/'src'/name for name in ['data.py','carry.py','portfolio.py','performance.py','volatility.py','conditioning.py','run.py','review.py','review_sources.py']]
    (out/'verified_file_hashes.json').write_text(json.dumps({str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in verified},indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['exposure_controls','baseline_primary']},indent=2))
    print(pd.DataFrame(controls).set_index('indicator')[['active_fraction','filtered_sharpe','constant_drawdown','filtered_drawdown','volmatched_drawdown']].to_string())
    print(ci.to_string());print(cie.to_string());print(lagtable[['sharpe','max_drawdown']].to_string())

if __name__=='__main__':main()
