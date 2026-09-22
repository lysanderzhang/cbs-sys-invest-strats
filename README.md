# Homework 1: SPY intraday strategy replication

This is an independently written, paper-only Python implementation of the requested Models A, B, and C. No author-provided code was searched, opened, copied, or used. No parameter optimization or external market-data download was performed. This delivery is the first implementation for the student's subsequent validation and critique, not an independently certified replication.

Read `PRE_IMPLEMENTATION.md` for the assignment requirements, paper equations, workbook audit, complete strategy choices, and ambiguities. Read `RESULTS_AND_VALIDATION.md` for results, metric definitions, and specific manual checks. `CHANGELOG.md` and `PROMPTS.md` preserve the development record.

## Run

With Python 3.12 and the packages in `requirements.txt` installed:

```sh
python strategy.py '/absolute/path/hw1.spy.20250313-20251201.intra-30m.xlsx' --output outputs/baseline
```

In the current Codex workspace, bundled Python plus locally installed plotting/statistics dependencies are already configured:

```sh
zsh run_local.sh '/Users/lysanzh/Library/CloudStorage/OneDrive-Personal/MacBook/curriculum/1 courses/sem-3 2026 fall/FINC9339 systematic investment strategies/homework/hw1/hw1.spy.20250313-20251201.intra-30m.xlsx'
PYTHONPATH=.python-deps /Users/lysanzh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 test_strategy.py
```

The test fixture path is at the top of `test_strategy.py`; change it when relocating the workbook. Source files are read-only and remain in their original directory. The original source workbook and PDFs are not committed here. The submission workbook integrates copies of the three source data sheets for auditability.

## Excel submission workbook

`outputs/submission/FINCB9339_HW1_Submission.xlsx` is the single-file spreadsheet deliverable. It contains the original SPY source sheets, all scored daily results, completed trades, execution legs, signal inputs, April 2 calculation checks, implementation sensitivities, concentration analysis, and a method note. Trade P&L and selected manual checks recalculate with Excel formulas; the full historical strategy state machine and sensitivity cases are fixed, labeled Python outputs. See `submission/prepare_data.py` and `submission/build_submission.mjs` for the reproducible packaging steps. The `submission/node_modules` symlink and staged JSON are local build dependencies and are not committed.

Later sensitivity switches are available but have NOT been run as a parameter search: `--vwap-method midpoint`, `--execution-delay 1`, `--entry-vwap-filter`, and `--timestamp-mode as_labeled`. Always give sensitivity runs a different `--output` directory. The as-labeled mode is valid only if vendor metadata establishes that observations are actually available at their labels; otherwise it can introduce look-ahead. A 30-minute delayed fill is a deliberately coarse alternative, not a realistic subsecond execution model.

## Function map

| Purpose | Function |
|---|---|
| Read workbook and audit raw/cleaned differences | `load_workbook`, `audit_data` |
| Prepare sessions, timestamp availability and closing prints | `prepare_data` |
| Open proxy, prior close and daily return construction | `construct_daily` |
| Validate/difference volume convention | `incremental_volume` |
| Prior-session time-of-day Noise Area | `calculate_noise_area` |
| Isolated VWAP approximation | `approximate_vwap` |
| Position state transitions | `generate_signal` |
| Event-by-event execution and realized accounting | `execute_trades`, `event_record` |
| Per-leg commissions/slippage | `transaction_costs` |
| Daily share counts and volatility scaling | `dynamic_position_size` |
| Independent daily aggregation of execution ledger | `daily_pnl_equity` |
| Constant-share SPY comparator | `buy_and_hold` |
| Return statistics and regression uncertainty | `performance_statistics` |

## Output map

All baseline output is under `outputs/baseline/`:

- `performance.csv`: requested statistics, five or more decimal places, with OLS and HAC regression inference.
- `features.csv`: each retained observation, source/availability timestamps, price provenance, volume weights, open proxy, previous close, Noise estimates/counts, boundaries and approximate VWAP/stops, including warm-up rows.
- `daily_inputs.csv`: daily price inputs, lagged volatility, scheduled close, warm-up eligibility.
- `A/B/C_executions.csv`: every charged entry/exit leg. `net_pnl` is event cash P&L (entry cost at entry, gross realization minus exit costs at exit). Sum this column, not just exit rows.
- `A/B/C_trades.csv`: completed round trips with BOTH entry and exit costs; `net_pnl` is the full round-trip result. Do not add this to execution P&L, which would double count.
- `A/B/C_daily.csv`: beginning equity, daily realized gross P&L, separate commissions/slippage, daily net P&L, ending equity, daily return and sizing.
- `A/B/C_positions.csv`: post-decision inventory, marked equity and marked leverage. These capture unrealized movement without changing the realized ledger.
- `SPY_gross_daily.csv`, `SPY_net_daily.csv`: common-period price-series buy-and-hold comparators, without and with one entry/exit cost.
- `data_audit.json`, `data_audit_by_day.csv`, `cleaning_changes.csv`, `excluded_rows.csv`: audit evidence. Excluded interval rows include separate closing prints whose price is still used for liquidation; they are not all discarded prices.
- `run_manifest.json`: parameters, source and code hashes, library versions, sample dates and provenance declarations.
- `equity_drawdown.png`, `spot_check_days.png`: charts. Lines connect available observations for display; they do not claim knowledge of the path between observations.
- `validation.txt`: final test run.

The estimator/strategy functions use only pandas/numpy. Matplotlib creates static plots; statsmodels provides the regression diagnostics. The baseline runtime used pandas 3.0.6, numpy 2.5.3, matplotlib 3.11.2, statsmodels 0.15.0 and scipy 1.18.1. All implementation and validation was performed in this task; there was no second-agent independent review.
