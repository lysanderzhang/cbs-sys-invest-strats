"""Exact arithmetic USD excess returns with calendar-day funding."""
import numpy as np
import pandas as pd
from .data import CCY, usd_spots

def currency_returns(d, tenor='1M', basis=365):
    x=usd_spots(d)
    spot=x.pct_change(fill_method=None)
    dt=d.index.to_series().diff().dt.days/basis
    y=d[[c+' '+tenor for c in CCY]].copy()/100; y.columns=CCY
    growth=np.exp(y.shift(1).mul(dt,axis=0))
    usd=np.exp(d['USD '+tenor].shift(1)/100*dt)
    carry=growth.sub(usd,axis=0)
    cross=(growth-1)*spot
    exact=growth*(1+spot)
    exact=exact.sub(usd,axis=0)
    return {'spot':spot,'carry':carry,'interaction':cross,'total':exact}
