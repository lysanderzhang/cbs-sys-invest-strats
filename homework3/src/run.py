"""Run from the project root with the shared course interpreter: -m src.run."""
import os
os.environ.setdefault('MPLCONFIGDIR',str(__import__('pathlib').Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import json, itertools, platform, hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from .data import ROOT,CCY,VOLS,load_data,quality_report,usd_spots
from .carry import currency_returns
from .portfolio import weights,portfolio_returns,ranks,weight_row
from .performance import table,stats,best,wealth,drawdown
from .volatility import regimes,realized_audjpy
from .conditioning import condition,common_period

OUT=ROOT/'results'
FIGURE_CHECKS=[]
def save(obj,name):
    obj.to_csv(OUT/name,float_format='%.12g',index_label='Date' if isinstance(obj.index,pd.DatetimeIndex) else None)

def finish(fig,name):
    fig.savefig(OUT/'figures'/f'{name}.pdf',bbox_inches='tight')
    fig.savefig(OUT/'figures'/f'{name}.png',dpi=190,bbox_inches='tight');plt.close(fig)

def plot_lines(frame,name,ylabel,transform=lambda x:x):
    fig,ax=plt.subplots(figsize=(10,4.4))
    plotted=transform(frame)
    plotted.plot(ax=ax,linewidth=1,alpha=.9)
    arr=frame.to_numpy()
    if transform.__name__=='wealth': expected=np.cumprod(1+arr,axis=0)
    elif transform.__name__=='drawdown':
        w=np.cumprod(1+arr,axis=0);expected=w/np.maximum(1,np.maximum.accumulate(w,axis=0))-1
    else: expected=arr
    for j,line in enumerate(ax.lines):
        np.testing.assert_allclose(line.get_ydata(),expected[:,j],rtol=1e-12,atol=1e-13)
    FIGURE_CHECKS.append({'figure':name,'series':len(ax.lines),'observations_per_series':len(frame),'artist_data_reconciled':True})
    ax.set(ylabel=ylabel,xlabel='',title='');ax.grid(alpha=.2)
    ax.legend(fontsize=7,ncol=3,loc='best');finish(fig,name)

def pair_comparisons(t):
    rows=[]
    for dimension in ['tenor','k','method']:
        other=[x for x in ['tenor','k','method'] if x!=dimension]
        for key,g in t.groupby(other):
            for left,right in itertools.combinations(g.index,2):
                a,b=g.loc[left],g.loc[right]
                rows.append(dict(dimension=dimension,left=left,right=right,
                    delta_sharpe=b.sharpe-a.sharpe,delta_geometric=b.geometric-a.geometric,
                    delta_es05=b.es05-a.es05,delta_drawdown=b.max_drawdown-a.max_drawdown))
    p=pd.DataFrame(rows)
    p.to_csv(OUT/'tables/paired_comparisons.csv',index=False,float_format='%.12g')
    summary=p.groupby('dimension').agg(mean_absolute_sharpe_difference=('delta_sharpe',lambda s:s.abs().mean()),
        mean_absolute_geometric_difference=('delta_geometric',lambda s:s.abs().mean()),n_pairs=('delta_sharpe','size'))
    save(summary,'tables/design_dimensions.csv')
    return summary

def scalar_audit(d,frames,weight_map):
    rows=[]
    for date in ['1999-01-04','2003-05-19','2008-09-15','2008-10-24','2010-06-04']:
        t=d.index.get_loc(pd.Timestamp(date));prev=d.index[t-1];now=d.index[t]
        dt=(now-prev).days/365
        for name,w in weight_map.items():
            tenor=name.split('_')[0];manual=0.;cash=0.
            for c in CCY:
                x0=float(d.iloc[t-1][c]);x1=float(d.iloc[t][c])
                if c in ['JPY','CAD','CHF','NOK','SEK']:x0,x1=1/x0,1/x1
                g=float(np.exp(float(d.iloc[t-1][c+' '+tenor])/100*dt))
                gu=float(np.exp(float(d.iloc[t-1]['USD '+tenor])/100*dt))
                wi=float(w.loc[prev,c]);manual+=wi*(g*x1/x0-gu)
                cash+=wi*g*x1/x0
            calc=frames.loc[now,name]
            rows.append(dict(date=date,decision_date=str(prev.date()),strategy=name,scalar_return=manual,
                vector_return=calc,error=manual-calc,usd_cancel_error=cash-calc))
    a=pd.DataFrame(rows);a.to_csv(OUT/'validation/independent_return_checks.csv',index=False,float_format='%.15g')
    assert a.error.abs().max()<1e-14 and a.usd_cancel_error.abs().max()<1e-14

def main():
    for name in ['tables','timeseries','figures','validation']:(OUT/name).mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    d=load_data();quality_report(d,OUT/'validation') # occurs before backtest
    save(usd_spots(d),'timeseries/normalized_spots.csv')
    returns={};contrib={key:{} for key in ['spot','carry','interaction']};wm={};allweights=[];examples=[]
    for tenor in ['1M','3M']:
        c=currency_returns(d,tenor)
        for key,val in c.items(): save(val.iloc[1:],f'timeseries/currency_{tenor}_{key}.csv')
        save(ranks(d,tenor),f'timeseries/rankings_{tenor}.csv')
        for k in [2,3]:
            for method in ['equal','rank','spread']:
                name=f'{tenor}_{k}_{method}';w=weights(d,tenor,k,method);wm[name]=w
                assert np.allclose(w.clip(lower=0).sum(axis=1),1)
                assert np.allclose(w.clip(upper=0).sum(axis=1),-1)
                assert np.allclose(w.abs().sum(axis=1),2)
                p=portfolio_returns(w,c);returns[name]=p['total']
                for key in contrib:contrib[key][name]=p[key]
                held=w.iloc[:-1].copy();held.index=d.index[1:]
                tmp=held.stack().rename('weight').reset_index();tmp.columns=['return_date','currency','weight']
                tmp['decision_date']=np.repeat(d.index[:-1],len(CCY));tmp['strategy']=name
                allweights.append(tmp[['strategy','decision_date','return_date','currency','weight']])
                for day in ['1999-01-01','2008-09-12','2010-06-03']:
                    s=w.loc[day]; examples.append(dict(strategy=name,decision_date=day,
                        longs='; '.join(f'{a} {b:+.5f}' for a,b in s.items() if b>0),
                        shorts='; '.join(f'{a} {b:+.5f}' for a,b in s.items() if b<0)))
    r=pd.DataFrame(returns);save(r,'timeseries/baseline_returns.csv')
    pd.concat(allweights,ignore_index=True).to_csv(OUT/'timeseries/daily_weights.csv',index=False,float_format='%.12g')
    pd.DataFrame(examples).to_csv(OUT/'tables/representative_holdings.csv',index=False)
    component_frames={key:pd.DataFrame(val) for key,val in contrib.items()}
    assert np.allclose(r,sum(component_frames.values()),atol=1e-14)
    for key,val in component_frames.items():save(val,f'timeseries/portfolio_{key}_contributions.csv')
    scalar_audit(d,r,wm)
    t=table(r)
    t[['tenor','k','method']]=pd.DataFrame([s.split('_') for s in t.index],index=t.index);t.k=t.k.astype(int)
    save(t,'tables/baseline_performance.csv');dimensions=pair_comparisons(t)
    baseline=best(r);br=r[baseline]
    save(table(r.loc['2008']),'tables/baseline_2008.csv')
    plot_lines(r,'baseline_wealth','Compounded excess-return index',wealth)
    plot_lines(r,'baseline_drawdowns','Drawdown',drawdown)
    plot_lines(r.loc['2008'],'baseline_2008','2008 compounded index',wealth)
    fig,axes=plt.subplots(3,4,figsize=(11,7),sharex=True)
    for ax,(name,s) in zip(axes.flat,r.items()):
        ax.hist(s*100,bins=np.linspace(-8,8,90),density=True,color='#305775',alpha=.8)
        ax.set_title(name,fontsize=8);ax.set_yscale('log');ax.grid(alpha=.15)
    fig.supxlabel('Daily excess return (%)');fig.supylabel('Density (log scale)');fig.tight_layout();finish(fig,'baseline_distributions')
    # Part c: common contemporaneous sample for all six actual observed changes.
    delta=d[VOLS].diff()
    corr_sample=common_period(pd.concat([br.rename('carry'),delta],axis=1))
    correlations=[]
    for period,sample in [('all',corr_sample),('2008',corr_sample.loc['2008'])]:
        for v in VOLS:
            correlations.append(dict(period=period,indicator=v,n=len(sample),
                pearson=sample['carry'].corr(sample[v]),spearman=spearmanr(sample['carry'],sample[v]).statistic))
    corr=pd.DataFrame(correlations);corr.to_csv(OUT/'tables/volatility_correlations.csv',index=False,float_format='%.12g')
    reg=pd.DataFrame({v:regimes(d[v]) for v in VOLS})
    predictive=reg.shift(1).reindex(br.index).dropna(how='any')
    contemporaneous=reg.reindex(predictive.index)
    regime_rows=[]
    for timing,rg in [('predictive',predictive),('contemporaneous',contemporaneous)]:
        for v in VOLS:
            for level in ['low','medium','high']:
                s=br.reindex(rg.index)[rg[v]==level];a=stats(s).to_dict()
                a.update(indicator=v,regime=level,timing=timing,mean_daily=s.mean(),
                    prob_loss=float((s<0).mean()),prob_below_minus2pct=float((s<-.02).mean()))
                # DD/geometric on concatenated selected days do not represent a tradable regime strategy.
                for key in ['max_drawdown','terminal_wealth','geometric']:a.pop(key,None)
                regime_rows.append(a)
    regimes_table=pd.DataFrame(regime_rows);regimes_table.to_csv(OUT/'tables/volatility_regimes.csv',index=False,float_format='%.12g')
    pred=regimes_table[regimes_table.timing=='predictive']
    contrast=pred.pivot(index='indicator',columns='regime',values='es05')
    contrast['high_minus_low_es']=contrast.high-contrast.low
    save(contrast,'tables/predictive_es_contrast.csv')
    candidate=contrast.high_minus_low_es.idxmax() # declared selection for part c, not tuned filter
    save(predictive,'timeseries/predictive_regimes.csv')
    fig,axes=plt.subplots(2,3,figsize=(10,6))
    for ax,v in zip(axes.flat,VOLS):
        frame=corr_sample[['carry',v]]
        ax.scatter(frame[v],100*frame['carry'],s=3,alpha=.25,c='#305775')
        ax.set(xlabel=f'Change in {v} (points)',ylabel='Carry return (%)',title=v);ax.grid(alpha=.2)
    fig.tight_layout();finish(fig,'volatility_scatter')
    fig,axes=plt.subplots(2,3,figsize=(10,6))
    for ax,v in zip(axes.flat,VOLS):
        vals=[100*br.reindex(predictive.index)[predictive[v]==lev].values for lev in ['low','medium','high']]
        ax.boxplot(vals,tick_labels=['Low','Medium','High'],showfliers=False)
        ax.set(title=v,ylabel='Next daily return (%)');ax.grid(alpha=.2)
    fig.tight_layout();finish(fig,'predictive_regime_distributions')
    # Part d: a single fixed rule, with a single common comparison sample.
    conditioned={};exposures={};thresholds={};signals={}
    for v in VOLS:
        cr,ex,th,filled=condition(br,d[v]);conditioned[v]=cr;exposures[v]=ex;thresholds[v]=th;signals[v]=filled
    rd=common_period(pd.DataFrame({'baseline':br,**conditioned}));ed=pd.DataFrame(exposures).reindex(rd.index)
    td=table(rd);td['active_fraction']=pd.concat([pd.Series(1.,index=rd.index,name='baseline'),ed],axis=1).mean()
    td['missed_compound_return']=np.nan
    for v in VOLS:
        off=br.reindex(rd.index).where(ed[v]==0,0.)
        td.loc[v,'missed_compound_return']=wealth(off).iloc[-1]-1
    save(rd,'timeseries/conditioned_returns_common.csv');save(pd.DataFrame(conditioned),'timeseries/conditioned_returns_full.csv')
    save(ed,'timeseries/conditioned_held_exposure.csv');save(pd.DataFrame(thresholds),'timeseries/volatility_thresholds.csv')
    save(pd.DataFrame(signals),'timeseries/asof_volatility.csv');save(d[VOLS].isna(),'timeseries/raw_volatility_missing.csv')
    ages={}
    for v in VOLS:
        pos=pd.Series(np.arange(len(d)),index=d.index,dtype=float)
        last=pos.where(d[v].notna()).ffill();ages[v]=pos-last
    save(pd.DataFrame(ages),'timeseries/volatility_signal_age.csv')
    save(td,'tables/conditioned_performance.csv');save(table(rd.loc['2008']),'tables/conditioned_2008.csv')
    winner=best(rd[VOLS]);fxwinner=best(rd[VOLS[:-1]])
    plot_lines(rd,'conditioned_wealth','Compounded excess-return index',wealth)
    plot_lines(rd,'conditioned_drawdowns','Drawdown',drawdown)
    # 2008 joint stress: observed IV/VIX levels and baseline wealth.
    fig,axes=plt.subplots(3,1,figsize=(10,7),sharex=True)
    wealth(rd.loc['2008',['baseline',winner]]).plot(ax=axes[0]);d.loc['2008',VOLS[:-1]].plot(ax=axes[1]);d.loc['2008',['VIX']].plot(ax=axes[2])
    for ax,yl in zip(axes,['Index','FX IV (%)','VIX']):ax.set_ylabel(yl);ax.grid(alpha=.2);ax.legend(fontsize=7,ncol=5)
    fig.tight_layout();finish(fig,'stress_2008')
    # Part e: compare best actual FX-implied measure and historical AUD/JPY RV.
    rv=realized_audjpy(d);rh,eh,th,filled=condition(br,rv)
    re=common_period(pd.DataFrame({'baseline':br,'FX_'+fxwinner:conditioned[fxwinner],'historical':rh}))
    te=table(re);te['active_fraction']=[1.,exposures[fxwinner].reindex(re.index).mean(),eh.reindex(re.index).mean()]
    save(re,'timeseries/historical_comparison_returns.csv');save(rh.rename('historical'),'timeseries/historical_conditioned_returns_full.csv')
    save(pd.DataFrame({'AUDJPY':d.AUD*d.JPY,'realized_volatility':rv,'threshold':th,'held_exposure':eh}), 'timeseries/historical_volatility.csv')
    save(te,'tables/historical_comparison.csv');save(table(re.loc['2008']),'tables/historical_2008.csv')
    plot_lines(re,'historical_wealth','Compounded excess-return index',wealth)
    plot_lines(re,'historical_drawdowns','Drawdown',drawdown)
    fig,axes=plt.subplots(1,2,figsize=(10,3.7))
    for label,s in re.items():
        axes[0].hist(s*100,bins=np.linspace(-8,8,100),histtype='step',density=True,label=label)
        sortedr=np.sort(s)*100;axes[1].plot(sortedr,np.arange(1,len(s)+1)/len(s),label=label)
    axes[0].set(yscale='log',xlabel='Daily excess return (%)',ylabel='Density (log)')
    axes[1].set(xlim=(-7,0),ylim=(0,.12),xlabel='Daily excess return (%)',ylabel='Empirical CDF')
    for ax in axes:ax.grid(alpha=.2);ax.legend(fontsize=7)
    fig.tight_layout();finish(fig,'historical_distributions')
    # Fixed specification checks (not optimization): extra timing lag and ACT/360.
    robustness=[]
    tenor,k,method=baseline.split('_');basew=wm[baseline]
    for label,w,basis in [('primary',basew,365),('extra_decision_lag',basew.shift(1),365),('ACT360',basew,360)]:
        sr=portfolio_returns(w,currency_returns(d,tenor,basis))['total'].reindex(br.index).dropna()
        row=stats(sr).to_dict();row['specification']=label;robustness.append(row)
    pd.DataFrame(robustness).to_csv(OUT/'tables/implementation_robustness.csv',index=False,float_format='%.12g')
    # Edge cases and exposure checks over all input days.
    medlog=[]
    for tenor in ['1M','3M']:
        for k in [2,3]:
            yy=d[[c+' '+tenor for c in CCY]]; yy.columns=CCY
            ties=0;zeros=0;fallbacks=0
            for _,row in yy.iterrows():
                s=row.sort_values();med=row.median();a=s.iloc[:k];b=s.iloc[-k:]
                ties+=int(row.duplicated().any());zeros+=int(((a==med).any() or (b==med).any()))
                fallbacks+=int((med-a).sum()<=1e-12)+int((b-med).sum()<=1e-12)
            medlog.append(dict(tenor=tenor,k=k,tie_dates=ties,zero_selected_spread_dates=zeros,fallback_side_events=fallbacks))
    pd.DataFrame(medlog).to_csv(OUT/'validation/weight_edge_cases.csv',index=False)
    components=pd.DataFrame({key:s[baseline] for key,s in component_frames.items()})
    save((components.mean()*252).rename('annualized_mean'),'tables/baseline_decomposition.csv')
    metadata=dict(baseline=baseline,candidate_c=candidate,winner_d=winner,best_fx_implied_d=fxwinner,
        influential_dimension=dimensions.mean_absolute_sharpe_difference.idxmax(),
        d_start=str(rd.index[0].date()),d_end=str(rd.index[-1].date()),d_n=len(rd),
        e_start=str(re.index[0].date()),e_end=str(re.index[-1].date()),e_n=len(re),
        correlation_start=str(corr_sample.index[0].date()),correlation_n=len(corr_sample),
        candidate_rule='Largest predictive high-minus-low 5% expected shortfall; prior rolling terciles',
        selection_rule='Sharpe descending; geometric descending; ES ascending; drawdown ascending; stable name order',
        assumptions=dict(day_count='ACT/365',yield_compounding='continuous',annual_trading_days=252,
            decision='close t using same-date observations; hold t to next row',threshold='previous 252 as-of observations; linear 75th percentile',
            missing_vol='forward fill only, no initial backfill',transaction_costs=0),python=platform.python_version())
    (OUT/'validation/figure_data_checks.json').write_text(json.dumps(FIGURE_CHECKS,indent=2)+'\n')
    (OUT/'summary.json').write_text(json.dumps(metadata,indent=2))
    print(json.dumps(metadata,indent=2));print(t.drop(columns=['tenor','k','method']).round(6).to_string());print(td.round(6).to_string());print(te.round(6).to_string())

if __name__=='__main__':main()
