"""Write report/main.tex with every quoted number bound to an exported result."""
from pathlib import Path
import json
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CLAIMS = []


def bind(label, path, column, selector=None, scale=1.0, digits=5):
    if path.endswith('.csv'):
        rows = pd.read_csv(ROOT / path)
        for k, v in (selector or {}).items(): rows = rows[rows[k].astype(str) == str(v)]
        assert len(rows) == 1, (label, len(rows)); value = float(rows.iloc[0][column])
    else:
        value = json.loads((ROOT / path).read_text())
        for k in column.split('.'): value = value[k]
        value = float(value)
    CLAIMS.append(dict(label=label, path=path, column=column, selector=selector, scale=scale, digits=digits,
                       formatted=f'{value * scale:.{digits}f}'))


def f5(x):
    return f'{x:.5f}'.replace('-', '$-$')


def tables():
    g = pd.read_csv(ROOT / 'results/tables/bound_n1_grid.csv')
    grid = '\n'.join(f'{a:.2f} & ' + ' & '.join(f5(v) for v in g[g.sr_old == a].sort_values('sr_new').bound) + r' \\'
                     for a in sorted(g.sr_old.unique()))
    h = pd.read_csv(ROOT / 'results/tables/heterogeneous_examples.csv')
    het = '\n'.join(f"{int(r.trial)} & {int(r.n)} & {f5(r.sr_new_bar)} & {f5(r.rho_new_bar)} & {f5(r.rho_on_bar)} & "
                    f"{f5(r.bound)} & {f5(r.exact_sharpe)} & {f5(r.closed_form_sharpe)} & {'yes' if r.improves else 'no'}" + r' \\'
                    for r in h.itertuples())
    p = pd.read_csv(ROOT / 'results/tables/growth_comparison.csv')
    gro = '\n'.join(f"${r.rate:g}$ & {f5(r.sharpe)} & {f5(r.w_star_approx)} & {f5(r.w_star_exact)} & {f5(r.g_star_approx)} & "
                    f"{f5(r.g_at_w_star_exact)} & {f5(r.g_max_exact)} & {f5(r.mc_mean_growth)} ({f5(r.mc_standard_error)})" + r' \\'
                    for r in p.itertuples())
    return grid, het, gro


BODY = r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=0.82in]{geometry}
\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage{amsmath,amssymb,booktabs,array,graphicx,float,microtype}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\pagestyle{plain}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{2em}\setlength{\intextsep}{8pt}
\newcommand{\SRo}{SR_{\mathrm{old}}}
\newcommand{\SRn}{SR_{\mathrm{new}}}
\newcommand{\RhoOn}{\rho_{\mathrm{old,new}}}
\newcommand{\RhoNew}{\rho_{\mathrm{new}}}
% BINDINGS
\begin{document}
\begin{center}{\Large\bfseries FINCB9339 Systematic Investment Strategies\\[3pt]
Homework 6: Sharpe Ratio Enhancement and Growth-Optimal Allocation}\\[8pt]
Hanyu Zhang (hz3069)\end{center}
\section*{Summary of answers}
Notation: $s=\SRn/\SRo$, $\SRo>0$; components scaled to unit volatility.

\textbf{1.1} Hold notional $N_j=k/\hat\sigma_j$ in each component $j=0,\dots,n$ (old portfolio $=$ one component); each then has volatility $k$. Rebalance as $\hat\sigma_j$ changes.

\textbf{1.2} $SR_{p}=\dfrac{\SRo+n\SRn}{\sqrt{1+n+2n\RhoOn+n(n-1)\RhoNew}}>\SRo
\iff \boxed{\RhoOn<s+\tfrac n2 s^2-\tfrac12\big(1+(n-1)\RhoNew\big)}$.

\textbf{1.3} $n=1$: $\RhoOn<s+\tfrac12s^2-\tfrac12=\tfrac12\big[(1+s)^2-2\big]$.

\textbf{1.4} Figure~\ref{fig:n1}, Table~\ref{tab:n1}. Bound $=-0.5$ at $\SRn=0$, $=0$ at $\SRn=\rZeroCross\,\SRo$, $=1$ at $\SRn=\SRo$. Increasing in $\SRn$, decreasing in $\SRo$.

\textbf{1.5--1.7} No added complexity under (e): $SR_p$ depends only on $\sum_iSR_i$, $\sum_i\rho_{0i}$, $\sum_{i<j}\rho_{ij}$, so the 1.2 bound holds exactly with the simple averages $\overline{SR}_{\mathrm{new}},\bar\rho_{\mathrm{old,new}},\bar\rho_{\mathrm{new}}$.

\textbf{1.8} Return per unit of expected shortfall, $\mu/\mathrm{ES}_\alpha$; tail co-movement (``tail beta'') replaces $\RhoOn$.

\textbf{2(a)} $g(w)=\frac1T\sum_t\log(1+wR_t)\approx E[\log(1+wR)]$.\quad
\textbf{2(b)} $g(w)\approx w\mu-\frac12w^2\sigma^2$.\quad
\textbf{2(c)} $w^*=\mu/\sigma^2$.\quad
\textbf{2(d)} $g^*=\frac12(\mu/\sigma)^2=\frac12SR^2$ (half the squared Sharpe ratio).

\textbf{2(e)} $w^*=\frac{(\mu-r)(1+r)}{\sigma^2}\approx\frac{\mu-r}{\sigma^2}$,\; $g^*=\log(1+r)+\frac12\big(\frac{\mu-r}{\sigma}\big)^2\approx r+\frac12SR^2$.

\textbf{2(f)} In (a): time average $\to$ expectation (LLN, $\operatorname{Var}[g]=\operatorname{Var}[\log(1+wR)]/T$); also justifies a constant $w$.

\textbf{2(g)} For risky mix $a$: $\max_wg=\log(1+r)+\frac12SR_p(a)^2$ $\Rightarrow$ maximize $SR_p(a)$ (tangency), then lever by $w^*$.
\clearpage

\section{Sharpe ratio enhancement}
Old portfolio $P_0$: mean $\mu_0$, volatility $\sigma_0$, $\SRo=\mu_0/\sigma_0>0$. New strategies $X_i$: $\mu_i/\sigma_i=\SRn$, $i=1,\dots,n$. $\rho_{0i}=\operatorname{Corr}(P_0,X_i)$, $\rho_{ij}=\operatorname{Corr}(X_i,X_j)$; by (b)--(c), $\rho_{ij}=\RhoNew$, $\rho_{0i}=\RhoOn$.

\subsection*{Equal marginal volatility: answer 1.1}
Estimate $\hat\sigma_j$ (e.g.\ rolling/EWMA realized volatility) and hold
\[
N_j=\frac{k}{\hat\sigma_j},\qquad Y_j=N_jR_j,\qquad \operatorname{Var}(Y_j)=k^2,\qquad E[Y_j]=k\,SR_j .
\]
With $k=1$ every component has unit volatility. $k$ sets total risk and does not affect the Sharpe ratio. Rebalance periodically; leverage or cash absorbs the difference.

\subsection*{Bound on the old/new correlation: answer 1.2}
Combined portfolio $Z=\sum_{j=0}^nY_j$:
\begin{align}
E[Z]&=\SRo+n\SRn,\\
\operatorname{Var}(Z)&=\sum_{j,k}\operatorname{Corr}(Y_j,Y_k)=(n+1)+2n\RhoOn+n(n-1)\RhoNew,\\
SR_p&=\frac{\SRo+n\SRn}{\sqrt{1+n+2n\RhoOn+n(n-1)\RhoNew}} .\label{eq:sr}
\end{align}
Improvement: $SR_p>\SRo$. If $\SRo+n\SRn\le0$, impossible. Otherwise square both sides:
\begin{align*}
(\SRo+n\SRn)^2&>\SRo^2\big[1+n+2n\RhoOn+n(n-1)\RhoNew\big]\\
2n\RhoOn&<(1+ns)^2-(1+n)-n(n-1)\RhoNew=2ns+n^2s^2-n-n(n-1)\RhoNew,
\end{align*}
\begin{equation}
\boxed{\RhoOn<\frac{\SRn}{\SRo}+\frac n2\Big(\frac{\SRn}{\SRo}\Big)^2-\frac{1+(n-1)\RhoNew}{2}\equiv B.}\label{eq:B}
\end{equation}
Admissible region: $\RhoOn\in[-1,1]$ and a positive semi-definite correlation matrix. $B\ge1$ means any $\RhoOn$ works.

Comparative statics:
\[
\frac{\partial B}{\partial\SRn}=\frac{1+ns}{\SRo}>0,\quad
\frac{\partial B}{\partial\SRo}=-\frac{s(1+ns)}{\SRo}<0,\quad
\frac{\partial B}{\partial\RhoNew}=-\frac{n-1}2,\quad
\frac{\partial B}{\partial n}=\frac{s^2-\RhoNew}{2}.
\]
More strategies loosen the bound iff $s^2>\RhoNew$ (Figure~\ref{fig:n}).

\begin{figure}[H]\centering\includegraphics[width=0.78\linewidth]{../results/figures/bound_vs_n.pdf}
\caption{$B$ versus $n$ for $\SRo=0.75$, $\SRn=0.50$ ($s^2=0.444$).}\label{fig:n}\end{figure}

\subsection*{One new strategy: answer 1.3}
$n=1$ in \eqref{eq:B}:
\[
\RhoOn<s+\tfrac12s^2-\tfrac12=\tfrac12\big[(1+s)^2-2\big].
\]
Directly: $SR_p=(\SRo+\SRn)/\sqrt{2+2\rho}>\SRo\iff(1+s)^2>2(1+\rho)$.
Compare the marginal (optimally small position) rule $\rho<s$: $s+\frac12s^2-\frac12=s-\frac12(1-s^2)\le s$ for $s\le1$, so EMV is stricter.

\subsection*{Plot for $n=1$: answer 1.4}
\begin{figure}[H]\centering\includegraphics[width=0.82\linewidth]{../results/figures/bound_n1.pdf}
\caption{$B(n=1)$ versus $\SRn$. Circles: $B=0$ at $\SRn=(\sqrt2-1)\SRo$. Squares: $B=1$ at $\SRn=\SRo$.}\label{fig:n1}\end{figure}
\begin{table}[H]\centering\small\caption{$B$ for $n=1$.}\label{tab:n1}
\begin{tabular}{lrrrrr}\toprule
 & \multicolumn{5}{c}{$\SRn$}\\\cmidrule(l){2-6}
$\SRo$ & 0.25 & 0.50 & 0.75 & 1.00 & 1.25\\\midrule
% GRID
\bottomrule\end{tabular}\end{table}
Interpretation:
\begin{itemize}\setlength{\itemsep}{1pt}
\item $B$ depends on $s$ only; higher $\SRn$ tolerates more correlation, higher $\SRo$ is harder to improve.
\item $s=1$: $SR_p=\SRo\sqrt{2/(1+\rho)}>\SRo$ for all $\rho<1$ (pure diversification). $s>1$: $B>1$.
\item $s=0$: $SR_p=\SRo/\sqrt{2(1+\rho)}>\SRo\iff\rho<-\frac12$ (hedge only).
\item $\min_s(s+\frac12s^2-\frac12)=-1$ at $s=-1$, so $B\ge-\frac12$ for $\SRn\ge0$: a strong enough hedge always helps.
\item Counter-intuitive: for $\rho=0$ improvement needs $s>\sqrt2-1=\rZeroCross$, although with optimal sizing $SR^*=\sqrt{\SRo^2+\SRn^2}>\SRo$ for any $\SRn>0$. The cost comes from EMV over-allocating to a weak strategy.
\end{itemize}

\subsection*{Unequal Sharpe ratios: answer 1.5}
Only the numerator of \eqref{eq:sr} changes:
\[
E[Z]=\SRo+\sum_{i=1}^nSR_i=\SRo+n\,\overline{SR}_{\mathrm{new}},\qquad \overline{SR}_{\mathrm{new}}=\tfrac1n\textstyle\sum_iSR_i .
\]
\eqref{eq:B} holds exactly with $\SRn\to\overline{SR}_{\mathrm{new}}$. Not more complicated. Caveats: the test is for the whole package (individual members may hurt; best subset is a $2^n$ search), and dispersion matters only if weights depend on $SR_i$.

\subsection*{Heterogeneous old/new correlations: answer 1.6}
The old/new block of $\operatorname{Var}(Z)$ is $2\sum_i\rho_{0i}=2n\bar\rho_{\mathrm{old,new}}$. Hence \eqref{eq:B} bounds the simple average, a single half-space:
\[
\textstyle\sum_{i=1}^n\rho_{0i}<nB .
\]
Individual $\rho_{0i}$ may exceed $B$. With non-EMV weights the relevant average would be weight-adjusted.

\subsection*{Heterogeneous new/new correlations: answer 1.7}
$\sum_{i\ne j}\rho_{ij}=n(n-1)\bar\rho_{\mathrm{new}}$, so \eqref{eq:B} holds with $\bar\rho_{\mathrm{new}}$. All three relaxations together:
\[
\sum_i\rho_{0i}<\frac12\left[\frac{(\SRo+\sum_iSR_i)^2}{\SRo^2}-(n+1)-2\sum_{i<j}\rho_{ij}\right].
\]
Only extra constraint: the full matrix must be positive semi-definite. Table~\ref{tab:het}: random heterogeneous inputs ($\SRo=0.75$); $SR_p$ from $\mathbf1'SR/\sqrt{\mathbf1'C\mathbf1}$ equals \eqref{eq:sr} at the averages (max difference \rHetMaxDiff{}), and ``improves'' $\iff\bar\rho_{\mathrm{old,new}}<B$.

If weights were optimized instead, the full $\mu,\Sigma$ matter: $SR^{*2}=\SRo^2+\alpha'\Sigma_\varepsilon^{-1}\alpha$ ($\alpha,\Sigma_\varepsilon$ from regressing new strategies on the old portfolio).

\begin{table}[H]\centering\small\setlength{\tabcolsep}{4.5pt}\caption{Heterogeneous Sharpe ratios and correlations, EMV weights.}\label{tab:het}
\begin{tabular}{rrrrrrrrc}\toprule
Trial & $n$ & $\overline{SR}_{\mathrm{new}}$ & $\bar\rho_{\mathrm{new}}$ & $\bar\rho_{\mathrm{old,new}}$ & $B$ & $SR_p$ (matrix) & $SR_p$ (eq.~\ref{eq:sr}) & Improves\\\midrule
% HET
\bottomrule\end{tabular}\end{table}

\subsection*{Alternative criterion: answer 1.8}
Criterion: $\mathcal R(Z)=E[Z]/\mathrm{ES}_\alpha(Z)$, $\mathrm{ES}_\alpha(Z)=-E[Z\mid Z\le q_\alpha(Z)]$ (e.g.\ $\alpha=5\%$).

Rationale: volatility penalizes upside and downside equally and uses linear correlation. Strategies with negative skew (momentum crashes, carry, short volatility) and correlations that rise in crises are understated by Sharpe. ES measures the left tail and is sub-additive; for elliptical returns $\mathrm{ES}\propto\sigma$ and $\mathcal R$ reduces to Sharpe.

Approach:
\begin{enumerate}\setlength{\itemsep}{1pt}
\item Joint scenarios for $(P_0,X_1,\dots,X_n)$: block bootstrap, or a fat-tailed model (multivariate-$t$, copula, regime switching).
\item Form the EMV portfolio; map $\{\mathcal R(Z)>\mathcal R(P_0)\}$ over the parameter grid as in 1.4.
\item Euler decomposition $\mathrm{ES}_\alpha(Z)=\sum_j-E[Y_j\mid Z\le q_\alpha(Z)]$. Marginal condition: $\mu_{\mathrm{new}}/\big(-E[X\mid P_0\le q_\alpha(P_0)]\big)>\mathcal R(P_0)$, the analogue of $\SRn>\rho\SRo$ with a tail beta in place of $\rho$.
\end{enumerate}

\section{Sharpe ratio and optimal capital allocation}
Risky return $R_t$: $E[R_t]=\mu$, $\operatorname{sd}(R_t)=\sigma$, independent across $t$; constant fraction $w$; $1+wR_t>0$.

\subsection*{Growth rate as an expectation: answer 2(a)}
\[
W_T=W_0\prod_{t=1}^T(1+wR_t)=W_0e^{g(w)T}\ \Rightarrow\ g(w)=\frac1T\sum_{t=1}^T\log(1+wR_t).
\]
i.i.d.\ terms: $E[g(w)]=E[\log(1+wR)]$, $\operatorname{Var}[g(w)]=\operatorname{Var}[\log(1+wR)]/T\to0$. Hence
\[
g(w)\approx E[\log(1+wR)] .
\]

\subsection*{Mean--variance approximation: answer 2(b)}
Second-order expansion $\log(1+x)\approx x-\frac12x^2$ (the mean--variance approximation in Daniel and Moskowitz):
\[
g(w)\approx E\big[wR-\tfrac12w^2R^2\big]=w\mu-\tfrac12w^2(\sigma^2+\mu^2)\approx w\mu-\tfrac12w^2\sigma^2,
\]
using $\mu^2\ll\sigma^2$ per period (e.g.\ $\mu=1\%$, $\sigma=5\%$: $\mu^2/\sigma^2=0.04$).

\subsection*{Optimal allocation: answer 2(c)}
\[
g'(w)=\mu-w\sigma^2=0\ \Rightarrow\ \boxed{w^*=\frac{\mu}{\sigma^2}=\frac{SR}{\sigma}},\qquad g''(w)=-\sigma^2<0 .
\]
(Keeping $\mu^2$: $w^*=\mu/(\sigma^2+\mu^2)$.) Same $\mu/\sigma^2$ form as the Daniel--Moskowitz dynamic weight. Note $g(2w^*)\approx0$.

\subsection*{Optimal growth rate: answer 2(d)}
\[
g^*=\frac{\mu}{\sigma^2}\mu-\frac12\frac{\mu^2}{\sigma^4}\sigma^2=\boxed{\frac12\Big(\frac{\mu}{\sigma}\Big)^2=\frac12SR^2}
\]
Half the squared Sharpe ratio: the Kelly growth rate. The maximal growth rate is a function of the Sharpe ratio only.

\subsection*{Cash earning $r$: answer 2(e)}
Per-period gross return $(1-w)(1+r)+w(1+R)=1+r+w(R-r)$.
\begin{itemize}\setlength{\itemsep}{1pt}
\item[(a$'$)] $g(w)\approx E[\log(1+r+w(R-r))]$.
\item[(b$'$)] $\log(1+r+w(R-r))=\log(1+r)+\log(1+w\tilde X)$ with $\tilde X=\frac{R-r}{1+r}$, $\tilde\mu=\frac{\mu-r}{1+r}$, $\tilde\sigma=\frac{\sigma}{1+r}$; applying (b),
\[g(w)\approx\log(1+r)+w\tilde\mu-\tfrac12w^2\tilde\sigma^2 .\]
\item[(c$'$)] $w^*=\dfrac{\tilde\mu}{\tilde\sigma^2}=\dfrac{(\mu-r)(1+r)}{\sigma^2}\approx\dfrac{\mu-r}{\sigma^2}$.
\item[(d$'$)] $g^*=\log(1+r)+\dfrac{\tilde\mu^2}{2\tilde\sigma^2}=\log(1+r)+\dfrac12\Big(\dfrac{\mu-r}{\sigma}\Big)^2\approx r+\dfrac12SR^2$, $SR=\dfrac{\mu-r}{\sigma}$.
\end{itemize}
The $(1+r)$ factors cancel in $\tilde\mu/\tilde\sigma$.

Numerical example (Table~\ref{tab:growth}, Figure~\ref{fig:growth}): $\mu=\rMu$, $\sigma=\rSigma$ per period, lognormal $1+R$. Exact $E[\log(\cdot)]$ by 80-point Gauss--Hermite quadrature; simulation: $T=\rPeriods$, \rPaths{} paths at $w^*$ (s.e.\ in parentheses).

\begin{table}[H]\centering\small\setlength{\tabcolsep}{4.5pt}\caption{Approximate versus exact optimum (per period).}\label{tab:growth}
\begin{tabular}{lrrrrrrr}\toprule
$r$ & $SR$ & $w^*$ approx. & $w^*$ exact & $g^*$ approx. & $g(w^*)$ exact & $\max_wg$ exact & Simulated $g$\\\midrule
% GROWTH
\bottomrule\end{tabular}\end{table}
\begin{figure}[H]\centering\includegraphics[width=0.8\linewidth]{../results/figures/growth.pdf}
\caption{Exact (solid) and approximate (dashed) $g(w)$; dots at $(w^*,g^*)$.}\label{fig:growth}\end{figure}
The exact optimum is slightly above $w^*$: the positive skew of the lognormal (third moment, dropped in (b)) rewards a slightly larger position.

\subsection*{Use of independence: answer 2(f)}
\begin{itemize}\setlength{\itemsep}{1pt}
\item In (a): replacing $\frac1T\sum_t\log(1+wR_t)$ by $E[\log(1+wR)]$. Identical distribution gives the mean; independence gives $\operatorname{Var}[g]=\operatorname{Var}[\log(1+wR)]/T\to0$ (LLN), so maximizing the expectation maximizes realized growth. Under dependence, autocovariance terms enter and convergence can fail.
\item Constant $w$: with i.i.d.\ returns nothing learned changes the next-period distribution. With predictable $\mu_t,\sigma_t$ the optimum is $w_t^*=\mu_t/\sigma_t^2$, the Daniel--Moskowitz dynamic strategy.
\item (b)--(e) use one-period moments only.
\end{itemize}

\subsection*{Several risky assets: answer 2(g)}
Risky mix $a$ ($\mathbf1'a=1$): $\mu_p(a)=a'\mu$, $\sigma_p^2(a)=a'\Sigma a$; total allocation $w$. For fixed $a$ the problem in $w$ is (a)--(e) with $(\mu_p,\sigma_p)$:
\[
\max_wg(w;a)=\log(1+r)+\tfrac12SR_p(a)^2,\qquad SR_p(a)=\frac{\mu_p(a)-r}{\sigma_p(a)} .
\]
$\Rightarrow\max_a\max_wg\iff\max_aSR_p(a)$: choose the tangency portfolio, then $w^*=(\mu_p-r)(1+r)/\sigma_p^2$. $r$ enters only additively and through excess returns, so the argument holds for any $r$ (including $0$).

Vector form, $x=wa$: $g\approx r+x'(\mu-r\mathbf1)-\frac12x'\Sigma x$,
\[
x^*=\Sigma^{-1}(\mu-r\mathbf1)\propto a_{\tan},\qquad g^*=r+\tfrac12(\mu-r\mathbf1)'\Sigma^{-1}(\mu-r\mathbf1)=r+\tfrac12SR_{\tan}^2 .
\]
Three-asset example ($\mu=(0.008,0.005,0.004)$, $\sigma=(0.11,0.05,0.03)$, $r=0.002$): $SR_{\tan}=\rTanSR$, $x^*=\rKellyTotal\times a_{\tan}$, $g^*=\rGVector$.
\end{document}
'''


def main():
    CLAIMS.clear()
    bind('ZeroCross', 'results/tables/bound_landmarks.json', 'zero_crossing_ratio')
    h = pd.read_csv(ROOT / 'results/tables/heterogeneous_examples.csv')
    (ROOT / 'results/tables/heterogeneous_summary.json').write_text(json.dumps(dict(max_abs_difference=float(h.abs_difference.max()), trials=len(h), improves=int(h.improves.sum())), indent=2) + '\n')
    bind('HetMaxDiff', 'results/tables/heterogeneous_summary.json', 'max_abs_difference', digits=1)
    CLAIMS[-1]['formatted'] = f"{float(json.loads((ROOT / 'results/tables/heterogeneous_summary.json').read_text())['max_abs_difference']):.1e}"
    for lab, col in [('Mu', 'mu'), ('Sigma', 'sigma')]:
        bind(lab, 'results/tables/growth_comparison.csv', col, {'rate': 0.0}, digits=3)
    bind('Periods', 'results/tables/growth_comparison.csv', 'periods', {'rate': 0.0}, digits=0)
    bind('Paths', 'results/tables/growth_comparison.csv', 'paths', {'rate': 0.0}, digits=0)
    CLAIMS[-1]['formatted'] = '{:,}'.format(int(float(CLAIMS[-1]['formatted']))).replace(',', '{,}')
    for lab, col in [('TanSR', 'tangency_sharpe'), ('KellyTotal', 'kelly_total_risky'), ('GVector', 'g_star_vector')]:
        bind(lab, 'results/tables/multi_asset_example.json', col)
    grid, het, gro = tables()
    defs = '\n'.join(r'\newcommand{\r' + c['label'] + '}{' + c['formatted'] + '}' for c in CLAIMS)
    doc = BODY.replace('% BINDINGS', defs).replace('% GRID', grid).replace('% HET', het).replace('% GROWTH', gro)
    (ROOT / 'report/main.tex').write_text(doc)
    (ROOT / 'report/numerical_claims.json').write_text(json.dumps(CLAIMS, indent=2) + '\n')
    print('report/main.tex written with', len(CLAIMS), 'bound quantities')


if __name__ == '__main__':
    main()
