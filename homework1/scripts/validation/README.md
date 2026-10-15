# Separate reconstruction and validation

Run from the `homework1/` project root with the existing shared FINCB9339
interpreter. Inputs come from `data/raw/`; no original workbook is edited.

```sh
"$HOME/.venvs/sys-inv/bin/python" scripts/validation/independent_validation.py
node scripts/validation/build_workbook.mjs
"$HOME/.venvs/sys-inv/bin/python" scripts/validation/verify_outputs.py
"$HOME/.venvs/sys-inv/bin/python" scripts/validation/write_report.py
```

The workbook builder needs the Artifact Tool Node package. Replay first: it
regenerates `results/validation/workbook_data.json`, scenario ledgers and the
preservation hashes needed by the subsequent builders/checks. These staging
files are intentionally absent from Git. Do not treat old absolute paths in
historical hash files as current configuration or edit the preserved baseline
solely to relocate it.

Delivered outputs remain at `results/validation/validation_tables.xlsx` and
`results/validation/VALIDATION_REPORT.md`. Baseline inputs/results are under
`data/raw/` and `results/baseline/`. The separate engine imports no strategy
functions; it uses direct historical summation and inventory-times-price-change
accounting, then compares with the baseline. It is corroboration by another
code path from the same researcher, not blind third-party validation.

The validation workbook recalculates selected manual arithmetic; its sensitivity
and daily replay inputs are fixed snapshots. Native Excel recalculation was not
tested in the original work. The folder reorganization preserves the delivered
workbook bytes and does not claim a new workbook-calculation test.
