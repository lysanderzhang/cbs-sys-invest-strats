"""Jurek's static initial option-delta overlay, normalized by initial spot S0."""
from dataclasses import dataclass
import numpy as np
from scipy.special import ndtr


@dataclass(frozen=True)
class Parameters:
    spot:float=100.
    strike:float=97.
    foreign_rate:float=.04
    funding_rate:float=.01
    maturity:float=.25
    volatility:float=.15


def prices(p):
    if not np.isfinite([p.spot,p.strike,p.foreign_rate,p.funding_rate,p.maturity,p.volatility]).all() or min(p.spot,p.maturity,p.volatility)<=0 or p.strike<0:raise ValueError('Invalid option inputs')
    g=np.exp(p.foreign_rate*p.maturity);a=np.exp(p.funding_rate*p.maturity)
    if p.strike==0:return dict(put=0.,call=p.spot/g,delta=0.,g=g,a=a)
    v=p.volatility*np.sqrt(p.maturity);d1=(np.log(p.spot/p.strike)+(p.funding_rate-p.foreign_rate+.5*p.volatility**2)*p.maturity)/v;d2=d1-v
    call=p.spot/g*ndtr(d1)-p.strike/a*ndtr(d2)
    put=p.strike/a*ndtr(-d2)-p.spot/g*ndtr(-d1)
    return dict(put=float(put),call=float(call),delta=float(-ndtr(-d1)/g),g=float(g),a=float(a))


def quantity(g,hedge_delta):
    denominator=1+g*hedge_delta
    if not np.isfinite([g,hedge_delta]).all() or g<=0 or denominator<=0 or hedge_delta>0:raise ValueError('Infeasible put-overlay quantity')
    return g/denominator


def construction(p,hedge_delta=None):
    v=prices(p);d=v['delta'] if hedge_delta is None else hedge_delta;q=quantity(v['g'],d);foreign=1-q*d
    return dict(**v,hedge_delta=d,q=q,foreign_units=foreign,extra_foreign_units=-q*d,
                borrowed_units=foreign*p.spot+q*v['put'],slope=q/p.spot,
                slope_ratio=q/v['g'],lower_bound=-q*v['a']*v['call']/p.spot,
                initial_total_delta=foreign+q*v['delta'])


def returns(p,terminal,hedge_delta=None):
    x=np.asarray(terminal,dtype=float)
    if not np.isfinite(x).all() or (x<0).any():raise ValueError('Invalid terminal exchange rate')
    z=construction(p,hedge_delta);q=z['q'];b=z['foreign_units']
    eq2=z['g']*b*x/p.spot+q*np.maximum(p.strike-x,0)/p.spot-z['a']*(b+q*z['put']/p.spot)
    eq4=q*np.maximum(x-p.strike,0)/p.spot-q*z['a']*z['call']/p.spot
    unhedged=z['g']*x/p.spot-z['a']
    return eq2,eq4,unhedged
