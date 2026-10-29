"""Spot-only cross-currency returns and moment approximations; no funding accrual."""
from pathlib import Path
import numpy as np
import pandas as pd


def inverse_return(r):
    x=np.asarray(r,dtype=float)
    if not np.isfinite(x).all() or (x<=-1).any():raise ValueError('Returns must be finite and above -1')
    return -x/(1+x)


def approximate_inverse_moments(mean,variance):
    if not np.isfinite([mean,variance]).all() or mean<=-1 or variance<0:raise ValueError('Invalid moments')
    m=1+mean
    return -mean/m+variance/m**3, variance/m**4


def load_crosses(path):
    d=pd.read_excel(Path(path),sheet_name='Data',header=1,usecols=['Date','NZD','JPY'])
    d['Date']=pd.to_datetime(d.Date);d=d.set_index('Date')
    if d.index.hasnans or d.index.has_duplicates or not d.index.is_monotonic_increasing:raise ValueError('Invalid dates')
    if not np.isfinite(d.to_numpy(dtype=float)).all() or (d<=0).any().any():raise ValueError('Invalid spot prices')
    # NZD = USD per NZD; JPY = JPY per USD, so multiply to obtain JPY per NZD.
    d['NZDJPY']=d.NZD*d.JPY;d['JPYNZD']=1/d.NZDJPY
    returns=d[['NZDJPY','JPYNZD']].pct_change(fill_method=None).iloc[1:]
    return d,returns


def moments(returns):
    rows=[]
    for source,target in [('NZDJPY','JPYNZD'),('JPYNZD','NZDJPY')]:
        x=returns[source].to_numpy();y=returns[target].to_numpy();mu=x.mean();v=x.var(ddof=0)
        am,av=approximate_inverse_moments(mu,v);ym=y.mean();yv=y.var(ddof=0)
        z=x-mu;m3=np.mean(z**3);m4=np.mean(z**4)
        rows.append(dict(source=source,target=target,n=len(x),source_mean=mu,source_variance=v,
            actual_mean=ym,approx_mean=am,mean_error=am-ym,mean_error_bp=(am-ym)*10000,
            actual_variance=yv,approx_variance=av,variance_error=av-yv,
            variance_relative_error_pct=100*(av/yv-1),source_third_central_moment=m3,
            source_fourth_central_moment=m4,quadratic_variance=v/(1+mu)**4-2*m3/(1+mu)**5+(m4-v*v)/(1+mu)**6,
            zero_expansion_mean=-mu+mu*mu+v))
    return pd.DataFrame(rows).set_index('source')
