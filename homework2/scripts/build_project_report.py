"""Build the HW2 project report from preserved outputs; no acquisition/backtest."""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'report/project';OUT.mkdir(parents=True,exist_ok=True)
T=ROOT/'results/tables'
p=pd.read_csv(T/'performance.csv');p=p[(p['sample']=='full') & (p.basis!='gross zero modeled trading costs')].set_index('variant')
checks=[]
for v in ['A0','A1','A2','A3','B0','B1','B2','B3','SPY','60_40','CASH']:
 d=pd.read_csv(T/f'{v}_daily.csv',parse_dates=['date']);m=pd.read_csv(T/f'{v}_monthly.csv')
 nav=np.cumprod(1+d.return_net.to_numpy());years=((d.date.iloc[-1]-d.date.iloc[0]).days+1)/365.25
 vals={'CAGR':nav[-1]**(1/years)-1,'annual_mean':m['return'].mean()*12,'annual_vol':m['return'].std(ddof=1)*np.sqrt(12),'max_daily_drawdown':np.min(nav/np.maximum.accumulate(np.r_[1,nav])[1:]-1)}
 if v!='CASH':vals['Sharpe']=np.sqrt(12)*m.excess.mean()/m.excess.std(ddof=1)
 q=m['return'].quantile(.05);vals['ES95_loss']=-m.loc[m['return']<=q,'return'].mean()
 for k,a in vals.items():
  b=float(p.loc[v,k]);assert np.isclose(a,b,rtol=1e-10,atol=1e-12),(v,k,a,b)
  checks.append(dict(variant=v,metric=k,recomputed=float(a),stored=b,passed=True))
 assert np.allclose(nav,d.nav,rtol=1e-11,atol=1e-12)
 if v.startswith('B') or v in ['SPY','60_40','CASH']:
  assert np.isclose(1-d.cash_weight_end.mean(),p.loc[v,'average_exposure'],atol=1e-12)
# Dynamic values and compact, readable tables in percent units.
def fmt(x,pct=False):return '--' if pd.isna(x) else f'{x*(100 if pct else 1):.5f}'
def table(variants,cols,headers,percent=()):
 lines=[r'\begin{center}\small',r'\begin{tabular}{l'+'r'*len(cols)+'}',r'\toprule','Strategy & '+' & '.join(headers)+r'\\\midrule']
 for v in variants:lines.append(v.replace('_','/')+' & '+' & '.join(fmt(p.loc[v,c],c in percent) for c in cols)+r'\\')
 return '\n'.join(lines+[r'\bottomrule\end{tabular}\end{center}'])
def fig(name,caption,height='0.46'):
 return r'\begin{figure}[H]\centering\includegraphics[width=\linewidth,height='+height+r'\textheight,keepaspectratio]{../../results/figures/'+name+r'.png}\caption{'+caption+r'}\end{figure}'
perfcols=['CAGR','annual_vol','Sharpe','max_daily_drawdown']
perfheads=['CAGR (\\%)','Vol. (\\%)','Sharpe','Max. DD (\\%)']
A=table(['A0','A1','A2','A3'],perfcols,perfheads,perfcols[:2]+['max_daily_drawdown'])
B=table(['B0','B1','B2','B3','SPY','60_40','CASH'],perfcols,perfheads,perfcols[:2]+['max_daily_drawdown'])
D=table(['B0','B1','B2','B3','SPY','60_40'],['annual_mean','skew','excess_kurtosis','ES95_loss'],['Mean (\\%)','Skew','Excess kurt.','ES5 (\\%)'],['annual_mean','ES95_loss'])
text=r'''\documentclass[11pt]{article}
\usepackage[margin=0.85in]{geometry}
\usepackage{amsmath,amssymb,booktabs,graphicx,xcolor,float,hyperref,microtype}
\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue}
\setlength{\emergencystretch}{3em}\setlength{\parindent}{0pt}\setlength{\parskip}{0.45em}
\begin{document}
\begin{center}{\Large\bfseries FINCB9339 Systematic Investment Strategies\\[3pt]Homework 2: Momentum Investing}\\[8pt]
Hanyu Zhang (hz3069)\\Columbia Business School, Fall 2026\\Project research report\end{center}
\section*{Executive summary}
\textbf{Pitch objective.} Raise assets for a transparent, monthly cross-asset ETF portfolio. The proposed portfolio is research-stage B3: relative momentum, a cash hurdle and an unlevered volatility cap. An illustrative \$1 million execution-validation scenario should precede consideration of \$10 million. Neither amount is a capacity commitment.

\textbf{Strategy and contribution.} Two controlled experiments separate mechanisms: A0--A3 adjust exposure to the aggregate equity momentum factor; B0--B3 add selection, absolute filtering and risk control across eight ETFs. The contribution is an auditable implementation and comparison of established ideas, rather than a newly discovered premium. B3 is the investor-facing prototype because its assets and orders can be specified directly.

\textbf{Results.} Over the common ETF capital window August 31, 2007--August 31, 2026 (first invested return September 4), B3 has modeled net CAGR \textbf{6.89099\%}, monthly cash-adjusted Sharpe \textbf{0.61357}, and maximum daily drawdown \textbf{17.91141\%}. Average cash is \textbf{22.82457\%}. B1 earns higher CAGR (8.65799\%); monthly 60/40 has higher Sharpe (0.71919). Protection therefore entails less participation and lower returns.

\textbf{Robustness.} The B3-minus-60/40 Sharpe difference is $-0.10562$, with paired six-month block-bootstrap 95\% interval $[-0.59792,0.27882]$. This does not establish superiority. Cost, signal-window, asset-exclusion and execution-delay diagnostics expose material implementation dependence. The inspected 2020 onward historical holdout is not prospective evidence.

\textbf{Feasibility and limits.} The evolving \$10 million scenario reaches 19.17367\% of DBC's historical daily-volume proxy. Single-close execution at that size is unproven. Factor experiment A3 improves gross risk statistics, but aggregate returns omit constituent trading and borrowing economics. Data revisions, retrospective universe choice, cash implementation, fees and taxes remain limitations. The saved results are reconciled in this report; missing original vendor caches prevent a fresh end-to-end data replay from this checkout.
\clearpage
\section{Landscape, motivation and research scope}
Momentum can represent cross-sectional rankings (relative strength), an asset's own trend (absolute momentum), or both. Delayed incorporation of information, extrapolation and risk compensation are plausible explanations. None guarantees a profitable premium in this universe. Buy-and-hold maintains exposure; stock momentum ETFs rank equities; futures trend strategies can short declining markets. Our ETF design is long-only and moves failed allocations to cash.

Daniel and Moskowitz (2016) relate equity momentum crashes to panic states following market losses and high volatility, when previous losers rebound. Experiment A uses a simple, fixed stress heuristic and inverse-volatility sizing to investigate that mechanism. It does not replicate their conditional-mean/variance strategy or their stock portfolio construction. The ETF experiment instead combines familiar relative and absolute momentum with risk control. Its equal capital slots are not equal risk contributions.

Asness et al. (2014) motivate attention to costs, robustness and diversification. Kolanovic and Wei (2015) distinguish relative and absolute signals, discuss information gaps, and illustrate that volatility targeting need not improve every strategy. Baltas and Kosowski (supplied 2013 version) study signed futures trends and volatility normalization; their futures results and capacity do not transfer directly to these ETFs. The lecture's dual-momentum modules motivate a 12-month, cash-relative signal, but our eight-ETF, three-slot portfolio is a different construction.

The assignment deliverable remains the investor presentation in \path{submission/Investor_Presentation.pdf}. This companion report explains the complete research project: rules, input provenance, accounting, measured outcomes, adverse evidence, investor questions and reproduction limits.
\section{Data, coverage and provenance}
The original research acquired real snapshots from Kenneth French (daily/monthly Mom, market, SMB, HML and RF), Cboe (VIX closes), and Yahoo Finance via yfinance (ETF adjusted prices, closes, volumes and actions). The cutoff was September 30, 2026; French daily RF/Mom end August 31, so September ETF/VIX observations are excluded from performance. Input timestamps, original headers, request options and SHA-256 digests are retained in \texttt{data/manifests/}.

French percentage factors are divided by 100 once. Missing markers are treated as missing rather than zero. VIX is joined backward, retaining source dates and rejecting staleness above seven calendar days. ETF adjusted closes proxy total returns, including distributions; dividends are not added again. Raw Close times Volume supplies the separate liquidity proxy. Split-normalized vendor Close is not an original pre-split transaction price.

DBC's first vendor observations (February 6, 2006) bind the common ETF history. Twelve-month signals and B3's additional 126-observation risk warmup yield an initial common execution on August 31, 2007. The factor experiment first executes January 31, 1990, with invested returns from February 1. No synthetic early ETF history is inserted. Within each experiment all primary variants share dates; differences across the two experiments are not controlled performance comparisons.
\clearpage
\section{Experiment A: crash-aware equity momentum}
Let $m_d$ denote daily French Mom and $f_d$ RF in decimal units. The factor is
\begin{equation}
m_d=\tfrac12(Small\ High_d+Big\ High_d)-\tfrac12(Small\ Low_d+Big\ Low_d).
\end{equation}
French's six underlying portfolios differ from a decile winners-minus-losers strategy. The modeled capital return is
\begin{equation}r_d=f_d+a_{d-1}m_d-c_d.\end{equation}
Mom is already an excess spread. Cash collateral earns RF once; the capital return is later compared with cash for Sharpe. Unit factor exposure corresponds conventionally to long-one/short-one, gross notional approximately two per capital dollar. This stylized financing convention does not establish executable stock-level funding or borrow costs.

At the penultimate trading close $s_t$, calculate
\begin{equation}
\widehat\sigma_t=\sqrt{252}\,s(m_{s_t-125:s_t}),\qquad
v_t=\min\left(1.5,\frac{0.10}{\max(\widehat\sigma_t,0.05)}\right),
\end{equation}
where $s$ is sample standard deviation. Compound $Mkt-RF+RF$ to obtain the market total-return index $I$. Define
\begin{align}
b_t&=\mathbf{1}\{I(s_t)/I(s_{t-24})-1<0\},\\
h_t&=\mathbf{1}\{VIX(s_t)>25\},\qquad g_t=1-\tfrac12(b_t+h_t).
\end{align}
Snapshots are monthly, at the same penultimate-close convention. The four exposure rules are
\begin{center}\begin{tabular}{lll}\toprule
Variant & Exposure & Purpose\\\midrule
A0 & $a_t=1$ & Static factor comparator\\
A1 & $a_t=v_t$ & Inverse-volatility overlay\\
A2 & $a_t=g_t$ & Bear/VIX stress overlay\\
A3 & $a_t=v_tg_t$ & Combined overlay\\\bottomrule\end{tabular}\end{center}
Exposures execute at the final trading close and remain fixed until the next monthly execution. Existing exposure earns the execution-day return; the new position first earns the following session's return. Information at $s_t$ therefore does not earn the return ending at $s_t$. The information gap reduces timing concerns but cannot certify actual VIX publication or closing fills.

Primary A results are gross. Separate sensitivities charge $2|\Delta a|$ times an assumed traded-dollar fee, or a stated annual exposure drag. These incomplete charges exclude transactions inside the factor and do not turn a factor series into a tradeable stock portfolio. Under the exposure cap, conventional gross notional can reach three times capital. No sector-neutrality, short availability or live capacity claim follows from these data.
\clearpage
\section{Experiment B: cross-asset ETF dual momentum}
The fixed universe is SPY (US equity), EFA (developed equity), EEM (emerging equity), IEF (intermediate Treasuries), TLT (long Treasuries), GLD (gold), DBC (commodity futures exposure), and VNQ (US real estate). Eight tickers are not eight independent economic risks: equities and duration are clustered. Retrospective selection of this surviving universe remains a bias.

For adjusted price $P_i$ and identical snapshot endpoints,
\begin{equation}
M_{i,t}=\frac{P_i(s_t)}{P_i(s_{t-12})}-1,\qquad
C_t=\prod_{d\in(s_{t-12},s_t]}(1+f_d)-1.
\end{equation}
The latest month is included. Rank by descending $M$, breaking ties alphabetically. Let $J_t$ be the top three and $u_{i,t}=\frac13\mathbf{1}\{i\in J_t\}\mathbf{1}\{M_{i,t}>C_t\}$.
\begin{center}\begin{tabular}{lll}\toprule
Variant & Risky target & Cash allocation\\\midrule
B0 & $1/8$ in each ETF & Zero\\
B1 & $\frac13\mathbf{1}\{i\in J_t\}$ & Zero\\
B2 & $u_{i,t}$ & $1-\sum_i u_{i,t}$\\
B3 & $q_tu_{i,t}$ & $1-q_t\sum_i u_{i,t}$\\\bottomrule\end{tabular}\end{center}
Failed B2 slots are not replaced or renormalized. The cap is
\begin{equation}
q_t=\min\left(1,\frac{0.10}{\max(\sqrt{252}\,s(e^{B2}_{s_t-125:s_t}),0.05)}\right),
\end{equation}
where $e^{B2}$ is the available historical unscaled gross B2 strategy daily excess return. It is portfolio-history risk, rather than the volatility of today's target holdings. The signal can lag a change in holdings or correlations. B3 never borrows to reach the 10\% target.

Signals use the penultimate close; targets execute at the final close and earn returns from the next session. Fractional shares are allowed, cash earns RF, and holdings drift between monthly executions. SPY buy-and-hold, monthly SPY60\%/IEF40\%, and cash are common-window benchmarks, with comparable initial investment accounting.

For example, top-three momentum of 12\%, 8\%, 1\% versus cash 2\% leaves two $1/3$ B2 positions. If forecast risk is 16\%, $q=0.625$; B3 invests $0.20833333$ in each passing ETF and $0.58333333$ in cash. This is an illustrative calculation, not an observed allocation.
\clearpage
\section{Portfolio accounting and performance definitions}
Beginning-of-day weights earn daily total returns. Before any closing rebalance,
\begin{align}
r_d^g&=\sum_i w_{i,d-1}r_{i,d}+w_{c,d-1}f_d,\\
\widetilde w_{i,d}&=\frac{w_{i,d-1}(1+r_{i,d})}{1+r_d^g},\qquad
T_d=\sum_{i\in risky}|w^*_{i,d}-\widetilde w_{i,d}|,\\
V_d&=V_{d-1}(1+r_d^g)(1-cT_d),\qquad c=0.001.
\end{align}
Both buys and sells count; cash turnover is excluded. A full switch between two risky ETFs has turnover two and costs 20 basis points at this assumption. Post-cost wealth is allocated to target weights. The proportional haircut approximates costs using pre-cost notional; actual post-cost trade dollars differ slightly. Initial trades incur charges. Expenses already embedded in ETF prices are not charged twice; management fees and taxes are excluded.

For a worked drift example, a 50/50 allocation with returns 10\% and zero becomes\[\widetilde w=(0.52380952,0.47619048).\]Moving fully into the second asset gives turnover $T=1.04761905$ and post-cost wealth\[1.05(1-0.00104761905)=1.04890000.\]A nonpositive NAV or return at/below $-100\%$ terminates the model; returns are not clipped or restarted.

Monthly capital return $R_m$ compounds daily net growth. The initial month-end trade cost is folded into the first holding month's return, preserving full capital wealth and avoiding an artificial stub month. Monthly cash $F_m$ compounds daily RF and $E_m=R_m-F_m$. Reported statistics use
\begin{align}
\mu_{ann}&=12\overline R,\qquad \sigma_{ann}=\sqrt{12}\,s(R),\\
SR&=\sqrt{12}\,\overline E/s(E),\qquad
CAGR=V_D^{1/Y}-1,\\
Y&=(D_{last}-D_{first}+1)/365.25,\\
DD_d&=V_d/\max(1,V_1,\ldots,V_d)-1.
\end{align}
Thus volatility is monthly capital-return volatility and Sharpe uses cash-adjusted monthly returns. CAGR uses inclusive elapsed calendar days from initial execution. These are the frozen HW2 conventions, rather than the daily 252-observation conventions used in HW3. Cash's Sharpe is undefined because its excess return is identically zero.

Skewness and Fisher excess kurtosis use sample-adjusted estimators. Monthly VaR5 loss is minus the empirical fifth percentile of $R$; ES5 loss is minus the average return at or below that cutoff. Maximum daily drawdown includes initial wealth one; month-end drawdown is a distinct statistic. Full-period tables retain all crisis observations and initial costs. Subperiods retain inherited signal and holding histories.
\clearpage
\section{Factor experiment results}
@@A@@
@@AFIG@@
The table uses percentages for return, volatility and signed drawdown. January 31, 1990--August 31, 2026 is the common capital period; invested returns start February 1. A3 raises gross CAGR from 7.93818\% to 11.99354\% and reduces maximum drawdown from 63.28816\% to 18.89310\%. Its mean factor exposure is 0.88869, compared with 1.00000 for A0: exposure timing and less average risk both matter.

During March--May 2009, static synthetic capital loses 45.64\%, while the stress and combined variants have zero factor exposure and receive the recorded zero RF. This is de-risking rather than option protection or an executable replication of the paper's hedge. A1 also improves gross Sharpe while mean unit exposure remains near one. These outcomes support further investigation of the timing mechanism, subject to the aggregate factor's omitted trading, funding and borrow economics. The full A0 drawdown remains unrecovered at the sample endpoint.
\clearpage
\section{ETF results and economic trade-offs}
@@B@@
@@BFIG@@
August 31, 2007--August 31, 2026 is the common capital period. Relative selection B1 improves CAGR over equal-weight B0 but concentrates the portfolio. Adding the cash hurdle in B2 reduces CAGR and barely changes the worst drawdown (25.14653\% versus B1's 25.12325\%): absolute filtering alone does not deliver the hoped-for downside improvement here.

B3's 17.91141\% drawdown and 9.26412\% annual volatility are lower, accompanied by average cash 22.82457\% versus B2's 5.21727\%. Lower exposure misses profitable markets as well as losses. B1 has higher CAGR and 60/40 higher Sharpe. B3 is recommended as a research-stage risk-limited design, rather than as the historical return or Sharpe winner. The 10\% cap is a forecast-based control, not a maximum realized loss guarantee.
\clearpage
\section{Distributions, exposure and adverse episodes}
@@D@@
Mean, volatility and tails above use monthly capital returns; ES5 is a positive loss percentage. The reported drawdowns elsewhere use daily paths. Both horizons matter: month-end risk measures alone can conceal intramonth losses. B3's lower downside accompanies smaller risky positions; it should not be described as costless crash protection.
@@EXPOSURE@@
In 2020 B3 returns 7.77\%, compared with 10.22\% for B1/B2, 15.99\% for 60/40 and 18.33\% for SPY. It misses a substantial part of the rebound. In 2022 B3 loses 5.03\%, versus B2's 9.45\%, 60/40's 16.67\% and SPY's 18.18\%. These episodes illustrate the intended risk trade-off without suggesting that the rule avoids all stress. They remain included in aggregate results.

Monthly CAPM and contextual factor regressions use HAC standard errors with three lags. Their intercepts are descriptive rather than causal alpha: omitted Treasury, gold and commodity exposures can matter. The factor experiment's contextual regressions also include static momentum exposure. Regression coefficients, worst months, allocation histories and exposure concentration remain exported for inspection.
\clearpage
\section{Robustness, uncertainty and data limitations}
The recorded primary specification was frozen before the original download/performance run. Development ends in 2013, validation spans 2014--2019, and the historical holdout starts in 2020. The holdout is publicly known and inspected in the recommendation process. It does not eliminate retrospective universe choice or establish a prospective track record. The variant ledger contains 84 evaluated rows, including adverse diagnostics and incomplete-cost experiments.

Paired moving-block bootstrap comparisons use six-month noncircular overlapping blocks, 1,000 draws and seed 9339. The same resampled month indices apply to both strategies. For B3 minus B2, the full-sample Sharpe difference is 0.04352 with 95\% interval $[-0.06125,0.16253]$. Against 60/40, the difference is $-0.10562$ with interval $[-0.59792,0.27882]$. Neither establishes superiority. Resampling fixed historical paths does not recreate signals, unseen crises, or remove selection bias.

Factor diagnostics vary windows (63/252 days), targets (8/12\%), VIX thresholds (20/30), bear windows (12/36 months) and cap (1). ETF diagnostics vary lookback (6/9 months), slots (2/4), skipped latest month, cost (0/5/25/50 bps), each excluded ETF and an extra execution-session delay. Common eligible sensitivity dates begin with execution October 31, 2007 because the skipped-month version requires longer warmup. The primary period remains unchanged.
@@ROBUST@@
The nine-month B3 diagnostic is stronger than primary but is not promoted to the main rule. Skipping a month deepens drawdown to 24.73\%; removing GLD lowers CAGR to 5.28\%; 50-bps costs lower CAGR to 5.20\% on sensitivity dates. Gold dependence, whipsaw and execution assumptions therefore matter. Full-precision sensitivity CSVs distinguish these dates from the primary results.

Two October 2008 EEM daily gains above 20\% were flagged and retained, not clipped. Independent source validation remains incomplete. Current French data incorporate the FIZ-to-CIZ transition and possible historical revisions; daily-derived factor capital returns are not spliced to official monthly momentum returns. Provider split/volume conventions and corporate-action adjustments also limit return and capacity confidence.
\clearpage
\section{Feasibility, investor questions and recommendation}
B3 risky turnover averages 3.14944 times capital annually, counting both sides. At 10 bps this implies approximately 0.31\% annual simple modeled cost; summed cost fractions are not a CAGR difference. The allowance is assumed, rather than calibrated to spreads or stressed fills. Investor fees, taxes, whole-share rounding, cash-vehicle costs and exact closing-auction fills remain excluded.

For each rebalance, the liquidity screen is
\begin{equation}
Participation_{i,t}=\frac{AUM_0\,V_t^{pretrade}|\Delta w_{i,t}|}{ADV20_{i,s_t}},
\end{equation}
where ADV20 averages vendor Close times Volume over the 20 sessions ending at the signal close. Scenarios start at \$1m/\$10m/\$50m and evolve with strategy NAV without flows. At \$10m, B3's maximum DBC participation is 19.17367\%; IEF also has material events. All-day vendor volume cannot certify closing-auction or underlying-asset liquidity. The \$1m scenario mechanically scales participation to one tenth but remains provisional.

\textbf{What is the competitive advantage?} Explicit holdings, monthly decisions, risk limits and auditability. The evidence supports a design trade-off, not reliable return superiority. Existing relative/absolute momentum ideas are not new alpha.

\textbf{When does the design fail?} Fast reversals, sideways whipsaw, correlated equity/duration losses, changes in covariance, gold dependence and prolonged cash opportunity costs. Backward-looking risk estimates can react after a shock. GLD is a bullion trust and DBC a commodity futures pool with roll, collateral and tax considerations; their exposures differ from ordinary equity funds.

\textbf{What capital is justified?} No certified live amount follows from the backtest. Independent volume and distribution validation, historical spreads, auction-volume/impact analysis and prospective execution records are required. Order slicing would change the current execution model and requires separate validation. Constituents, stock borrow and financing are missing for A, so its factor results cannot support an AUM pitch.

\textbf{What happens after a data failure?} The documented operating proposal preserves existing holdings pending verified data and escalation; it does not invent prices or silently substitute assets. Unexplained data/accounting defects or repeated liquidity failures should suspend new decisions for review. Such governance is a proposed live process, not a retrofitted historical return rule.

\textbf{Recommendation.} Keep B3 as a research-stage, risk-limited ETF pitch, with B1 and 60/40 serious comparators. Validate an illustrative \$1m implementation, then collect time-stamped prospective paper decisions before considering larger assets. The known historical holdout, bootstrap intervals and missing execution evidence do not establish live readiness.
\clearpage
\section{Project map, verification and reproduction}
The project root is \texttt{homework2/}. \texttt{config/base.yaml} freezes rules; \texttt{src/momentum\_hw2/} implements signals, data handling, factor/ETF backtests and statistics. \texttt{results/tables/} contains daily/monthly returns and comparisons; \texttt{results/audits/} contains decisions, targets, trades, drifted holdings and checks. \texttt{notebooks/} explains both experiments; \texttt{docs/research/} retains the plan, freeze, provenance, limitations and requirement matrix. Original inputs/manifests and historical audit records are preserved.

The previous run records 11 passing tests, 25 independent accounting checks and 137 identical numerical outputs in a clean replay. Those are historical records. For this report, the saved daily/monthly series were independently used to reconcile each main variant's CAGR, annual mean/volatility, Sharpe, daily drawdown and monthly ES, plus cumulative NAV and ETF average exposure. The current check is stored in \texttt{results/audits/project\_report\_verification.json}. Figures are retained from the existing research outputs; no new market data or revised backtest were introduced.

\textbf{Current reproduction boundary.} Raw and processed vendor caches are absent from this checkout. Consequently a fresh offline backtest and source-level endpoint verification cannot be repeated without restoring files matching \texttt{data/manifests/inputs.json}. Synthetic unit tests and this report's saved-output reconciliation remain runnable. New provider downloads can revise historical results and constitute a new vintage.

From the project root, use the shared course interpreter for all Python execution:
\begin{quote}\small\ttfamily
\$HOME/.venvs/sys-inv/bin/python -m pytest -q\\
\$HOME/.venvs/sys-inv/bin/python scripts/build\_project\_report.py\\
cd report/project\\
tectonic --keep-logs main.tex
\end{quote}
The builder produces the editable source and verification record from preserved CSVs. Copy the compiled PDF to \texttt{submission/HW2\_Hanyu\_Zhang\_FINCB9339.pdf}. A standard LaTeX engine can also compile the source. Do not create a homework environment, run \texttt{uv sync}, or replace shared dependencies. The README documents the existing shared environment and the separate cache-dependent analysis commands.

\section*{References}
\small
Venetoulias, A. (2026). \emph{B9339 Homework 2} and \emph{Lectures 3--5: Momentum}, Columbia Business School, supplied course materials.\\[4pt]
Daniel, K., and T. Moskowitz (2016). Momentum crashes. \emph{Journal of Financial Economics} 122, 221--247.\\[4pt]
Asness, C., A. Frazzini, R. Israel, and T. Moskowitz (2014). Fact, Fiction and Momentum Investing. \emph{Journal of Portfolio Management}.\\[4pt]
Kolanovic, M., and Z. Wei (2015). \emph{Momentum Strategies Across Asset Classes: Risk Factor Approach to Trend Following}, supplied report, pp. 19--20, 59--60.\\[4pt]
Baltas, N., and R. Kosowski (2013 supplied version). \emph{Momentum Strategies in Futures Markets and Trend-Following Funds}, January 5, section 3.\\[4pt]
Kenneth French Data Library; Cboe VIX historical data; Yahoo Finance via yfinance. Acquisition records and source URLs: \texttt{data/manifests/inputs.json}; source interpretation: \texttt{docs/research/source\_map.md}. These identify the original data vintage; this report does not claim a new acquisition.
\end{document}
'''
text=text.replace('@@A@@',A).replace('@@B@@',B).replace('@@D@@',D)
text=text.replace('@@AFIG@@',fig('A_nav_drawdown','Synthetic factor capital wealth and daily drawdowns, common A sample. Primary curves are gross.','0.39'))
text=text.replace('@@BFIG@@',fig('B_nav_drawdown','ETF capital wealth and daily drawdowns, common B sample. Costs are modeled at 10 bps per risky dollar.','0.36'))
text=text.replace('@@EXPOSURE@@',fig('B_allocations','B3 allocation and cash history from the saved ETF experiment; cash holdings reduce average risky exposure.','0.38'))
text=text.replace('@@ROBUST@@',fig('B_robustness','Preserved B3 sensitivity results. Diagnostic samples use common eligibility; alternatives are not promoted to the primary rule.','0.29'))
# Eliminate unsupported manually rounded precision in text by sourcing exact values.
text=text.replace('25.14653',fmt(-p.loc['B2','max_daily_drawdown'],True)).replace('25.12325',fmt(-p.loc['B1','max_daily_drawdown'],True)).replace('9.26412',fmt(p.loc['B3','annual_vol'],True)).replace('5.21727',fmt(p.loc['B2','cash_fraction'],True))
(OUT/'main.tex').write_text(text)
manifest={str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(T.glob('*.csv'))}
(ROOT/'results/audits/project_report_verification.json').write_text(json.dumps(dict(scope='Saved-output reconciliation only; vendor caches absent. No fresh backtest.',metric_checks=len(checks),all_passed=True,checks=checks,input_csv_sha256=manifest),indent=2)+'\n')
print('Built project report source;',len(checks),'independent metric reconciliations passed for 11 variants.')
