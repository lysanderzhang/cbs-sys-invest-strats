"""As-of observations, strictly historical percentiles, and AUD/JPY RV."""
import numpy as np
import pandas as pd

def asof_series(raw): return raw.ffill()  # no backfilling and no use of future data

def prior_quantile(s,q=.75,lookback=252):
    # Count previous available observations, not future values or incomplete windows.
    valid=s.dropna()
    threshold=valid.shift(1).rolling(lookback,min_periods=lookback).quantile(q,interpolation='linear')
    return threshold.reindex(s.index)

def signal(raw,q=.75,lookback=252):
    s=asof_series(raw);th=prior_quantile(s,q,lookback)
    z=(s<=th).astype(float);z[th.isna()|s.isna()]=np.nan
    return z,th,s

def realized_audjpy(d,window=21):
    # AUD=USD/AUD and JPY=JPY/USD, so AUD*JPY=JPY/AUD.
    cross=d.AUD*d.JPY
    r=cross.pct_change(fill_method=None)
    return r.rolling(window,min_periods=window).std(ddof=1)*np.sqrt(252)

def regimes(raw):
    s=asof_series(raw);lo=prior_quantile(s,1/3);hi=prior_quantile(s,2/3)
    z=pd.Series(np.nan,index=s.index,dtype=object)
    ok=s.notna()&lo.notna()&hi.notna()
    z.loc[ok]='medium';z.loc[ok&(s<=lo)]='low';z.loc[ok&(s>hi)]='high'
    return z
