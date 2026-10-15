import numpy as np
import pandas as pd
import pytest
from src.data import load_data, usd_spots, CCY,ROOT
from src.carry import currency_returns
from src.portfolio import weight_row, weights, portfolio_returns, ranks
from src.volatility import prior_quantile, signal,realized_audjpy
from src.conditioning import condition,common_period
from src.performance import wealth,drawdown,stats

@pytest.fixture(scope='module')
def d(): return load_data()

def test_quote_direction_and_ror(d):
    x=usd_spots(d)
    np.testing.assert_allclose(x.JPY,1/d.JPY)
    np.testing.assert_allclose(x.AUD,d.AUD)
    assert x.JPY.iloc[1]>x.JPY.iloc[0] # JPY/USD fell: yen appreciated
    assert x.AUD.iloc[1]>x.AUD.iloc[0]
    rr=x.pct_change(fill_method=None)
    for c in CCY:assert (rr[c]-d[c+' ROR']).abs().max()<=.000050001

def test_percentage_calendar_accrual_and_exact_return(d):
    c=currency_returns(d,'1M');dt=3/365
    expected=np.exp(d.iloc[0]['AUD 1M']/100*dt)*(d.iloc[1].AUD/d.iloc[0].AUD)-np.exp(d.iloc[0]['USD 1M']/100*dt)
    assert c['total'].iloc[1].AUD==pytest.approx(expected,abs=1e-15)
    np.testing.assert_allclose(c['total'].iloc[1:],sum(c[k].iloc[1:] for k in ['spot','carry','interaction']),atol=5e-16)

@pytest.mark.parametrize('method',['equal','rank','spread'])
@pytest.mark.parametrize('k',[2,3])
def test_weight_ranking_and_normalization(method,k):
    y=pd.Series(np.arange(9.),index=CCY);w=weight_row(y,k,method)
    assert w[w>0].sum()==pytest.approx(1)
    assert w[w<0].sum()==pytest.approx(-1)
    assert w.sum()==pytest.approx(0)
    assert w.abs().sum()==pytest.approx(2)
    assert set(w[w>0].index)==set(y.nlargest(k).index)
    assert set(w[w<0].index)==set(y.nsmallest(k).index)
    if method=='rank':assert w.loc[y.idxmax()]==pytest.approx(k/(k*(k+1)/2))
    if method=='spread':assert w.loc[y.idxmax()]==pytest.approx(4/np.arange(5-k,5).sum())

def test_ties_and_zero_spread_fallback():
    y=pd.Series(1.,index=CCY)
    w=weight_row(y,3,'spread')
    assert set(w[w>0].index)=={'AUD','CAD','CHF'}
    assert w[w>0].sum()==pytest.approx(1)
    np.testing.assert_allclose(w[w!=0].abs(),1/3)

def test_ranks(d):
    rr=ranks(d,'1M');assert rr.loc[d.index[0],'NOK']==1; assert rr.loc[d.index[0],'JPY']==9
    assert (rr.sum(axis=1)==45).all()

def test_portfolio_self_financing_and_alignment(d):
    w=weights(d,'1M',2,'equal');c=currency_returns(d,'1M');p=portfolio_returns(w,c)['total']
    assert p.index.equals(d.index[1:])
    i=250
    expected=(w.iloc[i-1]*c['total'].iloc[i]).sum()
    assert p.loc[d.index[i]]==pytest.approx(expected,abs=1e-15)
    # USD term cancels because signed initial USD notionals sum to zero.
    usd=np.exp(d['USD 1M'].shift(1)/100*d.index.to_series().diff().dt.days/365)
    a=(w.shift(1)*c['total'].add(usd,axis=0)).sum(axis=1,min_count=9).iloc[1:]
    np.testing.assert_allclose(a,p,atol=1e-15)

def test_no_future_weights_or_returns(d):
    part=d.iloc[:100].copy();changed=part.copy();changed.loc[changed.index[-1],['AUD 1M','NZD 1M']]=100
    a=portfolio_returns(weights(part,'1M',2,'rank'),currency_returns(part))['total']
    b=portfolio_returns(weights(changed,'1M',2,'rank'),currency_returns(changed))['total']
    np.testing.assert_allclose(a,b,atol=1e-15)

def test_prior_percentile_and_lookahead():
    s=pd.Series(np.arange(300.),index=pd.date_range('2000-01-01',periods=300))
    th=prior_quantile(s)
    assert th.iloc[:252].isna().all()
    assert th.iloc[252]==pytest.approx(np.quantile(np.arange(252.),.75))
    altered=s.copy();altered.iloc[252:]=10000
    pd.testing.assert_series_equal(th.iloc[:253],prior_quantile(altered).iloc[:253])
    eq=pd.Series(1.,index=s.index);z,_,_=signal(eq)
    assert z.iloc[252]==1 # equality is risk-on

def test_exposure_lag_missing_and_common_period():
    ix=pd.date_range('2000-01-01',periods=300)
    s=pd.Series(10.,index=ix);s.iloc[0]=np.nan;s.iloc[280]=100;s.iloc[281]=np.nan
    r=pd.Series(.01,index=ix);cr,ex,th,filled=condition(r,s)
    assert np.isnan(filled.iloc[0])
    assert filled.iloc[281]==100
    assert ex.iloc[280]==1 and ex.iloc[281]==0 and cr.iloc[281]==0
    assert th.first_valid_index()==ix[253]
    common=common_period(pd.DataFrame({'base':r,'cond':cr}))
    assert common.index.equals(cr.dropna().index)
    assert common.iloc[0].name==ix[254]

def test_realized_cross_and_volatility(d):
    rv=realized_audjpy(d)
    cross=d.AUD*d.JPY
    ret=np.array([cross.iloc[i]/cross.iloc[i-1]-1 for i in range(1,22)])
    assert rv.iloc[:21].isna().all()
    assert rv.iloc[21]==pytest.approx(np.std(ret,ddof=1)*np.sqrt(252),abs=1e-14)
    part=d.iloc[:100].copy();part.loc[part.index[-1],'AUD']*=2
    np.testing.assert_allclose(realized_audjpy(part).iloc[:99],rv.iloc[:99],equal_nan=True)

def test_compound_drawdown_and_stats():
    r=pd.Series([-.1,.2,-.25])
    np.testing.assert_allclose(wealth(r),[.9,1.08,.81])
    np.testing.assert_allclose(drawdown(r),[-.1,0,-.25])
    st=stats(r);assert st.max_drawdown==pytest.approx(.25)
    assert st.terminal_wealth==pytest.approx(.81)
    assert st.geometric==pytest.approx(.81**(252/3)-1)
    assert st.es05==pytest.approx(.25)

@pytest.mark.parametrize('name',['conditioned_returns_common.csv','historical_comparison_returns.csv'])
def test_export_fair_periods(name):
    f=pd.read_csv(ROOT/'results/timeseries'/name,index_col=0)
    assert f.notna().all().all()
    assert f.index.is_unique

def test_all_exported_weights():
    w=pd.read_csv(ROOT/'results/timeseries/daily_weights.csv')
    sums=w.groupby(['strategy','return_date']).weight.agg(['sum',lambda s:s.abs().sum()])
    np.testing.assert_allclose(sums['sum'],0,atol=1e-11)
    np.testing.assert_allclose(sums.iloc[:,1],2,atol=1e-11)
    assert (pd.to_datetime(w.return_date)>pd.to_datetime(w.decision_date)).all()

def test_independent_scalar_checks():
    a=pd.read_csv(ROOT/'results/validation/independent_return_checks.csv')
    assert len(a)==60
    assert a.error.abs().max()<1e-14
    assert a.usd_cancel_error.abs().max()<1e-14

def test_input_hashes_unchanged():
    import json,hashlib
    for row in json.loads((ROOT/'data/manifest.json').read_text()):
        assert hashlib.sha256((ROOT/row['copy']).read_bytes()).hexdigest()==row['sha256']

@pytest.mark.parametrize('column',['AUD 1M','AUD'])
def test_infinite_input_rejected_even_when_vix_missing(tmp_path,column):
    raw=pd.read_csv(ROOT/'data/raw/hw3.data.carry.FX.dly.csv')
    raw.loc[0,column]=np.inf  # first row also has missing VIX
    path=tmp_path/'invalid.csv';raw.to_csv(path,index=False)
    with pytest.raises(ValueError,match='Infinite'):load_data(path)

@pytest.mark.parametrize('values',[[0.01,np.inf],[0.01,-1.0]])
def test_statistics_stop_on_nonfinite_or_bankrupt_returns(values):
    with pytest.raises(ValueError):stats(pd.Series(values))

def test_integrated_future_mutation_cannot_change_earlier_returns(d):
    original=d.iloc[:600].copy();altered=original.copy();cut=500;date=original.index[cut]
    columns=[c+' 3M' for c in CCY]
    altered.loc[date:,columns]+=50
    altered.loc[date:,'AY3M']+=100
    altered.loc[original.index[cut+1]:,CCY]*=1.1
    def run(frame):
        base=portfolio_returns(weights(frame,'3M',3,'equal'),currency_returns(frame,'3M'))['total']
        return base,condition(base,frame.AY3M)[0],realized_audjpy(frame)
    a=run(original);b=run(altered)
    for x,y in zip(a,b):pd.testing.assert_series_equal(x.loc[:date],y.loc[:date])
