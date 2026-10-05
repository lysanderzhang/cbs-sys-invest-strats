# FINCB9339 Homework 2: controlled momentum experiments

Hanyu Zhang. Research cutoff **September 30, 2026**. Due **October 5, 2026 at 5:00 p.m. America/New_York**, per user instruction. Neither trades nor submission performed.

## Git repository edition

This project is now under `homework2/hw2_momentum/`. See [Homework 2 README](../README.md) for the updated October 5 editable LaTeX investor presentation and repository input policy. Raw/processed input caches, the virtual environment and build scratch are excluded from Git; a fresh clone needs authorized original caches or a new provider acquisition before offline backtests can run. New downloads may revise the data vintage. Existing historical outputs and verification logs are retained unchanged.

## Start with the deliverables

- [Technical report](deliverables/HW2_Momentum_Research_Report.md) and [report PDF](deliverables/HW2_Momentum_Research_Report.pdf).
- [Presentation PDF](deliverables/HW2_Investor_Presentation.pdf): 12 substantive slides plus five appendix slides.
- [Editable slide manuscript with speaker notes](deliverables/HW2_Investor_Presentation_Manuscript.md) and [structured slides](deliverables/slides.json).
- [Executed factor notebook](notebooks/01_factor_overlay.ipynb) and [executed ETF notebook](notebooks/02_etf_dual_momentum.ipynb).
- [Acceptance checklist](research/acceptance_checklist.md), [data quality](research/data_quality.md), [requirements map](research/requirements_matrix.md), [source map](research/source_map.md), [research freeze](research/freeze.json).
- Exact numeric evidence: [performance](outputs/tables/performance.csv), [sensitivities](outputs/tables/sensitivities.csv), [bootstrap](outputs/tables/bootstrap.csv), [capacity](outputs/tables/capacity_summary.csv), [all evaluated variants](outputs/tables/variant_ledger.csv).

**Presentation format limitation:** the installed presentation skill requires `load_workspace_dependencies` and `@oai/artifact-tool`; neither capability/package is available in this runtime. The native Microsoft PowerPoint fallback returned “Can't make class presentation” (-2710); computer control reported `noWindowsAvailable`. No PPTX is claimed. The specification's explicit fallback is delivered: a complete editable manuscript/JSON with notes and a shareable slide PDF. Artifact formatting markers were executed successfully; PDF generation/rendering uses ReportLab/PyMuPDF. Rendered chart PNGs and their underlying CSV data are included for future deck editing.

## Findings and interpretation

Primary **ETF first execution 2007-08-31**, first invested return **2007-09-04**, endpoint **2026-08-31**. All eight prices start by 2006-02-06; 12-month signals then 126 B2 strategy-return observations determine the later shared comparison start. Factor first execution **1990-01-31**, first invested return **1990-02-01**, endpoint **2026-08-31**. ETF and VIX caches reach September30; French daily RF/Mom end August31, binding both experiments. No September cash approximation is invented.

Recommend a **research-stage B3 risk-limited ETF pitch**, with a USD1m execution-validation scenario before the illustrative USD10m mandate. ETF modeled net full-history CAGR6.89099%, Sharpe0.61357, daily maximum drawdown-17.91141%. B1 has higher CAGR8.65799%;60/40 has higher full-history Sharpe0.71919. B3's lower downside comes with22.82457% average cash. Paired bootstrap does not establish superiority. The evolving10m scenario reaches19.17367% of historical DBC ADV20, so a universal single-close mandate is unsubstantiated. Consult exact CSVs for canonical values; rounded README values are explanatory.

A3's synthetic gross cash-plus-factor experiment has CAGR11.99354% and max daily drawdown-18.89310%, compared with static A0 CAGR7.93818% and drawdown-63.28816%. Factor financing/borrow/internal turnover and capacity are not established; it is not an executable stock strategy. No sector neutrality, volatility-adjusted stock rankings or new anomaly claimed.

## Reproduction with cached data

Python **3.12.7** was used. All installed research/notebook/report dependencies are pinned in `requirements.lock.txt`; it is a macOS environment snapshot (the `appnope` pin is Mac-specific). On another OS remove only that platform-specific package and document the environment difference. Source has no absolute original-workspace paths.

```bash
cd hw2_momentum
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
export PYTHONPATH="$PWD/src"
export MPLCONFIGDIR="$PWD/build/matplotlib"
.venv/bin/python -m momentum_hw2.cli validate-data --offline
.venv/bin/python -m pytest -q
.venv/bin/python -m momentum_hw2.cli run --offline
.venv/bin/python -m momentum_hw2.cli report --offline
.venv/bin/python scripts/audit_results.py
.venv/bin/python scripts/build_notebooks.py
.venv/bin/python scripts/execute_notebooks.py
.venv/bin/python scripts/clean_reproduce.py
```

In the supplied workspace `.venv` is already populated. If using uv, use `uv pip install --python .venv/bin/python -r requirements.lock.txt`. Notebook execution needs local Jupyter kernel ports; restricted environments may require approval. The kernel spec is created inside build/ and points to the new local environment. `execute_notebooks.py` sets all runtime/cache paths inside the project. Nothing calls WRDS.

`run`, `validate-data`, and `report` are offline by construction; `clean_reproduce.py` additionally forbids HTTP, reruns data validation/backtests/robustness/reports and compares SHA256 of every existing numeric result table plus decisions/holdings/targets/trades. Run metadata timestamps intentionally differ. Read `outputs/audits/clean_run.log`, `reproduction_hashes.json`, `pytest.log`, `independent_accounting_checks.csv`, and `artifact_qa.json` for actual verification status.

## Fetch / input fallback

Existing raw snapshots are preserved and reused. To acquire a **new vintage**, copy the project to a new directory, preserve original manifests and move its existing raw/processed caches into a dated vintage directory first; do not overwrite original snapshots.

```bash
.venv/bin/python -m momentum_hw2.cli fetch --config config/base.yaml
.venv/bin/python -m momentum_hw2.cli import-csv --ticker SPY --input path/to/SPY.csv --provider "documented provider"
```

Import accepts `date,Close,Adj Close,Volume`, optionally `Dividends,Stock Splits,Capital Gains`. It refuses to overwrite a ticker cache. Verify dividend/split adjustments, currency, daily US sessions, historical ticker coverage and volume scope; import provenance is stored separately. French fallback inputs use the original provider archives or normalized `date,Mom` / `date,Mkt-RF,SMB,HML,RF` CSVs in data/processed. Cboe fallback is `date,VIX`. No raw unadjusted return substitution is permitted. Databento was unused; no new charges authorized or incurred.

## Accounting and evaluation conventions

At penultimate close compute signals, execute final close, old holdings earn through execution and new holdings from next session. ETFs drift between rebalances. Risky turnover is full sum of absolute weight changes; costs10bps per traded dollar, with0/5/25/50bps sensitivities. Apply a pre-cost turnover charge as a proportional NAV haircut and allocate post-cost targets. Initial purchase costs included. Cash earns daily French RF. Adj Close already includes distributions; ETF expenses remain embedded. No dividends/expenses added or deducted again, no borrowing/leverage in B.

B3 forecasts trailing gross B2 excess volatility, requires126 observed daily strategy returns, caps exposure at1 and routes balance to cash. Initial execution stub charge is incorporated into first full holding-month return for monthly metrics; daily NAV records retain the charge on execution day. ACT/365.25 CAGR includes elapsed days from execution inception. Historical partitions do not restart rolling signals. B sensitivity comparison starts2007-10-31 to accommodate longer skip-month warmup; primary remains2007-08-31. This date adjustment follows eligibility, not results.

Sortino uses all-month RMS negative monthly excess; sample standard deviations use ddof1; monthly Sharpe uses compounded cash-adjusted capital returns. Maximum daily drawdown and monthly-end drawdown are separate; recovery records incomplete status. VaR/ES losses positive; tail counts exported. HAC3 regressions are attribution, not causal alpha. Paired moving-block bootstrap6months/1000reps/seed9339 resamples historical return paths, not new strategies or unseen markets.

## Output map

`data/raw`: immutable download snapshots; `data/manifests`: URLs, timestamps, hashes, headers/API options; `data/processed`: reproducible normalized factor/ETF/cash data. Public-source personal academic caches are not a claim of redistribution permission; keep the bundle private.

`outputs/tables`: primary gross/net daily/monthly returns and all sensitivities, chronological/stress metrics, official monthly Mom context, uncertainty/regressions/capacity. `outputs/audits`: dated signals, risk sizing, full daily drifted holdings, target/pretrade trades/costs, VIX backward joins, action checks, run and verification records. `outputs/figures`: actual-result NAV/drawdowns, factor regimes, ETF allocations/components/robustness.

`research`: requirements, sources, frozen plan/config hash, progress, data quality, recommendation and acceptance. `deliverables`: report and investor content. `scripts`: explanatory notebook builders/runners, independent audits, cached clean reproduction and artifact rendering. `build`: private runtime/rendering scratch, excluded from handoff archive.

Historical corporate-action QA: Yahoo Close is split-normalized, not original pre-split transaction price. Targeted issuer distributions show small rounding discrepancies despite rounding=False; June2026 EEM month-end return differs about2.14bps from issuer market-price return. No data were repaired. Volume normalization remains uncertified; capacity uses a vendor dollar-volume proxy. See research/corporate_actions.md and outputs/audits/independent_provider_checks.csv.
