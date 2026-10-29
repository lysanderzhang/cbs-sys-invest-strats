"""Rates are decimal per period; doubling times are real-valued periods."""
import numpy as np
import pandas as pd
from scipy.optimize import brentq
LOG2=float(np.log(2))
LABELS={'linear_log2':'L/r','linear_069':'0.69/r','corrected_log2':'L(1/r+1/2)','corrected_069':'0.69(1/r+1/2)','rule72':'0.72/r'}


def times(r):
    x=np.asarray(r,dtype=float)
    if not np.isfinite(x).all() or (x<=0).any():raise ValueError('Positive finite decimal rates required')
    return dict(exact=LOG2/np.log1p(x),linear_log2=LOG2/x,linear_069=.69/x,
                corrected_log2=LOG2*(1/x+.5),corrected_069=.69*(1/x+.5),rule72=.72/x)


def sensitivity(rates):
    vals=times(rates);df=pd.DataFrame({'rate_decimal':rates,'rate_percent':100*np.asarray(rates),**vals})
    for k in LABELS:
        df[k+'_error']=df[k]-df.exact;df[k+'_relative_error_pct']=100*(df[k]/df.exact-1)
    return df


def rule72_exact_rate():
    return float(brentq(lambda r:np.log1p(r)/r-LOG2/.72,1e-6,1.,xtol=1e-14))
