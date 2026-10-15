# Homework 2: momentum investing

Hanyu Zhang · Columbia FINCB9339 · Fall 2026

Two research prototypes: (A) crash-aware exposure overlays on the Kenneth French
aggregate momentum factor and (B) cross-asset ETF relative/absolute momentum with
volatility control. This folder contains the complete project report, investor
presentation, source code, preserved results and reproduction instructions.

## Start here

1. [Complete project report](submission/HW2_Hanyu_Zhang_FINCB9339.pdf) and
   [editable LaTeX source](report/project/main.tex)
2. [Preferred investor presentation](submission/Investor_Presentation.pdf)
3. [Editable presentation](report/presentation/Investor_Presentation.tex),
   [speaker notes](report/presentation/Presenter_Notes.md), and
   [presentation build instructions](report/presentation/README.md)
4. [Original technical report PDF](submission/HW2_Momentum_Research_Report.pdf) and
   [editable research report](report/HW2_Momentum_Research_Report.md)
5. [Detailed research guide](docs/RESEARCH_GUIDE.md),
   [factor notebook](notebooks/01_factor_overlay.ipynb), and
   [ETF notebook](notebooks/02_etf_dual_momentum.ipynb)
6. [Acceptance checklist](docs/research/acceptance_checklist.md),
   [performance table](results/tables/performance.csv), and
   [input provenance](data/manifests/inputs.json)

The original October 4 presentation is retained in `submission/archive/`, with
its manuscript/JSON under `report/original_presentation/`. The updated October 5
LaTeX presentation above remains the preferred deck. The original technical report
is retained as a distinct research record; the new project report is the main narrative write-up.

## Structure

```text
homework2/
  config/                Frozen primary settings
  data/manifests/        Acquisition metadata and original input checksums
  src/momentum_hw2/      Factor/ETF models, data handling and reporting
  tests/                 Targeted correctness tests
  scripts/               Audits, notebooks, cached reproduction and packaging
  notebooks/             Existing executed explanatory notebooks
  results/tables/        Preserved returns, statistics and robustness comparisons
  results/audits/        Preserved decisions, holdings, costs and checks
  results/figures/       Actual-result charts
  report/                Editable technical report and presentation source
  docs/research/         Frozen plan, sources, limitations and acceptance
  docs/provenance/       Historical package checksum record
  references/            Assignment requirements
  submission/            Final PDFs; archive/ holds the original presentation
  pyproject.toml         Dependency metadata and pytest source paths
  requirements.lock.txt  Historical dependency snapshot, not a synchronization target
```

`results/structure_manifest.json` records all original/new paths and file hashes.
Historical manifests, freeze records and logs remain unchanged, including paths
from their original layout. The handoff checker resolves the frozen research-plan
path to `docs/research/` without modifying the freeze or plan.

## Shared environment and validation

Use only `$HOME/.venvs/sys-inv/bin/python`. Do not create a homework-local `.venv`
or `venv`, run `uv sync`, or replace shared packages to match the historical lock
file. Install only missing packages with
`uv pip install --python "$HOME/.venvs/sys-inv/bin/python" <packages>`.
See the course [environment policy](../AGENTS.md).

From this homework root:

```sh
"$HOME/.venvs/sys-inv/bin/python" -c 'import sys; print(sys.executable)'
export PYTHONPATH="$PWD/src${PYTHONPATH:+:$PYTHONPATH}"
export MPLCONFIGDIR="$PWD/build/matplotlib"
"$HOME/.venvs/sys-inv/bin/python" -m pytest -q
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli --help
```

**The original raw and processed vendor caches are absent from this checkout.**
They were intentionally excluded from Git. Existing manifests and results are
preserved; no replacement data were downloaded during restructuring. The unit
tests use synthetic fixtures and can run without these caches. Full offline
backtests and notebook execution require authorized original files in `data/raw/`
and `data/processed/` matching the recorded input hashes.

Once those caches are restored, these commands run from the same root:

```sh
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli validate-data --offline
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli run --offline
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli report --offline
```

A new provider download is a new data vintage and may revise the original
results. Preserve manifests/results before any future authorized acquisition.
The original research records report 137 identical numerical outputs, 11 passing
tests and 25 independent accounting checks; those records are historical evidence,
not a claim that a cache-dependent run was repeated during restructuring.

Notebook source paths and kernel metadata now use the new layout and shared
course interpreter. Original execution outputs are preserved; the notebooks were
not re-executed without their missing input caches. Notebook builders/runners
create only project-local Jupyter runtime files, never a Python environment.

## Findings and limits

B3 remains the research-stage risk-limited ETF pitch: modeled net CAGR 6.89%,
monthly cash-adjusted Sharpe 0.614, maximum daily drawdown −17.91%, and average
cash 22.82%. B1 has higher CAGR (8.66%); monthly 60/40 has higher Sharpe (0.719).
Uncertainty intervals do not establish superiority, and assumed costs and
vendor-volume proxies do not establish live capacity.

The cutoff was September 30, 2026; observed French RF/Mom inputs end August 31.
Primary invested-return samples are February 1, 1990–August 31, 2026 for factors
and September 4, 2007–August 31, 2026 for ETFs. Known historical holdout results
are not unseen future evidence. Costs, capacity, data adjustments and limitations
remain documented in the detailed research guide and report. No trades or
assignment submissions were performed.

## Complete narrative project report

`submission/HW2_Hanyu_Zhang_FINCB9339.pdf` is the comprehensive 11-page
companion report, organized as an academic write-up: first-page summary, economic
context, data, all A/B strategies, mathematical rules and timing, portfolio
accounting, performance/distributions, robustness, capacity, investor questions,
limitations and reproduction. The investor deck remains the assignment's pitch.
The original technical PDF and Markdown report remain unchanged.

Build the new report from this project root without downloading data:

```sh
"$HOME/.venvs/sys-inv/bin/python" scripts/build_project_report.py
cd report/project
tectonic --keep-logs main.tex
cp main.pdf ../../submission/HW2_Hanyu_Zhang_FINCB9339.pdf
```

A standard LaTeX installation can use `pdflatex main.tex` twice instead of
Tectonic. The builder uses NumPy/pandas and reconciles 65 primary statistics
against the preserved daily/monthly CSVs across 11 variants, including capital
NAV and ETF average exposure checks. The verification record is
`results/audits/project_report_verification.json`; all 11 synthetic unit tests
also passed during report preparation. This is saved-output reconciliation,
not a cache-dependent backtest rerun. The shared interpreter policy above applies.
