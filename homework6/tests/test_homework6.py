import math
import numpy as np
import pytest
from src.sharpe import rho_bound, combined_sharpe, emv_sharpe, homogeneous_corr, averages, random_corr, bound_slope_in_n
from src.growth import Asset, exact_g, approx_g, w_star, g_star, sharpe, exact_optimum, simulate_growth, vector_kelly, tangency


def test_closed_form_matches_matrix_sharpe():
    for n, ron, rn in [(1, 0.3, 0.0), (4, -0.2, 0.4), (7, 0.1, -0.1)]:
        sr = np.r_[0.8, np.full(n, 0.5)]
        assert emv_sharpe(sr, homogeneous_corr(n, ron, rn)) == pytest.approx(combined_sharpe(0.8, 0.5, n, ron, rn), abs=1e-14)


@pytest.mark.parametrize('n,rn', [(1, 0.0), (3, 0.2), (10, 0.5)])
def test_bound_is_exact_improvement_threshold(n, rn):
    rng = np.random.default_rng(1)
    for _ in range(200):
        so, sn = rng.uniform(0.1, 1.5, 2); b = float(rho_bound(so, sn, n, rn))
        for rho in (b - 1e-6, b + 1e-6):
            if 1 + n + 2 * n * rho + n * (n - 1) * rn > 0:
                assert (combined_sharpe(so, sn, n, rho, rn) > so) == (rho < b)


def test_n1_landmarks():
    assert rho_bound(0.7, 0.0) == pytest.approx(-0.5)
    assert rho_bound(0.7, 0.7) == pytest.approx(1.0)
    assert rho_bound(1.0, math.sqrt(2) - 1) == pytest.approx(0.0, abs=1e-15)
    s = np.linspace(-3, 3, 6001); assert (s + s ** 2 / 2 - 0.5).min() == pytest.approx(-1.0, abs=1e-6)


def test_n1_stricter_than_marginal_rule_below_one():
    s = np.linspace(0, 1, 101); assert np.all(rho_bound(1.0, s) <= s + 1e-15)


def test_slope_in_n_sign():
    assert np.sign(rho_bound(0.75, 0.5, 6, 0.5) - rho_bound(0.75, 0.5, 5, 0.5)) == np.sign(bound_slope_in_n(0.75, 0.5, 0.5))
    assert bound_slope_in_n(0.75, 0.5, 0.5) < 0 < bound_slope_in_n(0.75, 0.5, 0.2)


def test_averages_are_sufficient_statistics():
    rng = np.random.default_rng(2)
    for _ in range(50):
        n = int(rng.integers(2, 9)); sr = np.r_[0.6, rng.uniform(0, 1, n)]; c = random_corr(n + 1, rng, rng.uniform(0, 3)); a = averages(sr, c)
        assert emv_sharpe(sr, c) == pytest.approx(combined_sharpe(0.6, a['sr_new_bar'], n, a['rho_on_bar'], a['rho_new_bar']), abs=1e-12)


def test_growth_closed_forms():
    a = Asset()
    assert w_star(a) == pytest.approx(a.mu / a.sigma ** 2)
    assert g_star(a) == pytest.approx(0.5 * sharpe(a) ** 2)
    assert approx_g(a, w_star(a)) == pytest.approx(g_star(a), abs=1e-15)
    assert approx_g(a, 2 * w_star(a)) == pytest.approx(0.0, abs=1e-15)
    r = 0.002; ws = w_star(a, r)
    assert approx_g(a, ws, r) == pytest.approx(math.log1p(r) + 0.5 * ((a.mu - r) / a.sigma) ** 2, abs=1e-15)


def test_lognormal_moments_and_exact_optimum():
    a = Asset(); z = np.random.default_rng(3).standard_normal(2_000_000); x = a.returns(z)
    assert x.mean() == pytest.approx(a.mu, abs=2e-4) and x.std() == pytest.approx(a.sigma, rel=2e-3)
    for r in (0.0, 0.002):
        we, ge = exact_optimum(a, r)
        assert abs(we - w_star(a, r)) < 0.02 and abs(ge - g_star(a, r)) < 5e-5 and ge >= exact_g(a, w_star(a, r), r)


def test_growth_variance_shrinks_with_horizon():
    a = Asset(); w = w_star(a)
    s1 = simulate_growth(a, w, 0, 10, 20000, 4).std(); s2 = simulate_growth(a, w, 0, 160, 20000, 4).std()
    assert s2 / s1 == pytest.approx(0.25, rel=0.05)  # sd ~ 1/sqrt(T)


def test_vector_kelly_is_levered_tangency():
    mu = np.array([0.008, 0.005, 0.004]); vol = np.array([0.11, 0.05, 0.03])
    corr = np.array([[1, 0.3, -0.1], [0.3, 1, 0.2], [-0.1, 0.2, 1]]); cov = np.outer(vol, vol) * corr
    x, g = vector_kelly(mu, cov, 0.002); a, sr = tangency(mu, cov, 0.002)
    assert np.allclose(x / x.sum(), a) and g == pytest.approx(0.002 + 0.5 * sr ** 2)
    rng = np.random.default_rng(5)
    for _ in range(2000):
        b = rng.dirichlet(np.ones(3)); assert (b @ (mu - 0.002)) / np.sqrt(b @ cov @ b) <= sr + 1e-12
