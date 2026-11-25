"""Problem 1: Sharpe-ratio enhancement under equal-marginal-volatility (EMV) weights.

Every component (the existing portfolio and each new strategy) is scaled to unit
stand-alone volatility, so a component's expected return equals its Sharpe ratio and
the combined variance is the sum of all entries of the correlation matrix.
"""
import numpy as np


def emv_sharpe(sr, corr):
    """Sharpe ratio of the sum of unit-volatility components: 1'SR / sqrt(1'C1)."""
    sr = np.asarray(sr, float); corr = np.asarray(corr, float); one = np.ones(len(sr))
    return float(one @ sr / np.sqrt(one @ corr @ one))


def combined_sharpe(sr_old, sr_new, n, rho_on, rho_new):
    """Closed form for one old portfolio plus n new strategies (homogeneous parameters)."""
    var = 1 + n + 2 * n * rho_on + n * (n - 1) * rho_new
    return (sr_old + n * sr_new) / np.sqrt(var)


def homogeneous_corr(n, rho_on, rho_new):
    """(n+1)x(n+1) correlation matrix: index 0 is the existing portfolio."""
    c = np.full((n + 1, n + 1), float(rho_new)); c[0, :] = c[:, 0] = rho_on; np.fill_diagonal(c, 1.0)
    return c


def rho_bound(sr_old, sr_new, n=1, rho_new=0.0):
    """Upper bound on rho_old,new: s + (n/2) s^2 - (1 + (n-1) rho_new)/2, s = SR_new/SR_old.

    Requires SR_old > 0 and SR_old + n SR_new > 0 (otherwise no correlation improves)."""
    s = np.asarray(sr_new, float) / sr_old
    return s + 0.5 * n * s ** 2 - 0.5 * (1 + (n - 1) * np.asarray(rho_new, float))


def bound_slope_in_n(sr_old, sr_new, rho_new):
    """d bound / d n = (s^2 - rho_new)/2."""
    return 0.5 * ((sr_new / sr_old) ** 2 - rho_new)


def averages(sr, corr):
    """Simple averages used in answers 1.5-1.7 (index 0 is the existing portfolio)."""
    corr = np.asarray(corr, float); n = len(sr) - 1
    return dict(sr_new_bar=float(np.mean(sr[1:])), rho_on_bar=float(np.mean(corr[0, 1:])),
                rho_new_bar=float(np.mean(corr[1:, 1:][np.triu_indices(n, 1)])) if n > 1 else 0.0)


def random_corr(k, rng, factor):
    """Random valid correlation matrix with a common factor of given strength."""
    a = rng.normal(size=(k, k + 3)) + factor * rng.uniform(0.5, 1.5, size=(k, 1)) * rng.normal(size=(1, k + 3))
    c = a @ a.T; d = np.sqrt(np.diag(c))
    return c / np.outer(d, d)
