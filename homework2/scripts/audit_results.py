from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
checks=[]
prices=pd.read_csv(ROOT/'data/processed/etf_adjclose.csv',index_col=0,parse_dates=True)
returns=prices.pct_change(fill_method=None)
rf=pd.read_csv(ROOT/'data/processed/etf_cash.csv',index_col=0,parse_dates=True).iloc[:,0]
for label in ['B0','B1','B2','B3','SPY','60_40','CASH']:
    d=pd.read_csv(ROOT/'results/tables'/f'{label}_daily.csv',index_col=0,parse_dates=True)
    h=pd.read_csv(ROOT/'results/audits'/f'{label}_holdings_daily.csv',index_col=0,parse_dates=True)
    prev=h.shift(1);asset_returns=returns.reindex(d.index).copy();asset_returns['CASH']=rf.reindex(d.index)
    independent=(prev*asset_returns).sum(axis=1).iloc[1:]
    assert np.allclose(independent,d.return_before_cost.iloc[1:],atol=1e-12)
    assert np.allclose((1+d.return_before_cost)*(1-d.cost_fraction)-1,d.return_net,atol=1e-12)
    assert np.allclose((1+d.return_net).cumprod(),d.nav,rtol=1e-12)
    assert np.allclose(h.sum(axis=1),1,atol=1e-12) and h.min().min()>=0
    balances=h.mul(d.nav,axis=0)
    balances.to_csv(ROOT/'results/audits'/f'{label}_balances_per_initial_dollar.csv')
    assert np.allclose(balances.sum(axis=1),d.nav)
    checks.append({'check':label+' independent daily weights/returns/cost/NAV reconciliation','status':'PASS','observations':len(d)})
    for start,end in [('2020-01-01','2020-12-31'),('2022-01-01','2022-12-31')]:
        z=d.loc[start:end];prior=d.nav.loc[d.index<z.index[0]].iloc[-1]
        direct=(1+z.return_net).prod()-1;ratio=z.nav.iloc[-1]/prior-1
        assert np.isclose(direct,ratio,atol=1e-12)
        checks.append({'check':f'{label} independent period {start[:4]} compounding vs NAV ratio','status':'PASS','observations':len(z)})
for label in ['A0','A1','A2','A3']:
    d=pd.read_csv(ROOT/'results/tables'/f'{label}_daily.csv',index_col=0,parse_dates=True)
    assert np.allclose(d.return_net,d.RF+d.excess_component)
    assert np.allclose((1+d.return_net).cumprod(),d.nav)
    checks.append({'check':label+' synthetic capital / NAV identity','status':'PASS','observations':len(d)})
pd.DataFrame(checks).to_csv(ROOT/'results/audits/independent_accounting_checks.csv',index=False)
print(len(checks),'independent accounting/period checks passed')
