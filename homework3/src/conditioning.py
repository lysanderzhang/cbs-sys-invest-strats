"""The exposure decided at close t is applied only to the return ending t+1."""
from .volatility import signal

def condition(returns,raw):
    exposure,threshold,filled=signal(raw)
    held=exposure.shift(1).reindex(returns.index)
    return returns*held, held, threshold, filled

def common_period(frame):
    result=frame.dropna(how='any')
    if len(result)==0: raise ValueError('No common comparison observations')
    return result
