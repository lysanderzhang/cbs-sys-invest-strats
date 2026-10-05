import numpy as np
import pandas as pd

def bootstrap(a,b,seed=9339,reps=1000,block=6):
    z=pd.concat([a.rename('a'),b.rename('b')],axis=1).dropna();n=len(z)
    if n<block:return {}
    rng=np.random.default_rng(seed)
    starts=rng.integers(0,n-block+1,size=(reps,int(np.ceil(n/block))))
    idx=(starts[:,:,None]+np.arange(block)).reshape(reps,-1)[:,:n]
    aa=z.a.to_numpy()[idx];bb=z.b.to_numpy()[idx]
    dm=(aa.mean(1)-bb.mean(1))*12
    ds=np.sqrt(12)*(aa.mean(1)/aa.std(1,ddof=1)-bb.mean(1)/bb.std(1,ddof=1))
    return dict(n_months=n,block_months=block,replications=reps,annual_excess_mean_difference=(z.a.mean()-z.b.mean())*12,annual_excess_mean_difference_low=np.quantile(dm,.025),annual_excess_mean_difference_high=np.quantile(dm,.975),Sharpe_difference=np.sqrt(12)*(z.a.mean()/z.a.std(ddof=1)-z.b.mean()/z.b.std(ddof=1)),Sharpe_difference_low=np.quantile(ds,.025),Sharpe_difference_high=np.quantile(ds,.975))

def partitions():
    return [('development',None,'2013-12-31'),('validation','2014-01-01','2019-12-31'),('historical_holdout','2020-01-01',None)]
