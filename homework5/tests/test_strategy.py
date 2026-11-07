import numpy as np
import pandas as pd
import pytest
from src.data import load
from src.config import ASSETS,CASH
from src.strategy import scores,holdings,statistics,turnover

@pytest.fixture
def prices():
    i=pd.date_range("2000-01-31",periods=40,freq="ME")
    a=np.arange(1,10)*.001
    return pd.DataFrame(np.exp(np.outer(np.arange(40),a)),index=i,columns=ASSETS)

def test_score_includes_last_month(prices):
    s=scores(prices)
    assert np.allclose(s.iloc[12],prices.iloc[12]/prices.iloc[0]-1)
    changed=prices.copy();changed.iloc[12,0]*=2
    assert scores(changed).iloc[12,0] != s.iloc[12,0]

@pytest.mark.parametrize("mode",["dual","relative","absolute","static","buffer"])
def test_long_only_and_normalization(prices,mode):
    w,r,_,_=holdings(prices,mode)
    assert (w>=0).all().all()
    assert np.allclose(w.sum(axis=1),1)
    assert len(r)==len(prices)-13

@pytest.mark.parametrize("mode",["dual","relative","absolute","buffer"])
def test_future_changes_do_not_change_holdings(prices,mode):
    w,_,_,_=holdings(prices,mode)
    altered=prices.copy();altered.iloc[25:]*=np.arange(1,10)
    w2,_,_,_=holdings(altered,mode)
    pd.testing.assert_frame_equal(w.loc[:prices.index[25]],w2.loc[:prices.index[25]])

def test_one_month_lag(prices):
    p=prices.copy();p[CASH]=1.
    w,r,_,_=holdings(p)
    d=w.index[0]
    assert d==prices.index[13]
    assert r.loc[d]==pytest.approx((w.loc[d]*p.pct_change().loc[d]).sum())

def test_absolute_tie_is_cash(prices):
    prices[:]=1.
    w,*_=holdings(prices)
    assert (w[CASH]==1).all()

def test_relative_tie_stable_first(prices):
    prices[:]=1.
    w,*_=holdings(prices,"relative")
    assert (w.VTI==.25).all()
    assert (w.EFA==0).all()

def test_wealth_and_initial_drawdown():
    i=pd.date_range("2000-01-31",periods=2,freq="ME")
    r=pd.Series([-.2,.25],index=i);s=statistics(r,r*0)
    assert s["terminal_wealth"]==pytest.approx(1)
    assert s["max_drawdown_pct"]==pytest.approx(-20)
    assert s["cagr_pct"]==pytest.approx(0)

def test_sharpe_excess_not_total():
    i=pd.date_range("2000-01-31",periods=3,freq="ME")
    r=pd.Series([.01,.02,-.01],index=i);c=pd.Series([.002,.003,.004],index=i)
    assert statistics(r,c)["sharpe"]==pytest.approx((r-c).mean()/(r-c).std()*np.sqrt(12))

def test_turnover_drift():
    i=pd.date_range("2000-01-31",periods=2,freq="ME")
    w=pd.DataFrame(0.,index=i,columns=ASSETS);w.VTI=.5;w.SHV=.5
    r=w*0;r.loc[i[0],"VTI"]=.1
    t=turnover(w,r)
    assert t.iloc[0]==pytest.approx(1.)
    assert t.iloc[1]==pytest.approx(2*(.55/1.05-.5))

def test_frozen_data_and_dates():
    _,p,q=load()
    assert p.index[0]==pd.Timestamp("2007-05-31")
    assert p.index[-1]==pd.Timestamp("2026-06-30")
    assert not p.isna().any().any()
    assert q.missing_values.sum()==0

def test_buffer_does_not_delay_absolute_exit(prices):
    prices[CASH]=1.
    w,*_=holdings(prices,"buffer")
    prices.iloc[24:,:8]=.01
    w2,*_=holdings(prices,"buffer")
    assert w2.loc[prices.index[25],CASH]==1.

def test_full_comparison_periods():
    from src.config import ROOT
    r=pd.read_csv(ROOT/"results/timeseries/portfolio_returns.csv",index_col=0)
    assert r[["Dual","Relative","Absolute","Static","Buffer","US equities","Cash"]].notna().all().all()
    assert len(r)==217

def test_module_reconstruction():
    from src.config import ROOT
    r=pd.read_csv(ROOT/"results/timeseries/portfolio_returns.csv",index_col=0)
    m=pd.read_csv(ROOT/"results/timeseries/module_returns.csv",index_col=0)
    assert np.allclose(r.Dual,m.mean(axis=1))
