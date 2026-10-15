"""Submission report generated from explicitly bound result cells and verified series."""
from pathlib import Path
import json,re,os
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.cache/matplotlib'))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
CLAIMS=[]

def esc(x):return str(x).replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def load(path):return pd.read_csv(ROOT/path,index_col=0)
def bind(label,path,row,column,scale=1,offset=0,where=None,digits=5):
    frame=pd.read_csv(ROOT/path)
    selector=where or {frame.columns[0]:row}
    chosen=frame.copy()
    for key,value in selector.items():chosen=chosen[chosen[key].astype(str)==str(value)]
    if len(chosen)!=1:raise ValueError((label,selector,len(chosen)))
    value=(float(chosen.iloc[0][column])+offset)*scale
    formatted=f'{value:.{digits}f}'
    CLAIMS.append(dict(label=label,path=path,selector=selector,column=column,scale=scale,offset=offset,digits=digits,formatted=formatted))
    return r'\r'+label+'{}'

def table(frame,columns,caption,percent=(),rowhead='Strategy'):
    out=r'\begin{table}[H]\centering\small\caption{'+caption+'}\n'
    out+=r'\begin{tabular}{l'+'r'*len(columns)+r'}\toprule'+'\n'+rowhead+' & '+' & '.join(v for _,v in columns)+r'\\\midrule'+'\n'
    for name,row in frame.iterrows():
        values=[]
        for key,header in columns:
            v=float(row[key])*(100 if key in percent else 1)
            values.append(str(int(v)) if key in ['n','n_pairs'] else f'{v:.5f}')
        out+=esc(name)+' & '+' & '.join(values)+r'\\'+'\n'
    return out+r'\bottomrule\end{tabular}\end{table}'+'\n'

def fig(name,caption,height='3.8in'):
    return r'\begin{figure}[H]\centering\includegraphics[width=\linewidth,height='+height+r',keepaspectratio]{../results/figures/'+name+r'.pdf}\caption{'+caption+r'}\end{figure}'+'\n'

def main():
    CLAIMS.clear()
    b=load('results/tables/baseline_performance.csv');d=load('results/tables/conditioned_performance.csv');e=load('results/tables/historical_comparison.csv')
    controls=load('results/audit/exposure_controls.csv');ci=load('results/audit/filter_sharpe_intervals.csv');lag=load('results/audit/additional_decision_lag.csv')
    values={}
    specs={
      'BaseSharpe':('results/tables/baseline_performance.csv','3M_3_equal','sharpe',1),
      'BaseArith':('results/tables/baseline_performance.csv','3M_3_equal','arithmetic',100),
      'BaseGeom':('results/tables/baseline_performance.csv','3M_3_equal','geometric',100),
      'BaseVol':('results/tables/baseline_performance.csv','3M_3_equal','volatility',100),
      'BaseDD':('results/tables/baseline_performance.csv','3M_3_equal','max_drawdown',100),
      'BaseSkew':('results/tables/baseline_performance.csv','3M_3_equal','skewness',1),
      'BaseKurt':('results/tables/baseline_performance.csv','3M_3_equal','excess_kurtosis',1),
      'BaseES':('results/tables/baseline_performance.csv','3M_3_equal','es05',100),
      'BaseWorst':('results/tables/baseline_performance.csv','3M_3_equal','worst_day',100),
      'CondSharpe':('results/tables/conditioned_performance.csv','AY3M','sharpe',1),
      'CondGeom':('results/tables/conditioned_performance.csv','AY3M','geometric',100),
      'CondES':('results/tables/conditioned_performance.csv','AY3M','es05',100),
      'CondDD':('results/tables/conditioned_performance.csv','AY3M','max_drawdown',100),
      'CondActive':('results/tables/conditioned_performance.csv','AY3M','active_fraction',100),
      'CondBaseSharpe':('results/tables/conditioned_performance.csv','baseline','sharpe',1),
      'CondBaseSkew':('results/tables/conditioned_performance.csv','baseline','skewness',1),
      'CondSkew':('results/tables/conditioned_performance.csv','AY3M','skewness',1),
      'ConstDD':('results/audit/exposure_controls.csv','AY3M','constant_drawdown',100),
      'VolMatchDD':('results/audit/exposure_controls.csv','AY3M','volmatched_drawdown',100),
      'ActiveES':('results/audit/exposure_controls.csv','AY3M','active_es05',100),
      'OffMean':('results/audit/exposure_controls.csv','AY3M','inactive_mean_daily',100),
      'OffProfits':('results/audit/exposure_controls.csv','AY3M','skipped_profit_days',1),
      'OffCompound':('results/audit/exposure_controls.csv','AY3M','off_compound',100),
      'LagBase':('results/audit/additional_decision_lag.csv','baseline_lagged','sharpe',1),
      'LagAY':('results/audit/additional_decision_lag.csv','AY3M_lagged','sharpe',1),
      'LagSix':('results/audit/additional_decision_lag.csv','AY6M_lagged','sharpe',1),
      'LagPrimaryAY':('results/audit/additional_decision_lag.csv','AY3M_primary','sharpe',1),
      'CICondLow':('results/audit/filter_sharpe_intervals.csv','AY3M','ci_low',1),
      'CICondHigh':('results/audit/filter_sharpe_intervals.csv','AY3M','ci_high',1),
      'HistSharpe':('results/tables/historical_comparison.csv','historical','sharpe',1),
      'HistGeom':('results/tables/historical_comparison.csv','historical','geometric',100),
      'HistDD':('results/tables/historical_comparison.csv','historical','max_drawdown',100),
      'HistES':('results/tables/historical_comparison.csv','historical','es05',100),
      'HistSkew':('results/tables/historical_comparison.csv','historical','skewness',1),
      'EBaseSharpe':('results/tables/historical_comparison.csv','baseline','sharpe',1),
      'EImpliedSharpe':('results/tables/historical_comparison.csv','FX_AY3M','sharpe',1),
      'EImpliedES':('results/tables/historical_comparison.csv','FX_AY3M','es05',100),
      'EImpliedSkew':('results/tables/historical_comparison.csv','FX_AY3M','skewness',1),
      'CIDiffLow':('results/audit/historical_sharpe_intervals.csv','AY3M minus historical','ci_low',1),
      'CIDiffHigh':('results/audit/historical_sharpe_intervals.csv','AY3M minus historical','ci_high',1),
      'SizeEffect':('results/tables/design_dimensions.csv','k','mean_absolute_sharpe_difference',1),
      'MethodEffect':('results/tables/design_dimensions.csv','method','mean_absolute_sharpe_difference',1),
      'TenorEffect':('results/tables/design_dimensions.csv','tenor','mean_absolute_sharpe_difference',1),
      'SpreadGeom':('results/tables/baseline_performance.csv','1M_2_spread','geometric',100),
      'SpreadVol':('results/tables/baseline_performance.csv','1M_2_spread','volatility',100),
      'SpotMean':('results/tables/baseline_decomposition.csv','spot','annualized_mean',100),
      'CarryMean':('results/tables/baseline_decomposition.csv','carry','annualized_mean',100),
      'InteractionMean':('results/tables/baseline_decomposition.csv','interaction','annualized_mean',100),
    }
    for label,(path,row,column,scale) in specs.items():values[label]=bind(label,path,row,column,scale,digits=0 if label=='OffProfits' else 5)
    for label,indicator,period in [('VixCorr','VIX','all'),('AYCorr','AY3M','all'),('VixCrisis','VIX','2008'),('AYCrisis','AY3M','2008')]:
        values[label]=bind(label,'results/tables/volatility_correlations.csv',None,'pearson',where={'period':period,'indicator':indicator})
    for label,regime,column in [('LowES','low','es05'),('HighES','high','es05'),('LowMean','low','mean_daily'),('HighMean','high','mean_daily')]:
        values[label]=bind(label,'results/tables/volatility_regimes.csv',None,column,100,where={'timing':'predictive','indicator':'AY3M','regime':regime})
    for label,path,row in [('CrisisBase','results/tables/baseline_2008.csv','3M_3_equal'),('CrisisAY','results/tables/conditioned_2008.csv','AY3M'),('CrisisHistorical','results/tables/historical_2008.csv','historical')]:
        values[label]=bind(label,path,row,'terminal_wealth',100,-1)
    # A compact figure using four clearly identified constructions; all 12 remain in the tables and supporting figures.
    r=load('results/timeseries/baseline_returns.csv');r.index=pd.to_datetime(r.index)
    selected=['3M_3_equal','1M_3_equal','1M_2_spread','3M_2_rank']
    wealth=(1+r[selected]).cumprod();dd=wealth/wealth.cummax().clip(lower=1)-1
    plt.rcParams.update({'font.size':8,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
    figure,axes=plt.subplots(2,1,figsize=(7.2,4.5),sharex=True)
    for name in selected:
        axes[0].plot(wealth.index,wealth[name],label=name,linewidth=1)
        axes[1].plot(dd.index,100*dd[name],label=name,linewidth=1)
    for j,name in enumerate(selected):
        expected=np.cumprod(1+r[name].to_numpy())
        np.testing.assert_allclose(axes[0].lines[j].get_ydata(),expected)
        np.testing.assert_allclose(axes[1].lines[j].get_ydata(),100*(expected/np.maximum(1,np.maximum.accumulate(expected))-1))
    (ROOT/'results/validation/report_figure_data_checks.json').write_text(json.dumps({'figure':'review_baseline_paths','series':selected,'observations':len(r),'line_data_reconciled':True},indent=2)+'\n')
    axes[0].set_ylabel('Excess-return index');axes[1].set_ylabel('Drawdown (%)');axes[0].legend(ncol=2,fontsize=7)
    for ax in axes:ax.grid(alpha=.2)
    figure.tight_layout();figure.savefig(ROOT/'results/figures/review_baseline_paths.pdf',bbox_inches='tight');figure.savefig(ROOT/'results/figures/review_baseline_paths.png',dpi=180,bbox_inches='tight');plt.close(figure)
    doc=r'''\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.73in]{geometry}
\usepackage{amsmath,amssymb,booktabs,array,graphicx,float,microtype}
\usepackage[round,authoryear]{natbib}
\usepackage[dvipsnames]{xcolor}
\usepackage[colorlinks=true,linkcolor=MidnightBlue,citecolor=MidnightBlue,urlcolor=MidnightBlue]{hyperref}
\usepackage{fancyhdr}\pagestyle{fancy}\fancyhf{}\lhead{FINC B9339 | Homework 3}\rhead{FX carry}\cfoot{\thepage}
\setlength{\headheight}{14pt}\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlength{\intextsep}{8pt}\renewcommand{\arraystretch}{1.06}
% NUMERICAL_BINDINGS
\begin{document}
\begin{center}{\Large\bfseries FX Carry and Volatility Conditioning}\\[5pt]
Columbia Business School | Systematic Investment Strategies\\
Professor Achilles Venetoulias | Fall 2026\end{center}
\section*{Summary of answers (a)--(e)}
\textbf{(a) Twelve portfolios.} Combine 1M/3M interest rates, two/three currencies on each side,
and equal/rank/median-spread allocation. At each daily close, buy the highest-yield currencies
and short the lowest-yield currencies. Long and short initial USD notionals sum to $+1$ and $-1$;
weights determined at $t$ earn the return from $t$ to the next observation. All 12 dated holdings
are shown in Section 2, and complete daily weights accompany the submission.

\textbf{(b) Baseline comparison.} The highest sample Sharpe is the \textbf{3M, three-per-side,
equal-weight} portfolio: \textbf{@@BaseSharpe@@}. Annual arithmetic/geometric returns are
\textbf{@@BaseArith@@\%/@@BaseGeom@@\%}, volatility \textbf{@@BaseVol@@\%}, and maximum drawdown
\textbf{@@BaseDD@@\%}. Skewness is @@BaseSkew@@ and excess kurtosis @@BaseKurt@@.
Adding a third currency per side has the largest mean absolute paired Sharpe effect
(@@SizeEffect@@ versus @@MethodEffect@@ for weighting and @@TenorEffect@@ for tenor).

\textbf{(c) Volatility relationship.} Carry correlates negatively with changes in all six
volatility indicators. Pearson correlations are @@AYCorr@@ with AY3M changes and @@VixCorr@@
with VIX changes; the latter becomes @@VixCrisis@@ in 2008. \textbf{AY3M} is a reasonable
conditioning candidate: next-day ES rises from @@LowES@@\% in its low regime to @@HighES@@\%
in its high regime. AY1wk is essentially tied on that risk contrast and has unusually stale quotes.
The data support Jurek's qualitative stress relationship, not an estimate of his crash premium.

\textbf{(d) Six filters.} The fixed prior-252-observation 75th-percentile rule selects
\textbf{AY3M} by sample Sharpe: @@CondSharpe@@, versus @@CondBaseSharpe@@ unfiltered on the same
2,727 dates. It is active @@CondActive@@\% of the time, with drawdown @@CondDD@@\% and daily
ES @@CondES@@\%. A constant portfolio with equal average exposure has drawdown @@ConstDD@@\%:
reduced exposure alone does not explain the outcome. However, one additional decision lag
changes the highest-Sharpe filter to AY6M. The winner is timing-sensitive.

\textbf{(e) Historical volatility.} A 21-day AUD/JPY realized-volatility filter has Sharpe
@@HistSharpe@@, versus @@EImpliedSharpe@@ for AY3M and @@EBaseSharpe@@ unfiltered on the common
2,707 dates. Drawdown is @@HistDD@@\%, versus @@CondDD@@\% for AY3M. AY3M wins on point estimates,
but a paired block-bootstrap interval for its Sharpe advantage over the historical filter is
[@@CIDiffLow@@, @@CIDiffHigh@@], which includes zero. Historical filtering loses less during 2008.

\textbf{Scope.} This is an in-sample, zero-cost comparison using 1999--2010 data, not an
out-of-sample ranking. Filtering reduces exposure; it does not purchase option insurance.
\newpage
\section{Data, returns and evaluation conventions}
The CSV contains 2,981 weekday observations from January 1, 1999 through June 4, 2010,
producing 2,980 holding returns. The universe is EUR, JPY, GBP, CAD, AUD, NZD, CHF, NOK and SEK;
USD supplies the matching funding rate. All spot and 20 yield series are complete. Five FX
implied-volatility series are complete, while VIX has 108 missing entries (at most four consecutive).
All supplied rows, including holidays, are retained. AY1wk has a 289-observation constant run
in 2002--2003, a data-quality limitation retained without unsupported corrections.

Yields and FX implied volatilities are annualized percentages; VIX is in percentage points.
The analysis uses the CSV consistently. The accompanying XLSX contains the same spot levels
but some higher-precision yields and volatilities; the two sources are not mixed.

\subsection{Quotation normalization and exact USD excess return}
Let $X_{i,t}$ be USD per unit of foreign currency. EUR, GBP, AUD and NZD already have this
convention; invert JPY, CAD, CHF, NOK and SEK. Arithmetic spot returns are
$s_{i,t+1}=X_{i,t+1}/X_{i,t}-1$. Returns are calculated directly from normalized spot levels at full available precision.
The supplied foreign ROR columns are rounded to four decimal places, with half-unit rounding
tolerance 0.00005, and are not used in the portfolio calculations.
For example, a fall in JPY/USD means yen appreciation and a positive USD-per-yen return.

Quoted yields $p_{i,t}$ are converted to decimals, $y_{i,t}=p_{i,t}/100$, and treated as
continuously compounded daily financing proxies. For actual calendar days divided by 365,
$\Delta_t=(\mathrm{date}_{t+1}-\mathrm{date}_t)/365$,
\begin{align}
x_{i,t+1}&=e^{y_{i,t}\Delta_t}\frac{X_{i,t+1}}{X_{i,t}}-e^{y_{USD,t}\Delta_t},\\
R_{t+1}&=\sum_i w_{i,t}x_{i,t+1}.
\end{align}
A USD of foreign deposit grows at the foreign yield and is converted back at the next spot;
subtract the matched USD funding growth. Signed weights represent lending or foreign borrowing.
The common USD term cancels because $\sum_iw_{i,t}=0$, but foreign interest does not cancel.
The exact decomposition is
\[
x_{i,t+1}=s_{i,t+1}+\left(e^{y_{i,t}\Delta_t}-e^{y_{USD,t}\Delta_t}\right)
+\left(e^{y_{i,t}\Delta_t}-1\right)s_{i,t+1}.
\]
Thus additive spot plus yield differential is only approximate. Baseline annual arithmetic
contributions are @@SpotMean@@\% spot, @@CarryMean@@\% carry and @@InteractionMean@@\% interaction.
One-/three-month rates proxy daily borrowing/lending; no term-deposit mark-to-market is modeled.
The original rate compounding basis is not identified by the dataset. ACT/365 gives three days'
accrual over weekends. Negative yields are allowed.

\subsection{Performance definitions}
Using $N$ daily arithmetic excess returns, sample standard deviation $s_R$ (divisor $N-1$),
and 252 observations per year,
\[
\mu_A=252\bar R,\quad \sigma_A=\sqrt{252}s_R,\quad SR=\sqrt{252}\bar R/s_R,\quad
G_A=\left[\prod_{t=1}^{N}(1+R_t)\right]^{252/N}-1.
\]
Funding is already included: do not subtract USD interest again for Sharpe. Skewness and Fisher
excess kurtosis use bias-corrected sample estimates. With a linear empirical quantile $q_{.05}$,
$VaR_{.05}=-q_{.05}$ and $ES_{.05}=-\operatorname{mean}\{R_t:R_t\le q_{.05}\}$.
For $W_0=1$, $W_t=\prod_{u\le t}(1+R_u)$, drawdown is
$D_t=W_t/\max(1,W_1,\ldots,W_t)-1$ and $MDD=-\min_tD_t$.
Loss VaR/ES/MDD are positive; worst daily returns are signed. Wealth is a compounded
excess-return index, not a cash balance including collateral interest.
\newpage
\section{Daily allocations: answer (a)}
At close $t$, rank the nine foreign yields for each tenor, select the top $k$ and bottom $k$,
$k\in\{2,3\}$, and hold until the next observation. This gives $2\times2\times3=12$ constructions.
Normalize each side separately: long $+1$, short $-1$, gross initial USD notional $2$ per unit
of collateral. Net initial notional zero does not imply zero exposure to all market risk factors.

\textbf{Equal allocation:} each selected currency has absolute weight $1/k$.
\textbf{Rank allocation:} within each side, weights are proportional to $k,k-1,\ldots,1$;
the highest-yield long and lowest-yield short receive the largest absolute weights.
\textbf{Median-spread allocation:} let $m_t$ be the median of all nine foreign yields. Then
\[
w_{i,t}=\frac{y_{i,t}-m_t}{\sum_{j\in L_t}(y_{j,t}-m_t)}\ (i\in L_t),\qquad
w_{i,t}=-\frac{m_t-y_{i,t}}{\sum_{j\in S_t}(m_t-y_{j,t})}\ (i\in S_t).
\]
This adapts Jurek's spread idea to nine foreign currencies; it does not reproduce his
ten-currency center or monthly rebalancing. Alphabetical order breaks tied yields.
Selected spreads must be nonnegative; a zero selected spread receives zero weight,
and an all-zero side falls back to equal allocation. Neither zero-spread event occurs here.
Yield ties occur on 17 dates for 1M and 91 for 3M, so a deterministic tie rule matters.

The table gives decisions at close September 12, 2008, earning the return ending September 15.
It explicitly states all 12 allocations; rounded weights need not sum exactly to one on paper.
Full-precision weights for every decision/holding date and two additional snapshots are supplied.
'''
    h=pd.read_csv(ROOT/'results/tables/representative_holdings.csv');h=h[h.decision_date=='2008-09-12']
    doc+=r'\begin{table}[H]\centering\small\caption{All 12 dated portfolios; E=equal, R=rank, S=median-spread}\begin{tabular}{l >{\raggedright\arraybackslash}p{5.8cm} >{\raggedright\arraybackslash}p{5.8cm}}\toprule Tenor/$k$/method & Long weights & Short weights\\\midrule'+'\n'
    for _,row in h.iterrows():
        tenor,k,method=row.strategy.split('_');label=tenor+'/'+k+'/'+{'equal':'E','rank':'R','spread':'S'}[method]
        doc+=label+' & '+row.longs+' & '+row.shorts+r'\\[4pt]'+'\n'
    doc+=r'\bottomrule\end{tabular}\end{table}'+'\n'
    doc+=r'''
These are dynamic positions. The 1M equal two-per-side portfolio initially buys GBP/NOK and
shorts JPY/CHF; the displayed snapshot instead buys AUD/NZD. The selected baseline is always
short JPY and almost always short CHF, while AUD/NZD are frequent longs. This motivates
AUD/JPY volatility but does not make it a complete risk measure for the changing basket.

\textbf{Timing assumption.} Holdings and yields dated $t$ are used only for $R_{t+1}$.
Same-date observations are assumed available at a common daily fixing; timestamps are not
provided. Portfolio returns begin after the observations used to set holdings, conditional on
this common-fixing assumption. The timing sensitivity analysis below delays both selection
and risk exposure by one additional observation.
\newpage
\section{Baseline performance: answer (b)}
Select the highest sample Sharpe, then higher geometric return, lower ES and lower drawdown
if needed; an alphabetical label resolves an exact remaining tie. This same rule selects
filtered portfolios. The required allocation grid and fixed filter settings are evaluated without an additional
parameter search. The winning labels are nevertheless selected in sample. All baselines use the same 2,980 dates.
'''
    doc+=table(b,[('arithmetic',r'Arith.\%'),('geometric',r'Geom.\%'),('volatility',r'Vol.\%'),('sharpe','Sharpe'),('terminal_wealth','$W_N$')],'All 12 baselines: January 4, 1999--June 4, 2010',percent=['arithmetic','geometric','volatility'])
    doc+=table(b,[('skewness','Skew'),('excess_kurtosis','Ex.kurt.'),('max_drawdown',r'MDD\%'),('worst_day',r'Worst\%'),('var05',r'VaR\%'),('es05',r'ES\%')],r'Baseline risk: daily 5\% VaR/ES and full-path drawdown',percent=['max_drawdown','worst_day','var05','es05'])
    doc+=r'''
The selected baseline has Sharpe @@BaseSharpe@@, geometric return @@BaseGeom@@\%, daily ES
@@BaseES@@\% and drawdown @@BaseDD@@\%. It does not dominate every metric: the
1M/two-per-side/spread portfolio earns geometric return @@SpreadGeom@@\%, but at volatility
@@SpreadVol@@\%, versus @@BaseVol@@\% for the selected portfolio.

All 12 return distributions are negatively skewed and heavy-tailed. The selected portfolio's
worst day is @@BaseWorst@@\%; a Gaussian description would omit economically important crash
exposure. Appendix~\ref{app:figures} presents the full histograms and 2008 portfolio paths.
\newpage
\subsection{Paired design comparisons and the crisis}
Each comparison holds the other two design choices fixed. Averaging absolute Sharpe changes
gives the following descriptive ranking; weighting has three pairwise contrasts per cell.
'''
    doc+=table(load('results/tables/design_dimensions.csv'),[('n_pairs','Pairs'),('mean_absolute_sharpe_difference',r'$|\Delta SR|$'),('mean_absolute_geometric_difference',r'$|\Delta G|$ (pp)')],'Average absolute paired design effects',percent=['mean_absolute_geometric_difference'],rowhead='Dimension')
    doc+=r'''
The number of currencies per side is the largest Sharpe influence. Three per side improves
Sharpe in all six matched comparisons, consistent with lower concentration. Equal allocation
beats rank/spread in all four tenor/size cells. The tenor comparison is mixed: 1M wins four of
six Sharpe pairs; the two leading equal three-per-side portfolios are very close. For geometric
return instead of Sharpe, allocation has the largest paired effect. ``Most influential'' is
therefore metric-dependent rather than a universal structural conclusion.
'''
    doc+=fig('review_baseline_paths',r'Four representative constructions illustrate diversification, concentration and return trade-offs. Appendix~\ref{app:figures} shows complete paths for all twelve portfolios.','3.6in')
    doc+=r'''
All portfolios lose in 2008; calendar compounded losses range from about 18.91\% to 33.48\%.
The chosen baseline returns @@CrisisBase@@\% during that year. Its crisis loss confirms that
interest accrual does not eliminate currency crash risk. Figure~\ref{appfig:baseline_2008}
compares all twelve constructions during the crisis.

Calendar-period return is $W_N-1$, distinct from annualized geometric return. There are 262
supplied weekday observations in 2008, while the stipulated annualization remains 252.
\newpage
\section{Volatility and carry: answer (c)}
\citet{jurek2014} documents negatively skewed carry returns and equity-downside exposure,
then studies option-based crash hedges. His hedged strategies retain positive mean excess
returns, and his estimated crash-risk share is at most about one third of carry compensation.
Those option-price results are not implied by a successful volatility filter. The Barclays framework \citep{barclays2011} motivates
simple systematic risk-premium portfolios and recognizes losses when underlying risks materialize.
These readings motivate a stress hypothesis; they do not establish that this sample must agree.

\subsection{Contemporaneous comovement}
Compute $\operatorname{Corr}(R_t,V_t-V_{t-1})$ using actual raw observations, not imputed
volatility changes. The same 2,769 dates are used for all six indicators (244 in 2008).
Pearson measures linear association; Spearman uses ranks and is less dominated by the largest
changes. Neither is, by itself, a forecast test.
'''
    c=pd.read_csv(ROOT/'results/tables/volatility_correlations.csv');ct=c[c.period=='all'].set_index('indicator');c8=c[c.period=='2008'].set_index('indicator');ct['crisis']=c8.pearson
    doc+=table(ct,[('pearson','Pearson'),('spearman','Spearman'),('crisis','Pearson 2008')],'Same-day carry returns and volatility changes',rowhead='Indicator')
    doc+=r'''
All signs are negative. VIX has the strongest contemporaneous association, @@VixCorr@@ overall
and @@VixCrisis@@ in 2008. JPY3M is the strongest FX measure contemporaneously. This supports
common stress exposure, but not causality or a priced crash premium. VIX is broad 30-day equity
volatility, not Jurek's equity put-writing/downside factor.

\subsection{Decision-date levels and subsequent losses}
At close $t$, compare $V_t$ with terciles of its preceding 252 as-of values; then group
$R_{t+1}$. Low is at/below the lower tercile, high is strictly above the upper tercile.
These relative regimes use no full-sample thresholds and need not have equal counts.
All six comparisons use the same 2,727 dates, December 23, 1999--June 4, 2010.
'''
    rg=pd.read_csv(ROOT/'results/tables/volatility_regimes.csv');pred=rg[rg.timing=='predictive'];z=pred.pivot(index='indicator',columns='regime',values=['mean_daily','es05']);z.columns=['_'.join(x) for x in z.columns];z=z.reindex(['AY1wk','AY3M','AY6M','JPY3M','AUD3M','VIX'])
    doc+=table(z,[('mean_daily_low','Mean low'),('mean_daily_medium','Mean mid'),('mean_daily_high','Mean high'),('es05_low','ES low'),('es05_medium','ES mid'),('es05_high','ES high')],r'Next-day conditional means and 5\% ES, all in daily \%',percent=list(z.columns),rowhead='Indicator')
    doc+=r'''
AY3M's low/high next-day means are @@LowMean@@\%/@@HighMean@@\%, while ES rises from
@@LowES@@\% to @@HighES@@\%. Its high-minus-low ES contrast is the largest, but less than one thousandth of a percentage point above AY1wk's: this is effectively a tie, not reliable statistical
separation. AY3M is a defensible candidate because AUD/JPY links frequent investment/funding
positions and its three-month tenor avoids especially persistent AY1wk quotes. The ES ranking
is exploratory and does not establish out-of-sample forecasting performance.
\newpage
\subsection{Economic interpretation and Jurek comparison}
AY1wk, AY3M and AY6M measure the same AUD/JPY cross over different horizons. A longer tenor
may smooth near-term noise but may react differently to a sudden shock. JPY3M relates to the
persistent yen funding short; AUD3M relates to a frequent investment currency. VIX captures
broader equity stress. None spans all changing NZD, NOK, CHF, CAD and other exposures.

High observed volatility can mark persistent stress and larger subsequent losses, while rising
volatility can simply accompany a loss already realized. The distinction explains why VIX's
strong same-day correlation need not produce the best next-day filter. Figure~\ref{appfig:predictive_regime_distributions}
compares subsequent return distributions across the observed regimes.
'''
    doc+=fig('stress_2008','2008: unfiltered and AY3M-filtered wealth, the five FX implied volatilities, and VIX. The filtered strategy remains exposed until the risk signal switches off.','3.9in')
    doc+=r'''
\textbf{Do the data confirm Jurek?} They support the qualitative stress relationship:
negative baseline skewness (@@BaseSkew@@), excess kurtosis (@@BaseKurt@@), a large 2008 loss,
and negative contemporaneous FX/equity-volatility correlations. They do not reproduce his
option-hedging or risk-premium result. Jurek uses monthly rebalancing, a different sample
(1990--2012), and actual options; this study uses daily positions and no option payoffs.
His Section 5.4.1 compares risk-neutral and realized moments. Our filtered-return difference
cannot identify either a variance risk premium or the fraction of carry compensation due to crashes.

\section{Fixed volatility filters: answer (d)}
For each indicator, define
\[
q_t=Q_{.75}(V_{t-252},\ldots,V_{t-1}),\qquad z_t=\mathbf{1}\{V_t\le q_t\},
\qquad R^{(V)}_{t+1}=z_tR_{t+1}.
\]
Lookback, percentile and exposure levels (one/zero) are fixed, not optimized. Risk-off earns
zero excess return. Percentiles are linear-interpolated and exclude $V_t$.
Missing volatility is forward-filled only after its first observation; the window counts
252 prior as-of values, including carried VIX values. No spot/yield imputation or partial
warm-up is used. All six filters and benchmark share the same 2,727-date evaluation window.
\newpage
\subsection{All six conditioned return distributions}
'''
    doc+=table(d,[('arithmetic',r'Arith.\%'),('geometric',r'Geom.\%'),('volatility',r'Vol.\%'),('sharpe','Sharpe'),('active_fraction',r'Active\%')],'Conditioned strategies: common-period central performance',percent=['arithmetic','geometric','volatility','active_fraction'])
    doc+=table(d,[('skewness','Skew'),('excess_kurtosis','Ex.kurt.'),('max_drawdown',r'MDD\%'),('worst_day',r'Worst\%'),('es05',r'ES\%')],'Conditioned strategies: shape and downside risk',percent=['max_drawdown','worst_day','es05'])
    doc+=r'''
AY3M wins under the same Sharpe criterion used for the baseline. It agrees with the exploratory
part (c) candidate, but agreement was not guaranteed: part (c) compares tercile risk contrasts,
whereas the trading rule switches at the 75th percentile. AUD3M has smaller daily ES and volatility
than AY3M, so the selected winner is not best on every risk measure.

Filtering improves loss magnitudes but does not eliminate asymmetry. AY3M skewness
(@@CondSkew@@) is more negative than unfiltered skewness (@@CondBaseSkew@@) on this sample.
Zero-return risk-off days alter unconditional quantiles and create a point mass at zero;
standardized moments need not improve when drawdowns fall.

The winning filter still skips @@OffProfits@@ profitable days. Compounding all skipped-day
carry returns gives @@OffCompound@@\%; that realized negative total explains why switching off
helped here, not why it must help in the future. No additional leverage restores the lost
average exposure. During 2008, AY3M returns @@CrisisAY@@\%, versus @@CrisisBase@@\% unfiltered;
it protects imperfectly and does not win every subperiod.

Comparing all six indicators is necessary because contemporaneous association, predictive risk
separation, and the payoff of a particular switch-off threshold are different questions.
Common, untuned parameters make the comparison interpretable. Selecting the best of six after
observing results still creates selection bias.

\textbf{Filtering versus insurance.} This rule can remain invested before a sudden shock,
react after losses, and re-enter when historical thresholds adapt to elevated absolute risk.
It buys no put and guarantees no loss floor. It is therefore not Jurek's crash-neutral overlay.
\newpage
\subsection{Exposure controls, timing and statistical uncertainty}
A constant reference with exposure $p=\operatorname{mean}(z_t)$ has returns $pR_t$.
Positive constant scaling leaves Sharpe unchanged. Its exposure level is measured ex post,
so it serves as a descriptive benchmark rather than an implementable trading rule. A second reference
scales the baseline to the filter's realized volatility. Both controls use the same dates.
'''
    doc+=table(controls,[('filtered_drawdown',r'Filter MDD\%'),('constant_drawdown',r'Equal-$p$ MDD\%'),('volmatched_drawdown',r'Equal-vol MDD\%'),('active_es05',r'Active-day ES\%')],'Downside protection beyond uniform exposure reduction',percent=['filtered_drawdown','constant_drawdown','volmatched_drawdown','active_es05'],rowhead='Indicator')
    doc+=r'''
For AY3M, uniform average-exposure scaling gives drawdown @@ConstDD@@\%, and matching realized
volatility gives @@VolMatchDD@@\%, both above the filter's @@CondDD@@\%. ES restricted to active
days is @@ActiveES@@\%. Thus the primary sample contains useful timing beyond merely taking
less exposure, although an ex-post control does not establish a causal or future timing premium.

The dataset lacks common-fixing timestamps. The timing sensitivity analysis delays \emph{both}
currency selection and the risk-exposure decision by one further observation, retaining funding
rates known at the holding period's start. Primary and delayed rules below share 2,726 dates
from December 24, 1999. The additional lag is fixed in advance and is not optimized.
'''
    lt=pd.DataFrame(index=['AY1wk','AY3M','AY6M','JPY3M','AUD3M','VIX'])
    lt['primary']=[lag.loc[v+'_primary','sharpe'] for v in lt.index];lt['lagged']=[lag.loc[v+'_lagged','sharpe'] for v in lt.index]
    doc+=table(lt,[('primary','Primary Sharpe'),('lagged','Extra-lag Sharpe')],'Additional lag on both selection and exposure',rowhead='Indicator')
    doc+=r'''
AY3M falls from @@LagPrimaryAY@@ to @@LagAY@@, while AY6M reaches @@LagSix@@ and becomes the
winner. The lagged unfiltered benchmark has Sharpe @@LagBase@@. The broad filtering benefit
persists under the additional lag, but the exact winning indicator changes.
'''
    doc+=table(ci,[('delta_sharpe',r'$\Delta SR$'),('ci_low',r'95\% lower'),('ci_high',r'95\% upper')],'Paired moving-block bootstrap: filter minus baseline Sharpe',rowhead='Indicator')
    doc+=r'''
Intervals resample paired realized return vectors in 20-observation blocks, with 2,000 draws
and seed 9339. They are pointwise, conditional on the selected baseline and realized rules;
thresholds and the selection procedure are not re-estimated. AY3M's interval is
[@@CICondLow@@, @@CICondHigh@@], but it is not corrected for choosing among 12 baselines and
six filters. These intervals do not establish out-of-sample significance or superiority.
\newpage
\section{Historical versus implied volatility: answer (e)}
Construct AUD/JPY in yen per AUD using the supplied market quotations:
\[
C_t=(USD/AUD)_t(JPY/USD)_t=AUD_t\,JPY_t,\quad u_t=C_t/C_{t-1}-1,
\quad H_t=\sqrt{252}\operatorname{sd}(u_{t-20},\ldots,u_t).
\]
The 21-return sample standard deviation has divisor 20. $H_t$ includes the close-$t$ return
and can condition only $R_{t+1}$. The cross return is computed directly, not approximated by
subtracting arithmetic USD returns. This proxy represents a frequent carry pair but omits
other currencies and the full covariance of actual holdings.

Apply exactly the same prior-252-value 75th-percentile rule. After the realized-volatility
warm-up, all three strategies share January 20, 2000--June 4, 2010, or 2,707 return dates.
The best FX-implied filter is AY3M; it also happens to win among all six indicators including VIX.
'''
    doc+=table(e,[('arithmetic',r'Arith.\%'),('geometric',r'Geom.\%'),('volatility',r'Vol.\%'),('sharpe','Sharpe'),('active_fraction',r'Active\%')],'Historical comparison: identical evaluation dates',percent=['arithmetic','geometric','volatility','active_fraction'])
    doc+=table(e,[('skewness','Skew'),('excess_kurtosis','Ex.kurt.'),('max_drawdown',r'MDD\%'),('worst_day',r'Worst\%'),('var05',r'VaR\%'),('es05',r'ES\%')],'Historical comparison: complete distributional risk',percent=['max_drawdown','worst_day','var05','es05'])
    doc+=fig('historical_distributions','Unconditional daily distributions, including zero-exposure days, and the lower-tail empirical CDF on the common sample.','2.6in')
    doc+=r'''
Historical filtering improves risk-adjusted performance relative to unfiltered carry. AY3M's
point estimates are better for Sharpe, drawdown and ES (@@EImpliedES@@\% versus @@HistES@@\%).
Historical skewness (@@HistSkew@@) is less negative than AY3M's (@@EImpliedSkew@@), and its
2008 return (@@CrisisHistorical@@\%) exceeds AY3M's (@@CrisisAY@@\%). The comparison therefore
contains trade-offs, not uniform dominance.
\newpage
\subsection{Information content and limits}
'''
    doc+=fig('historical_wealth','Compounded excess-return indices for the three strategies on the common historical comparison sample.','2.5in')
    doc+=r'''
Implied volatility reflects option prices over a future horizon under a risk-neutral measure;
it can contain insurance premia and market frictions rather than a pure physical forecast.
Realized volatility summarizes past physical spot movements. A 21-day measure can react only
after a shock enters its window, but repeated shocks may make it a useful persistent risk signal.
A forward-looking label alone does not guarantee better investment performance.

Here AY3M has the better point-estimate Sharpe, but the paired block-bootstrap interval for
AY3M minus historical Sharpe is [@@CIDiffLow@@, @@CIDiffHigh@@]. It includes zero even before
accounting for model selection. A three-month implied horizon and a 21-day realized window
also differ, so this is not a controlled identification of the value of implied information.
Both filters use relative thresholds and imperfect AUD/JPY risk coverage.

Jurek's implied-versus-realized-moment analysis motivates these distinctions. No option payoff,
option-implied skewness surface, matched variance claim, or equity downside index is available
here; the filtered return difference cannot recover his variance or crash-risk premium.

\section{Conclusion}
The preferred baseline is diversified equal-weight daily carry, but every construction retains
substantial crash exposure. All six volatility filters improve sample Sharpe under the primary
convention; AY3M has the highest point estimate. Exposure-matched controls support a timing
benefit in this sample, while timing sensitivity and the uncertain implied-versus-historical difference
limit claims about a unique winner. These findings support Jurek's qualitative stress evidence
without reproducing his option-hedging conclusions.

The conclusions depend on the assumed availability of spot rates, yields and volatility at a
common daily fixing. Transaction costs are excluded as stipulated by the assignment, and all
strategy selections remain in sample. The results therefore describe historical risk--return
trade-offs rather than a demonstrated out-of-sample investment advantage.
Appendix~\ref{app:figures} provides the complete graphical comparisons.

\bibliographystyle{plainnat}\bibliography{references}
\end{document}
'''
    from .appendix import latex as appendix_latex
    doc=doc.replace(r'\end{document}', appendix_latex()+r'\end{document}')
    for label,macro in values.items():doc=doc.replace('@@'+label+'@@',macro)
    if '@@' in doc:raise ValueError('Unresolved result binding')
    CLAIMS[:]=[c for c in CLAIMS if ('\\r'+c['label']+'{}') in doc]
    definitions='\n'.join(r'\newcommand{\r'+c['label']+'}{'+c['formatted']+'}' for c in CLAIMS)
    doc=doc.replace('% NUMERICAL_BINDINGS',definitions)
    (ROOT/'report/main.tex').write_text(doc)
    (ROOT/'report/numerical_claims.json').write_text(json.dumps(CLAIMS,indent=2)+'\n')
    print('Generated report with',len(CLAIMS),'source-bound numerical claims.')

if __name__=='__main__':main()
