# Change log

## Version 2 (October 5, 2026): submission version
- Reframed as a formal investor pitch. Removed all course and assignment references from slides, footer, PDF metadata and file names (`Investor_Presentation.tex/.pdf`).
- Removed the "Read honestly" box and the WRDS roadmap slide. CRSP reconciliation remains as one next step on slide 12.
- More persuasive structure: the opening slide now leads with four key figures (max drawdown, 2022 return, CAGR ÷ max drawdown, CAGR), followed by strategy, investor benefit and the ask.
- New metrics, all from `performance.csv` and `stress_periods.csv`: worst month, worst three months, CAGR ÷ |max daily drawdown|, and 2008–09, 2020 and 2022 stress rows. These come from existing outputs; no new backtests were run.
- Titles state the conclusion (for example, "B3 has the shallowest drawdown and the best return per unit of drawdown").
- Slide 3 presents the factor study as research foundation; slide 12 adds a risk-and-mitigant table and next steps.
- Disclosures are kept but shortened: 60/40's higher Sharpe, the 2014–2019 underperformance, the 2020 lag, the bootstrap interval, the inspected 2020–2026 period, GLD dependence and the non-adopted 9-month rule.
- Appendix is now 8 slides: factor construction, factor results and chart, accounting, B3 exposure, five-decimal table, references, reproducibility.

## Version 1
- Rebuilt the original presentation as a LaTeX Beamer deck generated from the canonical CSVs, with checks that fail the build if headline values drift.
