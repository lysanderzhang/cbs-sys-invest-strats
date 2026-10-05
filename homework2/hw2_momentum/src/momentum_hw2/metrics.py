import numpy as np
import pandas as pd
import statsmodels.api as sm

def monthly(daily):
    # Initial month-end execution charge belongs to first investable holding month.
    r=daily.return_net.copy();f=daily.RF.copy()
    first=r.index[0]
    stub=(1+r.loc[r.index.to_period('M')==first.to_period('M')]).prod()
    z=(1+r).resample('ME').prod()-1;cash=(1+f).resample('ME').prod()-1
    if len(z)>1:
        z.iloc[1]=(1+z.iloc[1])*stub-1
    z=z.iloc[1:];cash=cash.iloc[1:]
    return pd.DataFrame({'return':z,'RF':cash,'excess':z-cash})

def summary(daily):
    if len(daily)<30:return {}
    # For partitions/stress starting inside a holding history, aggregate every full month.
    full_start=daily.index[0].day<=7
    m=monthly(daily) if not full_start else pd.DataFrame({'return':(1+daily.return_net).resample('ME').prod()-1,'RF':(1+daily.RF).resample('ME').prod()-1})
    if 'excess' not in m:m['excess']=m['return']-m.RF
    ex=m.excess;vol=ex.std(ddof=1);down=np.sqrt(np.mean(np.minimum(ex,0)**2))
    nav=(1+daily.return_net).cumprod(); peaks=np.maximum.accumulate(np.r_[1,nav.values])[1:];dd=nav/peaks-1
    trough=dd.idxmin();j=nav.index.get_loc(trough);peak_value=peaks[j]
    before=np.r_[1,nav.values[:j+1]];pk=int(np.argmax(before))
    peak_date=(daily.index[0]-pd.Timedelta(days=1)) if pk==0 else daily.index[pk-1]
    recovered=nav.loc[trough:][nav.loc[trough:]>=peak_value]
    recovery=recovered.index[0] if len(recovered) else pd.NaT
    years=((daily.index[-1]-daily.index[0]).days+1)/365.25
    q=m['return'].quantile(.05);tail=m['return'][m['return']<=q]
    out=dict(start=str(daily.index[0].date()),end=str(daily.index[-1].date()),daily_n=len(daily),monthly_n=len(m),CAGR=float(nav.iloc[-1]**(1/years)-1) if (daily.return_net>-1).all() else np.nan,annual_mean=m['return'].mean()*12,annual_vol=m['return'].std(ddof=1)*np.sqrt(12),excess_vol=vol*np.sqrt(12),Sharpe=np.sqrt(12)*ex.mean()/vol if vol>1e-14 else np.nan,Sortino=np.sqrt(12)*ex.mean()/down if down>0 else np.nan,max_daily_drawdown=dd.min(),max_monthly_drawdown=((1+m['return']).cumprod()/np.maximum.accumulate(np.r_[1,(1+m['return']).cumprod().values])[1:]-1).min(),drawdown_peak=str(peak_date.date()),drawdown_trough=str(trough.date()),recovery_date=str(recovery.date()) if pd.notna(recovery) else 'unrecovered',recovery_days=(recovery-peak_date).days if pd.notna(recovery) else (daily.index[-1]-peak_date).days,skew=m['return'].skew(),excess_kurtosis=m['return'].kurt(),worst_month=m['return'].min(),worst_three_month=((1+m['return']).rolling(3).apply(np.prod,raw=True)-1).min(),hit_rate=(m['return']>0).mean(),VaR95_loss=-q,ES95_loss=-tail.mean(),tail_n=len(tail),turnover_annual=daily.turnover.sum()/years,cost_fraction_sum=daily.cost_fraction.sum(),cost_nav_sum=daily.get('cost_nav',pd.Series(dtype=float)).sum())
    if 'exposure_start' in daily:
        out.update(average_exposure=daily.exposure_start.iloc[1:].mean(),average_gross_notional=daily.gross_notional_start.iloc[1:].mean(),zero_exposure_fraction=(daily.exposure_start.iloc[1:]==0).mean())
    if 'cash_weight_end' in daily:
        out.update(average_exposure=1-daily.cash_weight_end.mean(),cash_fraction=daily.cash_weight_end.mean(),equity_concentration=daily.equity_weight_end.mean(),duration_concentration=daily.duration_weight_end.mean(),concentration=daily.concentration_end.mean())
    return out

def regression(monthly_return,ff,mom=None):
    z=monthly_return[['excess']].join(ff[['Mkt-RF','SMB','HML']],how='inner').dropna()
    if mom is not None:z=z.join(mom.rename('Mom'),how='inner')
    rows=[]
    if z.excess.std()<1e-14:return []  # Cash has deterministic zero excess, no meaningful R2/beta.
    for model,cols in [('CAPM',['Mkt-RF']),('contextual',[c for c in z if c!='excess'])]:
        if len(z)<24:continue
        fit=sm.OLS(z.excess,sm.add_constant(z[cols])).fit(cov_type='HAC',cov_kwds={'maxlags':3})
        for term in fit.params.index:rows.append(dict(model=model,term=term,coefficient=fit.params[term],HAC_se=fit.bse[term],t=fit.tvalues[term],n=len(z),r_squared=fit.rsquared,market_correlation=z.excess.corr(z['Mkt-RF'])))
    return rows
