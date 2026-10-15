# HW2 deliverables

- `HW2_Hanyu_Zhang_FINCB9339.pdf`: complete 11-page narrative project report, including first-page answers, mathematical rules, both experiments, results, risk, robustness, feasibility and reproduction. Editable source: `../report/project/main.tex`; builder: `../scripts/build_project_report.py`.
- `Investor_Presentation.pdf`: preferred investor pitch, the presentation requested by the assignment. Editable source: `../report/presentation/Investor_Presentation.tex`.
- `HW2_Momentum_Research_Report.pdf`: preserved original technical report.
- `archive/HW2_Investor_Presentation.pdf`: preserved earlier presentation.

Verification: 11 current unit tests pass; 65 independent primary metric reconciliations against saved return series pass; all 11 narrative-report pages visually checked. See `../results/audits/project_report_verification.json` and `project_report_visual_review.json`. Original raw/processed caches are absent, so a fresh data-to-results backtest was not rerun.
