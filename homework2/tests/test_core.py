import numpy as np
import pandas as pd
import pytest
from momentum_hw2.data_sources import parse_french
from momentum_hw2.signals import slots,vol_scale,schedule,etf_targets
from momentum_hw2.backtest_etf import simulate
from momentum_hw2.backtest_etf import make_b3
from momentum_hw2.backtest_factor import factor_decisions,run_factor
from momentum_hw2.metrics import monthly,summary

def test_units_footer_missing_and_duplicate():
    x=b'Header\n,Mom\n20200102,1.00\n20200103,-99.99\nAnnual Returns\n2020,50\n'
    d,_=parse_french(x,True)
    assert len(d)==2 and d.iloc[0,0]==.01 and np.isnan(d.iloc[1,0])
    with pytest.raises(ValueError):parse_french(x+b'20200102,2.00\n',True)

def test_no_refill_ties_strict_absolute():
    w,sel=slots(pd.Series({'Z':.2,'A':.2,'B':.01,'C':-.3}),.01,3)
    assert sel==['A','Z','B']
    assert np.allclose(w[['A','Z','C','CASH']],[1/3,1/3,0,1/3])
    assert w.B==0 and w.sum()==1

def test_vol_floor_cap_ddof_annualization():
    assert vol_scale(pd.Series(np.zeros(126)))==1.5
    assert np.isnan(vol_scale(pd.Series(np.zeros(125))))
    x=pd.Series(np.tile([-.01,.01],63))
    assert vol_scale(x)==pytest.approx(.1/(x.std(ddof=1)*np.sqrt(252)))
    assert vol_scale(x,cap=1)==min(1,.1/(x.std(ddof=1)*np.sqrt(252)))

def toy():
    idx=pd.to_datetime(['2020-01-30','2020-01-31','2020-02-03','2020-02-04'])
    r=pd.DataFrame({'A':[0,.1,.2,0],'B':[0,0,0,.1]},index=idx)
    rf=pd.Series(.001,index=idx)
    t=pd.DataFrame({'A':[.5,0],'B':[.5,1],'CASH':[0,0]},index=idx[[0,1]])
    return r,rf,t

def test_execution_old_positions_then_new():
    r,f,t=toy();z=simulate(r,f,t,cost_bps=0)
    # Jan31 old .5/.5 earns .05; Feb3 B receives 0, ignoring A .20.
    assert z['daily'].return_net.iloc[1]==pytest.approx(.05)
    assert z['daily'].return_net.iloc[2]==0
    pre=z['trades'].query("ticker=='A'").iloc[1].pretrade_weight
    assert pre==pytest.approx(.55/1.05)

def test_full_switch_two_sided_cost_and_nav():
    r,f,t=toy();t.loc[:]=[[1,0,0],[0,1,0]]
    z=simulate(r,f,t,cost_bps=10);d=z['daily']
    assert d.turnover.iloc[0]==1
    assert d.turnover.iloc[1]==2
    assert d.cost_fraction.iloc[1]==.002
    assert d.nav.iloc[1]==pytest.approx(.999*1.1*.998)
    assert np.allclose((1+d.return_net).cumprod(),d.nav)
    assert np.allclose(z['holdings'].sum(axis=1),1)

def test_cash_and_illegal_target_missing_ruin():
    r,f,t=toy();t.loc[:]=[0,0,1]
    z=simulate(r,f,t)
    assert np.allclose(z['daily'].return_net.iloc[1:],f.iloc[1:])
    t.iloc[0]=[-1,1,1]
    with pytest.raises(ValueError):simulate(r,f,t)
    t.loc[:]=[1,0,0];r.iloc[1,0]=-1.01
    with pytest.raises(ValueError):simulate(r,f,t)
    r.iloc[1,0]=np.nan
    with pytest.raises(ValueError):simulate(r,f,t)

def test_hand_signal_cash_matched_and_eligibility():
    idx=pd.bdate_range('2018-01-01','2020-03-31')
    p=pd.DataFrame({'SPY':np.exp(np.arange(len(idx))*.001),'IEF':np.exp(np.arange(len(idx))*.0001)},index=idx)
    f=pd.Series(.0002,index=idx);cfg={'lookback_months':12,'top_k':2,'skip_latest_month':False}
    targets,audit=etf_targets(p,f,cfg);sc=schedule(idx)
    assert targets['B2'].index[0]==sc.iloc[12].execution_date
    row=audit.iloc[0];s,e=row.lookback_start,row.lookback_end
    assert row.momentum==pytest.approx(p.loc[e,'SPY']/p.loc[s,'SPY']-1)
    assert row.cash_hurdle==pytest.approx((1+f.loc[(f.index>s)&(f.index<=e)]).prod()-1)
    assert targets['B2'].iloc[0].CASH==.5

def test_future_changes_do_not_change_signal():
    idx=pd.bdate_range('2018-01-01','2020-12-31');p=pd.DataFrame({'SPY':np.exp(np.arange(len(idx))*.001),'IEF':np.exp(np.arange(len(idx))*.0001)},index=idx)
    f=pd.Series(.0002,index=idx);cfg={'lookback_months':12,'top_k':2}
    a,au=etf_targets(p,f,cfg);s=au.iloc[0].signal_date;e=au.iloc[0].execution_date
    p.loc[p.index>s]*=100;f.loc[f.index>s]=.01
    b,_=etf_targets(p,f,cfg)
    assert a['B2'].loc[e].equals(b['B2'].loc[e])

def test_factor_future_vix_unchanged_and_scale_persistence():
    idx=pd.bdate_range('2016-01-01','2020-12-31');d=pd.DataFrame({'Mom':np.sin(np.arange(len(idx)))*.01,'Mkt-RF':.0001,'RF':.00001,'VIX':20},index=idx)
    cfg={'volatility_days':126,'target_annual_volatility':.1,'annual_volatility_floor':.05,'scale_cap':1.5,'bear_lookback_months':24,'vix_threshold_points':25}
    dec=factor_decisions(d,cfg);s=dec.iloc[0].signal_date;e=dec.index[0]
    other=d.copy();other.loc[other.index>s,['Mom','Mkt-RF','VIX']]=[.1,-.1,80]
    dec2=factor_decisions(other,cfg)
    assert dec.loc[e,['A0','A1','A2','A3']].equals(dec2.loc[e,['A0','A1','A2','A3']])
    z,_=run_factor(d,cfg);x=z['A3']['daily'];assert x.exposure_start.iloc[0]==0
    between=x.loc[(x.index>e)&(x.index<=dec.index[1])]
    assert (between.exposure_start==dec.loc[e,'A3']).all()
    d.VIX=80;d['Mkt-RF']=-.001
    z,_=run_factor(d,cfg);x=z['A3']['daily'];assert np.allclose(x.return_net.iloc[1:],x.RF.iloc[1:])

def test_initial_cost_in_first_holding_month_and_nav():
    idx=pd.bdate_range('2020-01-31','2020-03-31')
    d=pd.DataFrame({'return_net':0.,'RF':0.,'turnover':0.,'cost_fraction':0.},index=idx);d.iloc[0,0]=-.001
    m=monthly(d);assert m.index[0]==pd.Timestamp('2020-02-29');assert m.iloc[0]['return']==pytest.approx(-.001)
    assert (1+m['return']).prod()==pytest.approx((1+d.return_net).prod())

def test_b3_requires_actual_strategy_warmup_and_manual_forecast():
    idx=pd.bdate_range('2017-01-01','2020-12-31')
    p=pd.DataFrame({'SPY':np.exp(np.arange(len(idx))*.0005+np.sin(np.arange(len(idx)))*.03),'IEF':np.exp(np.arange(len(idx))*.0001)},index=idx)
    f=pd.Series(.00002,index=idx)
    cfg={'lookback_months':12,'top_k':2,'volatility_days':126,'risk_cap_annual_volatility':.1,'annual_volatility_floor':.05,'risk_scale_cap':1.}
    targets,_=etf_targets(p,f,cfg);t,size=make_b3(p,f,cfg,targets)
    e=t.index[0];s=size.iloc[0].signal_date
    history=simulate(p.pct_change(fill_method=None),f,targets['B2'],cost_bps=0)['daily'].iloc[1:]
    assert len(history.loc[:s])>=126
    ex=(history.return_net-history.RF).loc[:s].tail(126)
    manual=min(1,.1/max(ex.std(ddof=1)*np.sqrt(252),.05))
    assert size.iloc[0].q==pytest.approx(manual)
    assert np.allclose(t.loc[e].iloc[:-1],targets['B2'].loc[e].iloc[:-1]*manual)
    assert t.loc[e].sum()==pytest.approx(1)
    # A single future price perturbation cannot affect this forecast/target.
    p2=p.copy();p2.loc[p2.index>s]*=1.2
    targets2,_=etf_targets(p2,f,cfg);t2,size2=make_b3(p2,f,cfg,targets2)
    assert np.allclose(t2.loc[e],t.loc[e])
