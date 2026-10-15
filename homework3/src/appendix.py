"""Additional figures included in the single submission report, without duplicates."""
FIGURES = [
    ('baseline_wealth', 'All twelve baseline wealth paths',
     'Daily compounded excess-return indices over the full 2,980-return baseline sample. The complete paths complement the representative constructions in the main text.'),
    ('baseline_drawdowns', 'All twelve baseline drawdown paths',
     'Losses relative to previous wealth peaks, including initial wealth one, over the same baseline sample. Drawdowns here are signed fractions; reported maximum drawdown statistics are positive loss percentages.'),
    ('baseline_distributions', 'All twelve baseline return distributions',
     'Daily arithmetic excess-return histograms with log density. Shared plotted bins emphasize differences across portfolios; reported moments and tail statistics use every observation, including any extreme outside these bins.'),
    ('baseline_2008', 'Baseline portfolios during 2008',
     'Calendar-2008 compounded excess-return indices for all twelve constructions, rebased at the start of the episode. Crisis returns remain included in the full-sample comparisons.'),
    ('volatility_scatter', 'Carry and contemporaneous volatility changes',
     'Baseline daily carry returns versus same-period changes in all six volatility indicators. This describes contemporaneous co-movement, rather than a forecast available before the return.'),
    ('predictive_regime_distributions', 'Subsequent returns by observed volatility regime',
     'Next-period baseline carry returns grouped by previously observed low, medium and high volatility regimes for each indicator. Outlier markers are suppressed for legibility; tail observations remain in the regime statistics.'),
    ('conditioned_wealth', 'All six volatility-conditioned wealth paths',
     'The baseline and all six fixed-rule filters share the 2,727-date eligible sample. Thresholds use the preceding 252 observations and exposure decisions apply to subsequent returns; inactive FX positions earn zero excess return.'),
    ('conditioned_drawdowns', 'All six volatility-conditioned drawdown paths',
     'Drawdowns on the same six-filter comparison sample. Reduced market exposure contributes to protection; the main text separately compares exposure-matched and volatility-matched controls.'),
    ('historical_drawdowns', 'Historical versus implied conditioning: drawdowns',
     'The baseline, AY3M-implied filter and 21-day AUD/JPY realized-volatility filter use identical 2,707 evaluation dates. The main text provides the corresponding wealth and distribution figures and uncertainty comparison.'),
]


def latex():
    out = r"""
\clearpage
\appendix
\section{Additional graphical evidence}\label{app:figures}
The following figures complete the graphical comparisons for answers (b)--(e).
All twelve baseline constructions and all six volatility filters are shown.
The wealth, distribution and stress figures already in the main text are not repeated.
Return conventions and evaluation samples are the same as in the corresponding tables.
\setcounter{figure}{0}
\renewcommand{\thefigure}{A.\arabic{figure}}
\renewcommand{\theHfigure}{appendix.\arabic{figure}}
"""
    for i, (name, title, note) in enumerate(FIGURES):
        if i:
            out += r'\clearpage' + '\n'
        out += (r'\begin{figure}[H]\centering'
                r'\includegraphics[width=\linewidth,height=6.2in,keepaspectratio]{../results/figures/'
                + name + r'.pdf}\caption{\textbf{' + title + '.} ' + note
                + r'}\label{appfig:' + name + r'}\end{figure}' + '\n')
    return out
