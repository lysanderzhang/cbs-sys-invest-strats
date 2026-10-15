# Homework 1: SPY intraday strategy replication

An independent, paper-only implementation of Models A, B and C, with the submitted
report, original submitted workbook, research outputs and reproduction instructions.

## Start here

- [Submitted report](submission/HW1_Hanyu_Zhang_FINCB9339.pdf)
- [Original submitted workbook](submission/original_submitted/FINCB9339_HW1_Submission.xlsx)
- [Original LaTeX source](report/submitted/FINCB9339_HW1_data_prep_prompt.tex)
- [Research-generated workbook](submission/FINCB9339_HW1_Submission.xlsx)
- [Results and validation](report/RESULTS_AND_VALIDATION.md)
- [Separate reconstruction report](results/validation/VALIDATION_REPORT.md) and
  [formula validation workbook](results/validation/validation_tables.xlsx)
- [Methodology and source audit](docs/PRE_IMPLEMENTATION.md)
- [Development history](docs/CHANGELOG.md) and [prompt record](docs/PROMPTS.md)

## Structure

```text
homework1/
  data/raw/             Unchanged local copy of the supplied SPY workbook
  data/manifest.json    Original location and input SHA-256
  src/strategy.py       Models, accounting, statistics and command-line runner
  tests/                Deterministic correctness checks
  scripts/submission/   Submission workbook staging and builder
  scripts/validation/   Separate arithmetic replay and workbook verification
  results/baseline/     Preserved daily series, trades, positions and figures
  results/validation/   Preserved independent checks and sensitivity results
  report/               Research write-up
  docs/                 Methodology and development history
  submission/           Submitted report, original workbook and research workbook
  requirements.txt      Research dependencies
  pyproject.toml        Dependency metadata and pytest paths
```

`results/structure_manifest.json` records every original file's new location and
hash. Historical manifests and logs retain the paths and hashes from their original
runs; they are evidence, not current path configuration. The raw workbook and final
workbooks are unchanged. The source workbook copy is intentionally ignored by Git;
a fresh clone needs that authorized input at the documented local path.

## Shared Python environment

Use only `$HOME/.venvs/sys-inv/bin/python`, the existing FINCB9339 environment.
Do not create a project `.venv` or `venv`, run `uv sync`, or downgrade the course
environment to a homework dependency file. Install only missing dependencies with
`uv pip install --python "$HOME/.venvs/sys-inv/bin/python" <packages>`.
The course-wide policy is in [AGENTS.md](../AGENTS.md).

From this homework root:

```sh
"$HOME/.venvs/sys-inv/bin/python" -c 'import sys; print(sys.executable)'
"$HOME/.venvs/sys-inv/bin/python" -m pytest -q
# Reproduce into a separate run directory, keeping the historical baseline intact:
"$HOME/.venvs/sys-inv/bin/python" src/strategy.py data/raw/hw1.spy.20250313-20251201.intra-30m.xlsx --output results/reproduction
```

Without `--output`, the runner writes `results/baseline/`. Use separate directories
for sensitivity runs. Available switches are `--vwap-method midpoint`,
`--execution-delay 1`, `--entry-vwap-filter` and `--timestamp-mode as_labeled`.
The as-labeled mode requires vendor evidence that observations are available at
those timestamps; otherwise it can introduce look-ahead. A 30-minute delay is a
coarse diagnostic rather than a realistic subsecond execution model.

## Workbook and separate validation builds

Read [validation instructions](scripts/validation/README.md) before rebuilding
its outputs. From this homework root, stage the submission workbook inputs with:

```sh
"$HOME/.venvs/sys-inv/bin/python" scripts/submission/prepare_data.py
node scripts/submission/build_submission.mjs
```

Workbook builders require the existing Artifact Tool Node package/runtime. No
workbook authoring or recalculation is required to use the delivered Excel files.
Staged JSON, rendering scratch and Node dependencies are excluded from Git.

The final workbook contains copies of all three input sheets, daily results,
completed trades, execution legs, signals, April 2 checks, sensitivities and
concentration analysis. Selected calculations use Excel formulas; the full
historical state machine remains labeled Python output. It is not a live backtester.

## Methods and output interpretation

No author-provided implementation was consulted and no optimization or new market
data acquisition was performed in the original research. Read the methodology
for the inferred bar availability, open proxy, approximate VWAP, half-day treatment,
transaction costs and sizing assumptions. The implementation is not vendor-data
certification or blind third-party validation.

The baseline directory retains `performance.csv`, `features.csv`, `daily_inputs.csv`,
`A/B/C_daily.csv`, `A/B/C_trades.csv`, `A/B/C_executions.csv`, `A/B/C_positions.csv`,
SPY comparators, source-cleaning audits, two charts and `run_manifest.json`.
`net_pnl` in the execution ledger is event cash P&L including the applicable leg's
costs; summing it reconciles daily P&L. Trade-ledger P&L already includes both legs'
costs; adding it to execution P&L would double count. Positions retain marked
inventory information separately from the realized ledger.

The strategy functions use NumPy/pandas, matplotlib generates figures, and
statsmodels supplies regression diagnostics. Current restructuring checks and
result-preservation evidence are recorded in `results/structure_validation.json`.

## Restored submitted artifacts

The actual 20-page submitted report and associated LaTeX source were located in
the original external `homework/hw1/` folder on October 14, 2026, and copied
unchanged. They were absent from the repository used for the earlier restructuring.
`results/submitted_artifact_restoration.json` records source paths and matching SHA-256 hashes.

The original submitted workbook (837,251 bytes) differs from the preserved
research-generated workbook (689,456 bytes). Both remain available: the original
is under `submission/original_submitted/`; the research-generated workbook keeps
its existing path and validation record. No equivalence between these versions
is asserted. The original TeX is retained as source provenance; its external
figure dependencies have not been reconstructed or its submitted PDF rebuilt.
