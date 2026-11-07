# Assignment coverage

| Requirement | Evidence | Assessment |
|---|---|---|
| First-page answers, formulas, at least five decimal places | Report page 1; pages 3–8 | Complete |
| (a) Data ending June 30, 2026 and starting before 2011 | Frozen JSON, manifest, data-quality table, report page 2 | Complete |
| Four modules, at least two risky assets and one common safe alternative | VTI/EFA; HYG/LQD; VNQ/REM; GLD/TLT; SHV throughout | Complete; proxy differences disclosed |
| Month-end total-return observations and data-cleaning choices | src/data.py, daily/monthly adjusted closes, report page 2 | Complete; no imputation |
| Preferably include 2007–2009 and ideally full 2000–2009 | Raw REM begins May 2007; first holding return June 2008 | Partial preferred history; full optional comparison unavailable and not claimed |
| (b) Self-contained implementation including collected data | research_project.zip, README, source, raw inputs and results | Complete |
| Same 12-month criterion, most recent month included | Scores, unit tests, report page 3 | Complete |
| Same module allocation as paper | Four 25% sleeves, monthly rebalancing | Complete |
| No factor-model alpha comparisons required | Omitted | Permitted |
| (c) Critical findings versus paper | Report pages 4–7; paper Table 10, module ablations, subsamples, distributions, costs and uncertainty | Complete; samples labelled separately |
| (d) Suggest and show an improvement | Fixed 2pp switching buffer, cost table and appendix D | Complete; turnover improvement shown, superiority not established |
| No look-ahead in monthly returns | Prior decision month, scalar reconstruction and future-data perturbations | Complete computational alignment; month-end execution idealization disclosed |
| All graphs submitted together | Report appendix A–D contains all five figures | Complete |
| Reproducible environment | Existing shared interpreter, dependency records, offline inputs | Complete; no local virtual environment |

The handout labels November 9, 2026 as Thursday; the calendar date is Monday. This discrepancy is recorded without assuming an alternative deadline.
