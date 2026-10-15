"""Deterministic daily interest-rate sorts, normalized separately by side."""
import numpy as np
import pandas as pd
from .data import CCY

def weight_row(rates, k, method):
    if rates.isna().any(): raise ValueError('Missing yields')
    # Alphabetical tie-break, stable sort; extremal ranks receive largest weights.
    s=rates.sort_index().sort_values(ascending=False,kind='stable')
    long=s.iloc[:k]; short=s.iloc[-k:].iloc[::-1]
    w=pd.Series(0.,index=rates.index)
    for side,sign in [(long,1),(short,-1)]:
        if method=='equal': a=np.ones(k)
        elif method=='rank': a=np.arange(k,0,-1,dtype=float)
        elif method=='spread':
            a=sign*(side.to_numpy()-rates.median())
            if (a < -1e-12).any(): raise ValueError('Selected yield on wrong side of median')
            a=np.maximum(a,0)
            if a.sum()<=1e-12: a=np.ones(k)
        else: raise ValueError(method)
        w.loc[side.index]=sign*a/a.sum()
    return w

def weights(d,tenor,k,method):
    rates=d[[c+' '+tenor for c in CCY]].copy();rates.columns=CCY
    return rates.apply(weight_row,axis=1,k=k,method=method)

def portfolio_returns(w,components):
    # A row dated t is earned from close t-1 to t, with weights selected at t-1.
    return {key:(w.shift(1)*value).sum(axis=1,min_count=len(CCY)).iloc[1:]
            for key,value in components.items()}

def ranks(d,tenor):
    rates=d[[c+' '+tenor for c in CCY]].copy();rates.columns=CCY
    return rates.reindex(sorted(CCY),axis=1).rank(axis=1,ascending=False,method='first').reindex(columns=CCY)
