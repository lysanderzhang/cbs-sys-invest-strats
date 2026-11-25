"""Separate scalar reconstruction of every exported number; no production finance imports.

Problem 1 bounds are recovered by bisection on the Sharpe comparison itself (not the
closed-form bound). Problem 2 expectations use composite Simpson integration over the
normal density instead of Gauss-Hermite quadrature.
"""
from pathlib import Path
import csv, hashlib, json, math
ROOT = Path(__file__).resolve().parents[1]
CHECKS = []


def close(name, a, b, atol):
    err = abs(a - b); assert err <= atol, (name, a, b, err)
    CHECKS.append(dict(check=name, error=err, tolerance=atol))


def rows(path):
    return list(csv.DictReader((ROOT / 'results' / path).open()))


def sharpe_sum(sr, corr):
    k = len(sr); var = math.fsum(corr[i][j] for i in range(k) for j in range(k))
    return math.fsum(sr) / math.sqrt(var)


def crossing(sr_old, sr_new, n, rho_new):
    """Correlation at which the combined EMV Sharpe ratio equals SR_old, by bisection."""
    def gap(rho):
        var = 1 + n + 2 * n * rho + n * (n - 1) * rho_new
        return (sr_old + n * sr_new) / math.sqrt(var) - sr_old
    lo = -(1 + n + n * (n - 1) * rho_new) / (2 * n) + 1e-13; hi = 1e3  # gap decreasing in rho
    if gap(lo) <= 0: return None
    for _ in range(300):
        mid = 0.5 * (lo + hi); lo, hi = (mid, hi) if gap(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def lognormal(mu, sigma):
    s2 = math.log(1 + sigma ** 2 / (1 + mu) ** 2); return math.log(1 + mu) - 0.5 * s2, math.sqrt(s2)


def simpson_g(mu, sigma, w, r, n=4000, span=12.0):
    m, s = lognormal(mu, sigma); h = 2 * span / n; total = 0.0
    for i in range(n + 1):
        z = -span + i * h; x = math.exp(m + s * z) - 1
        f = math.log1p(r + w * (x - r)) * math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
        total += f * (1 if i in (0, n) else 4 if i % 2 else 2)
    return total * h / 3


def golden_max(f, a, b, tol=1e-11):
    g = (math.sqrt(5) - 1) / 2; c, d = b - g * (b - a), a + g * (b - a)
    while b - a > tol:
        if f(c) > f(d): b, d = d, c; c = b - g * (b - a)
        else: a, c = c, d; d = a + g * (b - a)
    x = 0.5 * (a + b); return x, f(x)


def solve3(a, b):
    """Gaussian elimination with partial pivoting (3x3)."""
    m = [list(map(float, row)) + [float(v)] for row, v in zip(a, b)]; k = len(m)
    for c in range(k):
        p = max(range(c, k), key=lambda i: abs(m[i][c])); m[c], m[p] = m[p], m[c]
        for i in range(c + 1, k):
            f = m[i][c] / m[c][c]; m[i] = [x - f * y for x, y in zip(m[i], m[c])]
    x = [0.0] * k
    for i in reversed(range(k)): x[i] = (m[i][k] - math.fsum(m[i][j] * x[j] for j in range(i + 1, k))) / m[i][i]
    return x


def main():
    CHECKS.clear()
    for rec in rows('tables/bound_n1_grid.csv'):
        a, b = float(rec['sr_old']), float(rec['sr_new'])
        close(f'n=1 bound {a},{b}', crossing(a, b, 1, 0.0), float(rec['bound']), 1e-10)
    for rec in rows('timeseries/bound_n1_curves.csv'):
        x = float(rec['sr_new'])
        for a in [0.25, 0.5, 0.75, 1.0, 1.25]:
            close(f'curve {a},{x}', x / a + 0.5 * (x / a) ** 2 - 0.5, float(rec[f'sr_old_{a:.2f}']), 1e-12)
    for rec in rows('tables/bound_vs_n.csv'):
        n, rn = int(rec['n']), float(rec['rho_new'])
        close(f'bound n={n} rho_new={rn}', crossing(0.75, 0.5, n, rn), float(rec['bound']), 1e-9)
    lm = json.loads((ROOT / 'results/tables/bound_landmarks.json').read_text())
    close('zero crossing', crossing(1.0, math.sqrt(2) - 1, 1, 0.0), 0.0, 1e-10)
    close('zero crossing ratio', lm['zero_crossing_ratio'], math.sqrt(2) - 1, 1e-15)
    close('bound at SR_new=0', crossing(1.0, 0.0, 1, 0.0), lm['bound_at_zero_sr_new'], 1e-10)
    inputs = {d['trial']: d for d in json.loads((ROOT / 'results/tables/heterogeneous_inputs.json').read_text())}
    for rec in rows('tables/heterogeneous_examples.csv'):
        d = inputs[int(rec['trial'])]; sr, c = d['sharpe_ratios'], d['correlation']; n = len(sr) - 1
        ex = sharpe_sum(sr, c); close(f"trial {rec['trial']} exact", ex, float(rec['exact_sharpe']), 1e-12)
        close(f"trial {rec['trial']} closed", ex, float(rec['closed_form_sharpe']), 1e-12)
        srb = math.fsum(sr[1:]) / n; ron = math.fsum(c[0][1:]) / n
        rnew = math.fsum(c[i][j] for i in range(1, n + 1) for j in range(i + 1, n + 1)) / (n * (n - 1) / 2)
        cr = crossing(sr[0], srb, n, rnew)
        close(f"trial {rec['trial']} bound", cr, float(rec['bound']), 1e-9)
        assert (rec['improves'] == 'True') == (ex > sr[0]) == (ron < cr) == (rec['below_bound'] == 'True')
    for rec in rows('tables/growth_comparison.csv'):
        mu, sg, r = float(rec['mu']), float(rec['sigma']), float(rec['rate'])
        ws = (mu - r) * (1 + r) / sg ** 2; sr = (mu - r) / sg
        close(f'w* r={r}', ws, float(rec['w_star_approx']), 1e-14)
        close(f'g* r={r}', math.log1p(r) + 0.5 * sr * sr, float(rec['g_star_approx']), 1e-15)
        close(f'exact g(w*) r={r}', simpson_g(mu, sg, ws, r), float(rec['g_at_w_star_exact']), 1e-11)
        we, ge = golden_max(lambda w: simpson_g(mu, sg, w, r, n=1200), 0.0, 1.0)
        close(f'exact argmax r={r}', we, float(rec['w_star_exact']), 2e-6)
        close(f'exact max r={r}', ge, float(rec['g_max_exact']), 1e-10)
        se = float(rec['mc_standard_error'])
        close(f'MC within 4 s.e. r={r}', float(rec['mc_mean_growth']), float(rec['g_at_w_star_exact']), 4 * se)
    ma = json.loads((ROOT / 'results/tables/multi_asset_example.json').read_text())
    mu, vol, corr, r = ma['mu'], ma['vol'], ma['corr'], ma['rate']
    cov = [[vol[i] * vol[j] * corr[i][j] for j in range(3)] for i in range(3)]
    x = solve3(cov, [m - r for m in mu]); tot = math.fsum(x); a = [v / tot for v in x]
    ex = math.fsum(ai * (m - r) for ai, m in zip(a, mu)); sd = math.sqrt(math.fsum(a[i] * a[j] * cov[i][j] for i in range(3) for j in range(3)))
    for i in range(3):
        close(f'kelly {i}', x[i], ma['kelly_dollar_weights'][i], 1e-12); close(f'tangency {i}', a[i], ma['tangency_weights'][i], 1e-12)
    close('tangency SR', ex / sd, ma['tangency_sharpe'], 1e-13)
    close('g* vector', r + 0.5 * math.fsum((m - r) * xi for m, xi in zip(mu, x)), ma['g_star_vector'], 1e-15)
    close('g* = r + SR^2/2', ma['g_star_vector'], r + 0.5 * (ex / sd) ** 2, 1e-15)
    names = ['results/tables/bound_n1_grid.csv', 'results/timeseries/bound_n1_curves.csv', 'results/tables/bound_vs_n.csv',
             'results/tables/bound_landmarks.json', 'results/tables/heterogeneous_examples.csv',
             'results/tables/heterogeneous_inputs.json', 'results/tables/growth_comparison.csv',
             'results/tables/multi_asset_example.json']
    out = dict(all_checks_passed=True, checks=len(CHECKS), max_error=max(c['error'] for c in CHECKS),
               verified_output_sha256={n: hashlib.sha256((ROOT / n).read_bytes()).hexdigest() for n in names}, details=CHECKS)
    (ROOT / 'results/verification/independent_reconstruction.json').write_text(json.dumps(out, indent=2) + '\n')
    print(f'{len(CHECKS)} independent checks passed')


if __name__ == '__main__':
    main()
