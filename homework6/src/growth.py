"""Problem 2: growth rate of capital, its mean-variance approximation and the Sharpe ratio.

Illustrative risky asset: gross return 1+R = exp(Y), Y ~ N(m, s^2), with (m, s) chosen so
that E[R] = MU and sd(R) = SIGMA. The lognormal keeps 1 + r + w(R - r) > 0 for 0 <= w <= 1.
"""
from dataclasses import dataclass
import numpy as np
from scipy.optimize import minimize_scalar

NODES, WEIGHTS = np.polynomial.hermite_e.hermegauss(80)  # probabilists' Hermite: N(0,1)


@dataclass(frozen=True)
class Asset:
    mu: float = 0.008      # mean per period
    sigma: float = 0.11    # volatility per period

    @property
    def s2(self):
        return float(np.log(1 + self.sigma ** 2 / (1 + self.mu) ** 2))

    @property
    def m(self):
        return float(np.log(1 + self.mu) - 0.5 * self.s2)

    def returns(self, z):
        return np.exp(self.m + np.sqrt(self.s2) * z) - 1


def exact_g(asset, w, r=0.0):
    """E[log(1 + r + w(R - r))] by 80-point Gauss-Hermite quadrature."""
    x = asset.returns(NODES)
    return float(WEIGHTS @ np.log1p(r + w * (x - r)) / np.sqrt(2 * np.pi))


def approx_g(asset, w, r=0.0):
    """log(1+r) + w*mt - w^2 st^2/2, mt=(mu-r)/(1+r), st=sigma/(1+r)."""
    mt, st = (asset.mu - r) / (1 + r), asset.sigma / (1 + r)
    return float(np.log1p(r) + w * mt - 0.5 * w ** 2 * st ** 2)


def w_star(asset, r=0.0):
    return (asset.mu - r) * (1 + r) / asset.sigma ** 2


def sharpe(asset, r=0.0):
    return (asset.mu - r) / asset.sigma


def g_star(asset, r=0.0):
    return float(np.log1p(r) + 0.5 * sharpe(asset, r) ** 2)


def exact_optimum(asset, r=0.0):
    res = minimize_scalar(lambda w: -exact_g(asset, w, r), bounds=(0.0, 1.0), method='bounded',
                          options=dict(xatol=1e-12))
    return float(res.x), float(-res.fun)


def simulate_growth(asset, w, r, periods, paths, seed):
    """Realized g = (1/T) sum log(1 + r + w(R_t - r)) on independent simulated paths."""
    rng = np.random.default_rng(seed)
    x = asset.returns(rng.standard_normal((paths, periods)))
    return np.log1p(r + w * (x - r)).sum(axis=1) / periods


def vector_kelly(mu, cov, r=0.0):
    """Approximate g = r + x'(mu - r1) - x'Cov x/2: optimum x* = Cov^{-1}(mu - r1), g* = r + SR_tan^2/2."""
    ex = np.asarray(mu, float) - r
    x = np.linalg.solve(cov, ex)
    return x, float(r + 0.5 * ex @ x)


def tangency(mu, cov, r=0.0):
    """Maximum-Sharpe fully invested risky portfolio and its Sharpe ratio."""
    ex = np.asarray(mu, float) - r
    y = np.linalg.solve(cov, ex); a = y / y.sum()
    return a, float(a @ ex / np.sqrt(a @ cov @ a))
