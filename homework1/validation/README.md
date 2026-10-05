# Separate validation outputs

This code and the `outputs/validation` directory extend the original v0.1 workspace. They do not replace or modify the baseline code, source workbook or baseline results.

Primary deliverables are `outputs/validation/validation_tables.xlsx` and `outputs/validation/VALIDATION_REPORT.md`. The report defines every sensitivity, trade-matching rule and concentration metric. `CHANGELOG.md` and `PROMPTS.md` retain both phases.

The second implementation imports no baseline functions. It uses source-row loops/direct arithmetic and interval inventory P&L, and compares its output with the frozen baseline only afterward. It is not a blind validation by a different researcher: the same AI knew and preserved the baseline conventions.

To reproduce in the original workspace:

```sh
/Users/lysanzh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validation/independent_validation.py
/Users/lysanzh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node validation/build_workbook.mjs
/Users/lysanzh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validation/verify_outputs.py
/Users/lysanzh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 validation/write_report.py
```

The workbook builder uses the Artifact Tool package through the local `validation/node_modules` symlink to the bundled dependency directory. This symlink and the original source workbook are not copied into the validation archive. Outside this environment, install pandas/numpy/openpyxl for the Python steps and provide Artifact Tool for the optional workbook-building step. The delivered workbook and CSVs are usable directly in Excel without running the scripts.

Extract the validation archive alongside the original v0.1 workspace if rerunning: the baseline manifest, baseline CSVs, original workbook and protected v0.1 package are needed by the preservation/reconciliation checks. Absolute source paths in the baseline manifest may require adjustment in a relocated copy; never edit the original preserved baseline solely to run a relocated copy.

The Excel workbook recalculates the manual arithmetic for the four selected days. Its sensitivity tables and daily replay cash-flow inputs are saved run outputs, not an interactive full-history backtest. Native Excel recalculation was not tested; exported formula caches and Artifact Tool recalculation were verified.
