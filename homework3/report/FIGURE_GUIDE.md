# HW3 figures: integrated submission report

Submit `submission/HW3_Hanyu_Zhang_FINCB9339.pdf`: the main text and appendix now form one
complete write-up, with every graph appearing once. Main text: compact baseline
paths, 2008 stress, historical-comparison distributions and wealth.

## Appendix A

- Figure A.1: **All twelve baseline wealth paths** (`baseline_wealth`). Daily compounded excess-return indices over the full 2,980-return baseline sample. The complete paths complement the representative constructions in the main text.

- Figure A.2: **All twelve baseline drawdown paths** (`baseline_drawdowns`). Losses relative to previous wealth peaks, including initial wealth one, over the same baseline sample. Drawdowns here are signed fractions; reported maximum drawdown statistics are positive loss percentages.

- Figure A.3: **All twelve baseline return distributions** (`baseline_distributions`). Daily arithmetic excess-return histograms with log density. Shared plotted bins emphasize differences across portfolios; exported moments and tail statistics use every observation, including any extreme outside these bins.

- Figure A.4: **Baseline portfolios during 2008** (`baseline_2008`). Calendar-2008 compounded excess-return indices for all twelve constructions, rebased at the start of the episode. Crisis returns remain included in the full-sample comparisons.

- Figure A.5: **Carry and contemporaneous volatility changes** (`volatility_scatter`). Baseline daily carry returns versus same-period changes in all six volatility indicators. This describes contemporaneous co-movement, rather than a forecast available before the return.

- Figure A.6: **Subsequent returns by observed volatility regime** (`predictive_regime_distributions`). Next-period baseline carry returns grouped by previously observed low, medium and high volatility regimes for each indicator. Outlier markers are suppressed for legibility; tail observations remain in the regime statistics.

- Figure A.7: **All six volatility-conditioned wealth paths** (`conditioned_wealth`). The baseline and all six fixed-rule filters share the 2,727-date eligible sample. Thresholds use the preceding 252 observations and exposure decisions apply to subsequent returns; inactive FX positions earn zero excess return.

- Figure A.8: **All six volatility-conditioned drawdown paths** (`conditioned_drawdowns`). Drawdowns on the same six-filter comparison sample. Reduced market exposure contributes to protection; the main text separately compares exposure-matched and volatility-matched controls.

- Figure A.9: **Historical versus implied conditioning: drawdowns** (`historical_drawdowns`). The baseline, AY3M-implied filter and 21-day AUD/JPY realized-volatility filter use identical 2,707 evaluation dates. The main text provides the corresponding wealth and distribution figures and uncertainty comparison.

## Preservation

All 12 original PNGs remain byte-identical to the pre-review archive; original
PDF drawing streams are unchanged. See `figure_preservation.json`. The thirteenth
figure is the compact baseline comparison. Every figure appears in the final
report; the redundant standalone supplement has been removed.

The report builder includes `src/appendix.py` automatically. Run the normal
README report generation, compilation, validation, visual review and packaging
sequence to reproduce the integrated report.
