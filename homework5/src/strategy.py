"""Long-only, monthly rebalanced module portfolios, with explicit next-month timing."""
import numpy as np
import pandas as pd
from .config import MODULES, CASH, ASSETS

def scores(prices, lookback=12):
    return prices / prices.shift(lookback) - 1

def holdings(prices, mode="dual", buffer=0.02):
    signal = scores(prices)
    returns = prices.pct_change(fill_method=None)
    index = signal.dropna().index
    target = pd.DataFrame(0.,index=index,columns=ASSETS)
    module_rows = []
    incumbent = {m:CASH for m in MODULES}
    for d in index:
        for m,pair in MODULES.items():
            if mode in ["dual","relative","buffer"]:
                # Stable listed order resolves exact ties. Absolute equality selects cash.
                winner = max(pair,key=lambda a:signal.loc[d,a])
                if mode == "buffer":
                    old = incumbent[m]
                    if old in pair and signal.loc[d,old]>signal.loc[d,CASH] and signal.loc[d,winner]-signal.loc[d,old] <= buffer:
                        winner = old
                selected = winner if mode=="relative" or signal.loc[d,winner]>signal.loc[d,CASH] else CASH
                allocation = {selected:1.}
                incumbent[m] = selected
            elif mode=="static": allocation = {a:.5 for a in pair}
            elif mode=="absolute":
                allocation = {CASH:0.}
                for a in pair:
                    b = a if signal.loc[d,a]>signal.loc[d,CASH] else CASH
                    allocation[b] = allocation.get(b,0)+.5
            else: raise ValueError(mode)
            for a,w in allocation.items(): target.loc[d,a] += .25*w
            module_rows.append({"decision_date":d,"module":m,**{a:allocation.get(a,0.) for a in ASSETS}})
    # A target observed at month-end t earns the return from t to t+1.
    holding = target.reindex(prices.index).shift(1).dropna()
    earning = returns.loc[holding.index]
    assert np.allclose(holding.sum(axis=1),1)
    return holding, (holding*earning).sum(axis=1), signal, pd.DataFrame(module_rows)

def turnover(weights, returns):
    """Dollar traded / portfolio value, counting purchases AND sales; initial purchase from cash."""
    prior = weights.shift(1)
    prev_r = returns.shift(1)
    drift = prior*(1+prev_r)
    drift = drift.div(drift.sum(axis=1),axis=0)
    drift.iloc[0] = 0.
    drift.loc[weights.index[0],CASH] = 1.
    return (weights-drift).abs().sum(axis=1)

def statistics(r,cash):
    r = pd.Series(r).dropna()
    cash = cash.loc[r.index]
    ex = r-cash
    wealth=(1+r).cumprod()
    peak=wealth.cummax().clip(lower=1)
    cutoff=r.quantile(.05)
    return {"months":len(r),"arithmetic_pct":1200*r.mean(),"cagr_pct":100*(wealth.iloc[-1]**(12/len(r))-1),"volatility_pct":100*r.std(ddof=1)*np.sqrt(12),"sharpe":ex.mean()/ex.std(ddof=1)*np.sqrt(12) if ex.std(ddof=1)>1e-14 else np.nan,"max_drawdown_pct":100*(wealth/peak-1).min(),"worst_month_pct":100*r.min(),"var5_pct":100*cutoff,"es5_pct":100*r[r<=cutoff].mean(),"skewness":r.skew(),"excess_kurtosis":r.kurt(),"positive_months_pct":100*(r>0).mean(),"terminal_wealth":wealth.iloc[-1]}
