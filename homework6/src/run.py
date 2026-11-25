"""Reproduce every table and figure for Homework 6 (no market data or network needed)."""
from pathlib import Path
import json, os, importlib.metadata
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache/matplotlib'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .sharpe import rho_bound, combined_sharpe, emv_sharpe, averages, random_corr, bound_slope_in_n
from .growth import Asset, exact_g, approx_g, w_star, g_star, sharpe, exact_optimum, simulate_growth, vector_kelly, tangency

SEED = 9339
SR_OLD = [0.25, 0.50, 0.75, 1.00, 1.25]
SR_NEW_GRID = [0.25, 0.50, 0.75, 1.00, 1.25]
RATE = 0.002
PERIODS, PATHS = 120, 20000
BLUE, GREY = '#1d4e79', '0.45'


def save(frame, path, index=False):
    frame.to_csv(ROOT / 'results' / path, index=index, float_format='%.17g')


def dump(obj, path):
    (ROOT / 'results' / path).write_text(json.dumps(obj, indent=2) + '\n')


def figure(fig, name):
    fig.tight_layout(); fig.savefig(ROOT / 'results/figures' / f'{name}.pdf', bbox_inches='tight'); plt.close(fig)


def problem1():
    # 1.4 grid (5 x 5) and plotted curves
    grid = pd.DataFrame([dict(sr_old=a, sr_new=b, s=b / a, bound=float(rho_bound(a, b)),
                              marginal_rule_bound=b / a) for a in SR_OLD for b in SR_NEW_GRID])
    save(grid, 'tables/bound_n1_grid.csv')
    x = np.linspace(0, 1.5, 601)
    curves = pd.DataFrame({'sr_new': x, **{f'sr_old_{a:.2f}': rho_bound(a, x) for a in SR_OLD}})
    save(curves, 'timeseries/bound_n1_curves.csv')
    landmarks = dict(bound_at_zero_sr_new=float(rho_bound(1, 0)), zero_crossing_ratio=float(np.sqrt(2) - 1),
                     unit_bound_ratio=1.0, minimum_bound_over_real_s=-1.0, minimum_at_s=-1.0)
    dump(landmarks, 'tables/bound_landmarks.json')
    # bound versus n (illustration for 1.2)
    rows = []
    for rn in [0.0, 0.2, 0.5]:
        for n in range(1, 21):
            rows.append(dict(sr_old=0.75, sr_new=0.50, rho_new=rn, n=n, bound=float(rho_bound(0.75, 0.50, n, rn)),
                             slope_in_n=float(bound_slope_in_n(0.75, 0.50, rn))))
    save(pd.DataFrame(rows), 'tables/bound_vs_n.csv')
    # 1.5-1.7 heterogeneous inputs: exact EMV Sharpe versus closed form at averages
    rng = np.random.default_rng(SEED); rows = []; inputs = []
    for trial in range(1, 9):
        n = int(rng.integers(2, 7)); hi, (f0, f1) = (0.9, (0.0, 1.0)) if trial % 2 else (0.35, (2.0, 4.0))
        sr = np.concatenate([[0.75], rng.uniform(0.0, hi, n)])  # alternate weak/correlated and strong/diverse designs
        c = random_corr(n + 1, rng, rng.uniform(f0, f1)); av = averages(sr, c)
        exact = emv_sharpe(sr, c); closed = float(combined_sharpe(0.75, av['sr_new_bar'], n, av['rho_on_bar'], av['rho_new_bar']))
        b = float(rho_bound(0.75, av['sr_new_bar'], n, av['rho_new_bar']))
        inputs.append(dict(trial=trial, sharpe_ratios=sr.tolist(), correlation=c.tolist()))
        rows.append(dict(trial=trial, n=n, sr_old=0.75, **av, exact_sharpe=exact, closed_form_sharpe=closed,
                         abs_difference=abs(exact - closed), bound=b, improves=bool(exact > 0.75),
                         below_bound=bool(av['rho_on_bar'] < b), max_individual_rho_on=float(c[0, 1:].max()),
                         sr_new_values=' '.join(f'{v:.17g}' for v in sr[1:])))
    save(pd.DataFrame(rows), 'tables/heterogeneous_examples.csv')
    dump(inputs, 'tables/heterogeneous_inputs.json')

    plt.rcParams.update({'font.family': 'serif', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'pdf.fonttype': 42, 'mathtext.fontset': 'cm'})
    fig, ax = plt.subplots(figsize=(6.4, 3.5))
    shades = ['0.78', '0.6', '0.42', '0.22', BLUE]; styles = [(0, (1, 1.3)), (0, (4, 2)), (0, (6, 2, 1, 2)), '-', '-']
    for a, c, ls in zip(SR_OLD, shades, styles):
        ax.plot(x, rho_bound(a, x), color=c, ls=ls, lw=1.4, label=rf'$SR_{{old}}={a:.2f}$')
        ax.plot([(np.sqrt(2) - 1) * a], [0], 'o', ms=3, color=c); ax.plot([a], [1], 's', ms=3.2, color=c)
    ax.axhspan(1, 1.6, color='0.93', lw=0)
    for y in (1, -1): ax.axhline(y, color='black', lw=0.7)
    ax.axhline(0, color='0.5', lw=0.5)
    ax.text(1.49, 1.45, r'bound $\geq 1$: every $\rho_{old,new}<1$ improves the Sharpe ratio', ha='right', va='center',
            fontsize=8, bbox=dict(facecolor='white', edgecolor='none', pad=1.5))
    ax.set(xlim=(0, 1.5), ylim=(-1.05, 1.6), xlabel=r'$SR_{new}$', ylabel=r'upper bound on $\rho_{old,new}$')
    ax.legend(loc='lower right', frameon=False); ax.grid(color='0.9', lw=0.5)
    figure(fig, 'bound_n1')
    fig, ax = plt.subplots(figsize=(6.4, 2.9)); b = pd.read_csv(ROOT / 'results/tables/bound_vs_n.csv')
    for rn, c, ls in [(0.0, BLUE, '-'), (0.2, '0.35', (0, (4, 2))), (0.5, '0.65', (0, (1, 1.3)))]:
        f = b[b.rho_new == rn]; ax.plot(f.n, f.bound, color=c, ls=ls, marker='o', ms=2.5, lw=1.2, label=rf'$\rho_{{new}}={rn:.1f}$')
    for y in (1, -1): ax.axhline(y, color='black', lw=0.7)
    ax.set(xlabel=r'number of new strategies $n$', ylabel=r'bound on $\rho_{old,new}$', ylim=(-1.1, 2.2), xticks=[1, 5, 10, 15, 20])
    ax.legend(frameon=False, loc='upper left'); ax.grid(color='0.9', lw=0.5)
    figure(fig, 'bound_vs_n')


def problem2():
    asset = Asset(); rows = []
    for r in (0.0, RATE):
        we, ge = exact_optimum(asset, r); ws = w_star(asset, r)
        g = simulate_growth(asset, ws, r, PERIODS, PATHS, SEED)
        rows.append(dict(rate=r, mu=asset.mu, sigma=asset.sigma, sharpe=sharpe(asset, r), w_star_approx=ws,
                         w_star_simple=(asset.mu - r) / asset.sigma ** 2, w_star_exact=we, g_star_approx=g_star(asset, r),
                         g_at_w_star_exact=exact_g(asset, ws, r), g_max_exact=ge, mc_mean_growth=float(g.mean()),
                         mc_standard_error=float(g.std(ddof=1) / np.sqrt(PATHS)), mc_sd_growth=float(g.std(ddof=1)),
                         one_period_log_sd=float(np.sqrt(exact_g2(asset, ws, r))), periods=PERIODS, paths=PATHS))
    save(pd.DataFrame(rows), 'tables/growth_comparison.csv')
    ws_grid = np.linspace(0, 1, 401)
    curves = pd.DataFrame({'w': ws_grid, **{f'{k}_r{r}': [fn(asset, w, r) for w in ws_grid]
                                             for r in (0.0, RATE) for k, fn in [('exact', exact_g), ('approx', approx_g)]}})
    save(curves, 'timeseries/growth_curves.csv')
    # (g) three-asset illustration of separation: tangency then leverage
    mu = np.array([0.008, 0.005, 0.004]); vol = np.array([0.11, 0.05, 0.03])
    corr = np.array([[1, 0.3, -0.1], [0.3, 1, 0.2], [-0.1, 0.2, 1]]); cov = np.outer(vol, vol) * corr
    x, gv = vector_kelly(mu, cov, RATE); a, sr = tangency(mu, cov, RATE)
    dump(dict(mu=mu.tolist(), vol=vol.tolist(), corr=corr.tolist(), rate=RATE, kelly_dollar_weights=x.tolist(),
              kelly_total_risky=float(x.sum()), tangency_weights=a.tolist(), tangency_sharpe=sr,
              g_star_vector=gv, g_star_from_sharpe=float(np.log1p(RATE) + 0.5 * sr ** 2),
              kelly_over_tangency=(x / a).tolist()), 'tables/multi_asset_example.json')
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for r, c in [(0.0, GREY), (RATE, BLUE)]:
        ax.plot(ws_grid, 1e3 * curves[f'exact_r{r}'], color=c, lw=1.5, label=rf'exact $E[\log(1+r+w(R-r))]$, $r={r}$')
        ax.plot(ws_grid, 1e3 * curves[f'approx_r{r}'], color=c, lw=1.0, ls=(0, (4, 2)), label=rf'approximation, $r={r}$')
        ax.plot([w_star(asset, r)], [1e3 * g_star(asset, r)], 'o', color=c, ms=3.5)
    ax.axhline(0, color='black', lw=0.5)
    ax.set(xlabel=r'allocation to the risky asset $w$', ylabel=r'$g(w)$ per period ($\times 10^{-3}$)')
    ax.legend(frameon=False, fontsize=7.5, loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    ax.grid(color='0.9', lw=0.5)
    figure(fig, 'growth')


def exact_g2(asset, w, r):
    """Variance of one-period log growth, by quadrature (used for the LLN illustration)."""
    from .growth import NODES, WEIGHTS
    lg = np.log1p(r + w * (asset.returns(NODES) - r)); p = WEIGHTS / np.sqrt(2 * np.pi)
    return float(p @ lg ** 2 - (p @ lg) ** 2)


def main():
    for d in ['tables', 'timeseries', 'figures', 'verification']: (ROOT / 'results' / d).mkdir(parents=True, exist_ok=True)
    import hashlib
    for x in json.loads((ROOT / 'data/manifest.json').read_text()):
        assert hashlib.sha256((ROOT / x['copy']).read_bytes()).hexdigest() == x['sha256']
    problem1(); problem2()
    deps = {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scipy', 'matplotlib']}
    dump(dict(seed=SEED, packages=deps), 'verification/run_environment.json')
    print('Homework 6 outputs written to results/')


if __name__ == '__main__':
    main()
