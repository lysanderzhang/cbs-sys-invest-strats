"""Distributional statistics; loss VaR/ES are positive when tails lose money."""
import numpy as np
import pandas as pd
from scipy.stats import skew, kurtosis
A=252

def wealth(r): return (1+r).cumprod()
def drawdown(r):
    w=wealth(r); peak=w.cummax().clip(lower=1.)
    return w/peak-1

def stats(r):
    r=r.dropna()
    if len(r)<2: return pd.Series(dtype=float)
    if not np.isfinite(r.to_numpy()).all(): raise ValueError('Nonfinite return')
    if (r<=-1).any(): raise ValueError('Return at or below -100%; stop compounding a bankrupt portfolio')
    q=r.quantile(.05);sd=r.std(ddof=1);w=wealth(r)
    return pd.Series(dict(n=len(r),arithmetic=r.mean()*A,
        geometric=np.expm1(np.log1p(r).sum()*A/len(r)),volatility=sd*np.sqrt(A),
        sharpe=r.mean()/sd*np.sqrt(A) if sd else np.nan,
        skewness=skew(r,bias=False),excess_kurtosis=kurtosis(r,fisher=True,bias=False),
        max_drawdown=-drawdown(r).min(),worst_day=r.min(),var05=-q,
        es05=-r[r<=q].mean(),terminal_wealth=w.iloc[-1]))

def table(frame): return frame.apply(stats).T

def best(frame):
    # Predeclared ordering: Sharpe, geometric return, ES, drawdown, name.
    t=table(frame).sort_index();return t.sort_values(['sharpe','geometric','es05','max_drawdown'],ascending=[False,False,True,True],kind='stable').index[0]
