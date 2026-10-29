"""Reproduce the three homework analyses from unchanged local inputs."""
from pathlib import Path
import hashlib,json,os,importlib.metadata
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.cache/matplotlib'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .fx import load_crosses,moments,inverse_return
from .doubling import sensitivity,rule72_exact_rate,LABELS,times
from .options import Parameters,construction,returns


def save(frame,path,index=True):frame.to_csv(ROOT/'results'/path,index=index,float_format='%.17g')
def figure(fig,name):
    fig.tight_layout();fig.savefig(ROOT/'results/figures'/f'{name}.pdf',bbox_inches='tight');plt.close(fig)


def main():
    for x in ['tables','timeseries','figures','verification']:(ROOT/'results'/x).mkdir(parents=True,exist_ok=True)
    for x in json.loads((ROOT/'data/manifest.json').read_text()):
        assert hashlib.sha256((ROOT/x['copy']).read_bytes()).hexdigest()==x['sha256']
    d,r=load_crosses(ROOT/'data/raw/hw3.data.carry.FX.dly.xlsx');m=moments(r)
    save(d,'timeseries/fx_levels.csv');save(r,'timeseries/fx_returns.csv');save(m,'tables/inverse_moments.csv')
    stats=r.apply(lambda s:pd.Series(dict(mean=s.mean(),variance=s.var(ddof=0),sd=s.std(ddof=0),sample_variance=s.var(ddof=1),minimum=s.min(),maximum=s.max(),skewness=s.skew(),excess_kurtosis=s.kurt())))
    save(stats.T,'tables/empirical_fx_statistics.csv')
    quality=dict(level_observations=len(d),return_observations=len(r),start=str(d.index[0].date()),end=str(d.index[-1].date()),first_return=str(r.index[0].date()),missing_observations=int(d.isna().sum().sum()),duplicate_dates=int(d.index.duplicated().sum()),variance_divisor='N (empirical-distribution moments)',inverse_identity_max_error=float(np.max(np.abs(r.JPYNZD-inverse_return(r.NZDJPY)))),jensen_sum_daily_means=float(r.mean().sum()),mean_r_squared_over_gross=float(np.mean(r.NZDJPY**2/(1+r.NZDJPY))))
    (ROOT/'results/verification/data_quality.json').write_text(json.dumps(quality,indent=2)+'\n')
    rates=np.linspace(.001,.5,4991);s=sensitivity(rates);save(s,'tables/doubling_sensitivity.csv',False)
    sel=sensitivity(np.array([.001,.005,.01,.02,.04,.06,.08,.10,.12,.20,.50]));save(sel,'tables/doubling_selected_rates.csv',False)
    summary=[]
    for k in LABELS:
        for end in [.20,.50]:
            f=s[s.rate_decimal<=end+1e-12];err=f[k+'_relative_error_pct']
            summary.append(dict(method=k,start_percent=.1,end_percent=end*100,max_absolute_relative_error_pct=err.abs().max(),rmse_relative_error_pct=np.sqrt(np.mean(err**2))))
    save(pd.DataFrame(summary),'tables/doubling_error_summary.csv',False)
    opt=rule72_exact_rate();optimal=dict(rate_decimal=opt,rate_percent=100*opt,doubling_periods=float(times(opt)['exact']),rule72_periods=float(times(opt)['rule72']),equation_residual=float(np.log1p(opt)/opt-np.log(2)/.72))
    (ROOT/'results/tables/rule72_optimum.json').write_text(json.dumps(optimal,indent=2)+'\n')
    # Equal first two moments need not give equal inverse-return moments.
    examples=[]
    for name,x,w in [('two_point',np.array([-.1,.1]),np.array([.5,.5])),('three_point',np.array([-np.sqrt(.02),0,np.sqrt(.02)]),np.array([.25,.5,.25]))]:
        mu=np.dot(w,x);v=np.dot(w,(x-mu)**2);y=inverse_return(x);ym=np.dot(w,y)
        examples.append(dict(distribution=name,mean=mu,variance=v,inverse_mean=ym,inverse_variance=np.dot(w,(y-ym)**2)))
    save(pd.DataFrame(examples),'tables/moment_nonidentification.csv',False)
    p=Parameters();z=construction(p);z0=construction(p,0.);x=np.linspace(20,160,561);rr,rr4,u=returns(p,x);r0,_,_=returns(p,x,0.)
    save(pd.DataFrame({'terminal_spot':x,'unhedged_carry':u,'delta_hedged_put_overlay':rr,'put_overlay_without_delta_hedge':r0}),'timeseries/illustrative_option_payoffs.csv',False)
    oz=dict(parameters=p.__dict__,delta_hedged=z,without_delta_hedge=z0,eq2_eq4_max_error=float(np.max(np.abs(rr-rr4))))
    (ROOT/'results/tables/illustrative_option_example.json').write_text(json.dumps(oz,indent=2)+'\n')
    plt.rcParams.update({'font.family':'serif','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    fig,ax=plt.subplots(1,2,figsize=(10,3.7))
    for k,label,color in [('NZDJPY','JPY per NZD','#1d4e79'),('JPYNZD','NZD per JPY','#a25d28')]:ax[0].plot(d.index,100*d[k]/d[k].iloc[0],label=label,color=color,lw=1)
    ax[0].set(ylabel='Spot index (initial = 100)',title='Reciprocal exchange rates');ax[0].legend(fontsize=8)
    lo,hi=r.NZDJPY.min(),r.NZDJPY.max();grid=np.linspace(lo,hi,300)
    ax[1].scatter(r.NZDJPY*100,r.JPYNZD*100,s=4,alpha=.25,color='#1d4e79');ax[1].plot(grid*100,inverse_return(grid)*100,color='#a25d28',label='Exact inverse');ax[1].plot(grid*100,-grid*100,'--',color='grey',label='Negative return')
    ax[1].set(xlabel='NZD/JPY daily return (%)',ylabel='JPY/NZD daily return (%)',title='Arithmetic returns are nonlinear');ax[1].legend(fontsize=8)
    for a in ax:a.grid(alpha=.2)
    figure(fig,'fx_reciprocity')
    fig,ax=plt.subplots(1,2,figsize=(10,3.8))
    ax[0].plot(s.rate_percent,s.exact,color='black',lw=2,label='Exact')
    for k in LABELS:
        ax[0].plot(s.rate_percent,s[k],lw=1,label=LABELS[k]);ax[1].plot(s.rate_percent,s[k+'_relative_error_pct'],lw=1.2,label=LABELS[k])
    ax[0].set(xlabel='Interest rate per period (%)',ylabel='Doubling time (periods, log scale)',yscale='log',title='Exact and approximate doubling times');ax[1].set(xlabel='Interest rate per period (%)',ylabel='Signed relative error (%)',title='All five approximation errors');ax[1].axhline(0,color='black',lw=.6);ax[1].axvline(opt*100,color='grey',ls=':',lw=.8)
    for a in ax:a.grid(alpha=.2);a.legend(fontsize=7,ncol=2)
    figure(fig,'doubling_sensitivity')
    fig,ax=plt.subplots(figsize=(7.6,3.7))
    for vals,label,color in [(u,'Unhedged carry','#666666'),(rr,'Put + initial delta hedge','#1d4e79'),(r0,'Put without delta hedge','#a25d28')]:ax.plot(x,100*vals,label=label,color=color,lw=1.4)
    ax.axvline(p.strike,color='black',ls=':',lw=.8,label='Strike K');ax.axhline(0,color='grey',lw=.5);ax.set(xlabel='Terminal exchange rate (I per J)',ylabel='Normalized excess payoff (%)',title='Illustrative funded option overlays');ax.legend(fontsize=8);ax.grid(alpha=.2);figure(fig,'option_overlay')
    versions={x:importlib.metadata.version(x) for x in ['numpy','pandas','scipy','matplotlib','openpyxl','pypdf','pytest']}
    (ROOT/'requirements-lock.txt').write_text('# Recorded shared-course package versions; do not synchronize the environment.\n'+'\n'.join(f'{k}=={v}' for k,v in versions.items())+'\n')
    print('FX data:',quality);print('Inverse moments:\n',m.to_string());print('Rule 72:',optimal);print('Option illustration:',oz)

if __name__=='__main__':main()
