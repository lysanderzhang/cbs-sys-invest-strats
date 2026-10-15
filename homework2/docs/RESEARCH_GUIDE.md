# FINCB9339 Homework 2: controlled momentum experiments

Hanyu Zhang. Research cutoff **September 30, 2026**. Due **October 5, 2026 at 5:00 p.m. America/New_York**, per user instruction. Neither trades nor submission performed.

## Git repository edition

This project is now under `homework2/`. See [Homework 2 README](../README.md) for the updated October 5 editable LaTeX investor presentation and repository input policy. Raw/processed input caches and build scratch are excluded from Git; the shared Python environment is outside the repository. a fresh clone needs authorized original caches or a new provider acquisition before offline backtests can run. New downloads may revise the data vintage. Existing historical outputs and verification logs are retained unchanged.

## Start with the deliverables

- [Technical report](../report/HW2_Momentum_Research_Report.md) and [report PDF](../submission/HW2_Momentum_Research_Report.pdf).
- [Presentation PDF](../submission/archive/HW2_Investor_Presentation.pdf): 12 substantive slides plus five appendix slides.
- [Editable slide manuscript with speaker notes](../report/original_presentation/HW2_Investor_Presentation_Manuscript.md) and [structured slides](../report/original_presentation/slides.json).
- [Executed factor notebook](../notebooks/01_factor_overlay.ipynb) and [executed ETF notebook](../notebooks/02_etf_dual_momentum.ipynb).
- [Acceptance checklist](research/acceptance_checklist.md), [data quality](research/data_quality.md), [requirements map](research/requirements_matrix.md), [source map](research/source_map.md), [research freeze](research/freeze.json).
- Exact numeric evidence: [performance](../results/tables/performance.csv), [sensitivities](../results/tables/sensitivities.csv), [bootstrap](../results/tables/bootstrap.csv), [capacity](../results/tables/capacity_summary.csv), [all evaluated variants](../results/tables/variant_ledger.csv).

**Presentation format limitation:** the installed presentation skill requires `load_workspace_dependencies` and `@oai/artifact-tool`; neither capability/package is available in this runtime. The native Microsoft PowerPoint fallback returned “Can't make class presentation” (-2710); computer control reported `noWindowsAvailable`. No PPTX is claimed. The specification's explicit fallback is delivered: a complete editable manuscript/JSON with notes and a shareable slide PDF. Artifact formatting markers were executed successfully; PDF generation/rendering uses ReportLab/PyMuPDF. Rendered chart PNGs and their underlying CSV data are included for future deck editing.

## Findings and interpretation

Primary **ETF first execution 2007-08-31**, first invested return **2007-09-04**, endpoint **2026-08-31**. All eight prices start by 2006-02-06; 12-month signals then 126 B2 strategy-return observations determine the later shared comparison start. Factor first execution **1990-01-31**, first invested return **1990-02-01**, endpoint **2026-08-31**. ETF and VIX caches reach September30; French daily RF/Mom end August31, binding both experiments. No September cash approximation is invented.

Recommend a **research-stage B3 risk-limited ETF pitch**, with a USD1m execution-validation scenario before the illustrative USD10m mandate. ETF modeled net full-history CAGR6.89099%, Sharpe0.61357, daily maximum drawdown-17.91141%. B1 has higher CAGR8.65799%;60/40 has higher full-history Sharpe0.71919. B3's lower downside comes with22.82457% average cash. Paired bootstrap does not establish superiority. The evolving10m scenario reaches19.17367% of historical DBC ADV20, so a universal single-close mandate is unsubstantiated. Consult exact CSVs for canonical values; rounded README values are explanatory.

A3's synthetic gross cash-plus-factor experiment has CAGR11.99354% and max daily drawdown-18.89310%, compared with static A0 CAGR7.93818% and drawdown-63.28816%. Factor financing/borrow/internal turnover and capacity are not established; it is not an executable stock strategy. No sector neutrality, volatility-adjusted stock rankings or new anomaly claimed.

## Reproduction with cached data

The original raw/processed vendor caches are absent from the current checkout. Restore authorized original caches before running cache-dependent commands below; the restructuring did not fetch data or re-execute the notebooks.

The original research used Python **3.12.7**. Reuse the existing shared course environment for current work. The historical research/notebook/report package versions are recorded in `requirements.lock.txt` (including a macOS-specific `appnope` pin). This record is provenance only; do not install or synchronize it into the shared course environment. Source has no absolute original-workspace paths.

```bash
cd homework2
"$HOME/.venvs/sys-inv/bin/python" -c 'import sys; print(sys.executable)'
export PYTHONPATH="$PWD/src"
export MPLCONFIGDIR="$PWD/build/matplotlib"
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli validate-data --offline
"$HOME/.venvs/sys-inv/bin/python" -m pytest -q
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli run --offline
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli report --offline
"$HOME/.venvs/sys-inv/bin/python" scripts/audit_results.py
"$HOME/.venvs/sys-inv/bin/python" scripts/build_notebooks.py
"$HOME/.venvs/sys-inv/bin/python" scripts/execute_notebooks.py
"$HOME/.venvs/sys-inv/bin/python" scripts/clean_reproduce.py
```

Do not create a homework-local environment or run `uv sync`. The historical lock file is provenance, not a synchronization target for the shared environment. Install only missing packages with `uv pip install --python "$HOME/.venvs/sys-inv/bin/python" <packages>`. Notebook kernels point to that shared interpreter; project `build/` contains only runtime scratch. Nothing calls WRDS.

`run`, `validate-data`, and `report` are offline by construction; `clean_reproduce.py` additionally forbids HTTP, reruns data validation/backtests/robustness/reports and compares SHA256 of every existing numeric result table plus decisions/holdings/targets/trades. Run metadata timestamps intentionally differ. Read `results/audits/clean_run.log`, `reproduction_hashes.json`, `pytest.log`, `independent_accounting_checks.csv`, and `artifact_qa.json` for actual verification status.

## Fetch / input fallback

Existing raw snapshots are preserved and reused. To acquire a **new vintage**, copy the project to a new directory, preserve original manifests and move its existing raw/processed caches into a dated vintage directory first; do not overwrite original snapshots.

```bash
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli fetch --config config/base.yaml
"$HOME/.venvs/sys-inv/bin/python" -m momentum_hw2.cli import-csv --ticker SPY --input path/to/SPY.csv --provider "documented provider"
```

Import accepts `date,Close,Adj Close,Volume`, optionally `Dividends,Stock Splits,Capital Gains`. It refuses to overwrite a ticker cache. Verify dividend/split adjustments, currency, daily US sessions, historical ticker coverage and volume scope; import provenance is stored separately. French fallback inputs use the original provider archives or normalized `date,Mom` / `date,Mkt-RF,SMB,HML,RF` CSVs in data/processed. Cboe fallback is `date,VIX`. No raw unadjusted return substitution is permitted. Databento was unused; no new charges authorized or incurred.

## Accounting and evaluation conventions

At penultimate close compute signals, execute final close, old holdings earn through execution and new holdings from next session. ETFs drift between rebalances. Risky turnover is full sum of absolute weight changes; costs10bps per traded dollar, with0/5/25/50bps sensitivities. Apply a pre-cost turnover charge as a proportional NAV haircut and allocate post-cost targets. Initial purchase costs included. Cash earns daily French RF. Adj Close already includes distributions; ETF expenses remain embedded. No dividends/expenses added or deducted again, no borrowing/leverage in B.

B3 forecasts trailing gross B2 excess volatility, requires126 observed daily strategy returns, caps exposure at1 and routes balance to cash. Initial execution stub charge is incorporated into first full holding-month return for monthly metrics; daily NAV records retain the charge on execution day. ACT/365.25 CAGR includes elapsed days from execution inception. Historical partitions do not restart rolling signals. B sensitivity comparison starts2007-10-31 to accommodate longer skip-month warmup; primary remains2007-08-31. This date adjustment follows eligibility, not results.

Sortino uses all-month RMS negative monthly excess; sample standard deviations use ddof1; monthly Sharpe uses compounded cash-adjusted capital returns. Maximum daily drawdown and monthly-end drawdown are separate; recovery records incomplete status. VaR/ES losses positive; tail counts exported. HAC3 regressions are attribution, not causal alpha. Paired moving-block bootstrap6months/1000reps/seed9339 resamples historical return paths, not new strategies or unseen markets.

## Output map

`data/raw`: immutable download snapshots; `data/manifests`: URLs, timestamps, hashes, headers/API options; `data/processed`: reproducible normalized factor/ETF/cash data. Public-source personal academic caches are not a claim of redistribution permission; keep the bundle private.

`results/tables`: primary gross/net daily/monthly returns and all sensitivities, chronological/stress metrics, official monthly Mom context, uncertainty/regressions/capacity. `results/audits`: dated signals, risk sizing, full daily drifted holdings, target/pretrade trades/costs, VIX backward joins, action checks, run and verification records. `results/figures`: actual-result NAV/drawdowns, factor regimes, ETF allocations/components/robustness.

`docs/research`: requirements, sources, frozen plan/config hash, progress, data quality, recommendation and acceptance. `report/`: editable research and presentation sources; `submission/`: final PDFs and the archived original deck. `scripts`: explanatory notebook builders/runners, independent audits, cached clean reproduction and artifact rendering. `build`: private runtime/rendering scratch, excluded from handoff archive.

Historical corporate-action QA: Yahoo Close is split-normalized, not original pre-split transaction price. Targeted issuer distributions show small rounding discrepancies despite rounding=False; June2026 EEM month-end return differs about2.14bps from issuer market-price return. No data were repaired. Volume normalization remains uncertified; capacity uses a vendor dollar-volume proxy. See docs/research/corporate_actions.md and results/audits/independent_provider_checks.csv.
