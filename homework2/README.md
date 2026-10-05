# Homework 2 — Momentum investing

Hanyu Zhang · Columbia FINCB9339 · Fall 2026

Two reproducible research prototypes: (A) crash-aware exposure overlays on Kenneth French's aggregate equity momentum factor and (B) cross-asset ETF relative/absolute momentum with optional volatility control. The ETF universe is SPY, EFA, EEM, IEF, TLT, GLD, DBC and VNQ. WRDS/CRSP was not used.

## Final reading order

1. [Investor presentation PDF](Investor_Presentation.pdf): the updated October 5 LaTeX presentation.
2. [Editable LaTeX presentation source](Investor_Presentation_Source/Investor_Presentation.tex), [speaker notes](Investor_Presentation_Source/Presenter_Notes.md), and [presentation build instructions](Investor_Presentation_Source/README.md).
3. [Technical report PDF](hw2_momentum/deliverables/HW2_Momentum_Research_Report.pdf) or [editable report](hw2_momentum/deliverables/HW2_Momentum_Research_Report.md).
4. [Research project README](hw2_momentum/README.md), [executed factor notebook](hw2_momentum/notebooks/01_factor_overlay.ipynb), and [executed ETF notebook](hw2_momentum/notebooks/02_etf_dual_momentum.ipynb).
5. [Acceptance checklist](hw2_momentum/research/acceptance_checklist.md), [exact performance table](hw2_momentum/outputs/tables/performance.csv), [robustness ledger](hw2_momentum/outputs/tables/variant_ledger.csv), and [data provenance](hw2_momentum/data/manifests/inputs.json).

The original October 4 slide manuscript/PDF remain inside `hw2_momentum/deliverables/` as research-stage artifacts. The updated presentation and editable LaTeX source above are the preferred deck. Statements about a missing PPTX in the original package describe that original delivery; editable LaTeX is now available.

## Repository layout

```text
homework2/
├── README.md
├── hw2.md                            Assignment requirements
├── HW2_Momentum_Agent_Spec.md        Original execution specification
├── Investor_Presentation.pdf        Updated presentation
├── Investor_Presentation_Source/    Editable LaTeX, charts, generated tables, notes
└── hw2_momentum/                    Python research project
    ├── config/                     Frozen primary settings
    ├── src/                        Shared backtest modules
    ├── tests/                      Targeted validation tests
    ├── scripts/                    Reproduction / audit / notebook tools
    ├── notebooks/                  Two executed explanatory notebooks
    ├── data/manifests/              Acquisition metadata and input checksums
    ├── outputs/                    Canonical tables, audits and actual-result charts
    ├── research/                   Sources, freeze, limitations and acceptance
    └── deliverables/               Technical report and original investor artifacts
```

## Research result and limits

Recommend B3 as a research-stage risk-limited ETF pitch, not as a proven superior-return product. On the primary sample its modeled net CAGR is 6.89%, monthly cash-adjusted Sharpe 0.614 and maximum daily drawdown −17.91%; average cash is 22.82%. B1 has higher CAGR (8.66%); monthly 60/40 has higher Sharpe (0.719). Uncertainty intervals do not establish superiority, and liquidity/cost assumptions do not establish live capacity.

The cutoff was September 30, 2026, but French Mom/RF inputs stop August 31. Primary invested-return samples: factor February 1, 1990–August 31, 2026; ETFs September 4, 2007–August 31, 2026. Historical holdout results are publicly known historical evidence, not unseen future performance. Full explanations, adverse variants and actual verification records are retained.

## Reproduction and input availability

From the repository root:

```sh
cd homework2/hw2_momentum
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
export PYTHONPATH="$PWD/src"
export MPLCONFIGDIR="$PWD/build/matplotlib"
.venv/bin/python -m pytest -q
.venv/bin/python -m momentum_hw2.cli fetch --config config/base.yaml
.venv/bin/python -m momentum_hw2.cli validate-data --offline
.venv/bin/python -m momentum_hw2.cli run --offline
.venv/bin/python -m momentum_hw2.cli report --offline
```

**Original raw and processed vendor input caches are retained locally and intentionally excluded from Git.** This repository includes acquisition manifests, recorded hashes, source code, executed notebooks, and derived research outputs. A new clone must acquire inputs or receive an authorized copy of the original caches before running a backtest. Fresh provider downloads are a new vintage and may revise data or extend the endpoint; they are not guaranteed to reproduce the original hashes or headline results. Preserve the committed manifests/outputs before fetching a new vintage, preferably in a separate checkout. The original cached clean-run record reports 137 identical numerical outputs, 11 passing tests and 25 independent accounting checks.

To rebuild the updated presentation, follow `Investor_Presentation_Source/README.md`. Its default relative CSV path is preserved by this layout. Excluded items include virtual environments, dependency caches, rendering scratch, duplicated ZIPs and TeX build intermediates. No data charges, trades, publishing beyond this requested Git repository update, or homework submissions are part of the project.

The original `PACKAGE_SHA256.json`, freeze files and run logs are historical records of the October 4 research delivery, not checksums of this reorganized Git checkout. Repository README edits and the later presentation do not alter frozen strategy inputs.
