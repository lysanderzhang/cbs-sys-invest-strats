import numpy as np
import pytest
from src.fx import inverse_return,approximate_inverse_moments
from src.doubling import times,rule72_exact_rate
from src.options import Parameters,prices,construction,returns,quantity


def test_reciprocal_not_negative():
    assert inverse_return(.1)==pytest.approx(-1/11)
    assert inverse_return(-.1)==pytest.approx(1/9)
    x=np.array([-.8,-.2,0,.1,2.]);np.testing.assert_allclose(inverse_return(inverse_return(x)),x)

@pytest.mark.parametrize('x',[-1.,-1.01,np.nan,np.inf])
def test_return_domain(x):
    with pytest.raises(ValueError):inverse_return(x)


def test_taylor_error_orders():
    # For symmetric tiny shocks the omitted mean and variance terms begin at order four.
    errors=[]
    for a in [.01,.005]:
        x=np.array([-a,a]);y=inverse_return(x);m,v=approximate_inverse_moments(0,a*a)
        errors.append((abs(y.mean()-m),abs(y.var()-v)))
    ratios=np.array(errors[0])/np.array(errors[1]);assert (ratios>15.9).all() and (ratios<16.1).all()


def test_moments_not_identifying():
    x=np.array([-.1,.1]);y=np.array([-np.sqrt(.02),0,np.sqrt(.02)]);w=np.array([.25,.5,.25])
    assert np.dot(w,y)==pytest.approx(x.mean());assert np.dot(w,y*y)==pytest.approx(x.var())
    assert abs(np.dot(w,inverse_return(y))-inverse_return(x).mean())>1e-5

@pytest.mark.parametrize('r',[.001,.01,.08,.5,1.])
def test_exact_doubling(r):
    t=times(r);assert np.exp(t['exact']*np.log1p(r))==pytest.approx(2)
    assert t['rule72']==pytest.approx(72/(100*r))
    assert t['corrected_log2']>t['exact']>t['linear_log2']

@pytest.mark.parametrize('r',[0,-.01,np.nan,np.inf])
def test_doubling_domain(r):
    with pytest.raises(ValueError):times(r)


def test_rule72_unique_crossing():
    x=rule72_exact_rate();t=times(x);assert .07<x<.09;assert t['rule72']==pytest.approx(t['exact'],abs=1e-12)
    assert times(x*.9)['rule72']>times(x*.9)['exact'];assert times(x*1.1)['rule72']<times(x*1.1)['exact']


def test_option_budget_and_terminal_floor():
    p=Parameters();z=construction(p);x=np.array([0,50,p.strike,100,150]);a,b,u=returns(p,x)
    np.testing.assert_allclose(a,b,atol=2e-15);np.testing.assert_allclose(a[:3],z['lower_bound'],atol=2e-15)
    assert z['initial_total_delta']==pytest.approx(1);assert z['slope_ratio']>1
    assert z['q']==pytest.approx(z['g']*z['foreign_units']);assert z['put']>0


def test_overlay_no_delta_hedge_still_insured():
    p=Parameters();z=construction(p,0);a,_,u=returns(p,[0,50,150],0)
    assert z['foreign_units']==1;assert z['q']==pytest.approx(z['g']);assert a[0]==pytest.approx(a[1]);assert a[0]!=pytest.approx(u[0]);assert z['initial_total_delta']<1


def test_zero_strike_removes_overlay():
    p=Parameters(strike=0);z=construction(p);a,b,u=returns(p,[0,50,100,150]);assert z['delta']==0 and z['put']==0
    np.testing.assert_allclose(a,u,atol=1e-15);np.testing.assert_allclose(b,u,atol=1e-15)


def test_option_parity_and_terminal_slopes():
    p=Parameters();z=construction(p);a,_,u=returns(p,np.array([120.,121.]))
    assert z['call']-z['put']==pytest.approx(p.spot/z['g']-p.strike/z['a'])
    assert (a[1]-a[0])/(u[1]-u[0])==pytest.approx(z['slope_ratio'])

@pytest.mark.parametrize('d',[-2.,.1,np.nan])
def test_infeasible_hedge(d):
    with pytest.raises(ValueError):quantity(1.01,d)
