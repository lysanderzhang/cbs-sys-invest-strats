# Changelog

Append subsequent iterations here; do not overwrite this first-delivery history. Each entry should record user prompt/reference, change, reason, affected results, validation, and unresolved questions. Baseline artifacts and `run_manifest.json` identify the current first-delivery state.

## 2026-09-22 — v0.1, first AI-generated implementation

- Prompt: initial user request preserved in `PROMPTS.md`. Tool: Codex; language Python; pandas/numpy for transparent formulas/event accounting, matplotlib for plots, statsmodels for inference. The student should supply their own reason for choosing Codex rather than have that personal choice invented here.
- Read all assignment requirements and the paper's mathematical rules, cost discussion and relevant FAQ context. Rendered key equation pages to verify floor notation, boundary adjustments and the volatility denominator. Did not follow any links to author code or consult other implementations.
- Found three workbook sheets and audited all rows. Identified noncumulative volume, 176 changed/added closing volumes, seven daily-volume discrepancies, closing-print rounding, likely start-labeled bars, and stale half-day afternoon records.
- Recorded the pre-code specification in `PRE_IMPLEMENTATION.md`. Selected conservative information availability under inferred start labeling, a first-interval open proxy, isolated endpoint VWAP approximation, scheduled half-day liquidation and explicit available-slot averaging within 14 prior sessions.
- Created modular `strategy.py`, diagnostics, benchmark, regression statistics, tests and charts. No parameter search was run.
- Environment issue: bundled Python lacked matplotlib/statsmodels. Initial package download failed on sandbox DNS; approved retry installed dependencies into workspace `.python-deps`, leaving bundled dependencies unchanged. Initial plot run reported unwritable font caches but finished; the local matplotlib cache made subsequent run clean. This was not a strategy error.
- Test correction: initial cost check used exact floating-point equality between separate commission+slippage calculations and .0045*shares. Replaced it with absolute tolerance 1e-12. No cost formula or strategy result changed.
- Specification correction before delivery: removed initial B/C VWAP entry gate from baseline because the user requires the same Noise-based entry signals. Retained the gate as an optional future sensitivity switch. No baseline entry already breached VWAP, so this correction changed no trades or returns on the supplied sample. Updated pre-implementation choice transparently rather than presenting it as original.
- Provenance improvement: added separate price-source timestamp for the liquidation print, so a corrected final close is not attributed to the preceding interval label.
- Reporting correction: removed benchmark-on-itself regression p-values as uninformative. Strategy OLS and HAC results retained.
- Final verification: all 8 tests pass; accounting reconciles; future-data mutation does not affect preceding features/trades; all positions are flat at scheduled close; charts visually inspected. Independent author-code or second-implementation validation has not been performed.
- Final scored period April 2–December 1, 168 sessions. Net cumulative returns: A 3.59421%, B 4.47404%, C 11.13927%; SPY supplied-price gross benchmark 21.96250%. Stopped at first implementation as requested.

## Template for next iteration

- Date/version and exact prompt:
- Issue discovered and independent evidence:
- Correction or improvement:
- Affected assumptions/functions:
- Before/after trade and performance differences:
- Checks run and outcome:
- Remaining limitations:

## 2026-09-22 — v0.2 validation outputs; v0.1 baseline unchanged

- Prompt: second user request recorded in `PROMPTS.md`: independently reconstruct April 2, July 3, October 10 and November 21 Model C calculations; run five implementation-ambiguity sensitivities; analyze concentration; preserve the baseline and do not optimize.
- Created a separate implementation in `validation/independent_validation.py` with no import or call to baseline functions. It rereads the original workbook, identifies literal Excel source cells, directly sums historical observations, and accounts for equity through held inventory times successive price changes. Frozen baseline CSVs are read only after replay for comparison.
- Reconstructed all 46 decision rows for four days, 644 historical Noise observations, 56 daily-return inputs and six round trips. Created an Excel workbook with formulas and matching CSVs. October 10 contains one short trade; November 21 contains two long trades.
- All 34 reconciliation checks pass; all baseline trade episodes match and the maximum checked numerical difference is 3.35e-10. This is separate-code-path validation by the same AI, not a blind third-party review or vendor-data verification. No author code was consulted.
- Predeclared one-change-at-a-time cases: midpoint VWAP; one-grid-step execution delay with scheduled-close override; additional B/C VWAP entry gate; require a full 14-observation history or suppress that discretionary slot; commission .005 plus slippage .002 per share. All 18 case/model runs are retained, with no preferred specification selected.
- Defined changed trades by exact direction, entry/exit times and prices; counted missing baseline episodes as changed and reported quantity-only changes separately. Four C episodes change under the strict-slot treatment; all 135 change under delayed execution. Midpoint and entry gating change no trades in this sample.
- C cumulative returns: baseline 11.13927%; midpoint 11.13927%; delayed 3.90194%; entry gate 11.13927%; strict slots 12.21890%; higher costs 10.80734%. These results do not alter the baseline.
- Concentration: best-day dollar P&L is 85.10779% of total net profit. Removing best 1/3/5 net daily returns by setting them to zero yields 1.66230% / -4.18574% / -7.95159%; analogous worst-day removals yield 13.42072% / 17.42466% / 20.83376%. No forward trading rule is inferred from hindsight rankings.
- Validation-tool correction: source-cell readback initially attempted to access `.coordinate` on an openpyxl EmptyCell. The read-only verifier now skips empty cells; no source data, calculations or results changed. A pandas concatenation future warning was nonfatal and is retained in the run log.
- Presentation correction: displayed reconciliation residuals are rounded to eight decimals to avoid red negative zero caused by floating arithmetic. An interim commentary transcription was corrected to the full-precision delayed return 3.90194% and best-three-removal return -4.18574%; delivered tables use the actual outputs.
- Workbook checks: 2,774 formula values agree with the independent calculations, input perturbation/restoration confirms recalculation, no formula errors found, all nine sheets visually inspected, and saved formula caches verified. Native Excel recalculation has not been tested.
- All 18 scenario/model ledgers reconcile; source references match the workbook. SHA-256 hashes confirm all 30 protected baseline/source files remain unchanged. New outputs are only in `outputs/validation/`, new code in `validation/`, and the validation package is separate.
- Remaining uncertainty: exact market open, timestamp semantics, full VWAP, execution feasibility, and interpretation of the half-day omission policy. The sensitivity conclusions apply to these selected interpretations and this short sample, not all possible implementations.

## 2026-09-22 — v0.3 single-file Excel submission; baseline unchanged

- Prompt: create one Excel deliverable for submission, using `FINCB9339_HW1.tex` as the reference write-up. The write-up's reported baseline figures and interpretation were checked against the frozen output files.
- Created `outputs/submission/FINCB9339_HW1_Submission.xlsx` with 13 sheets: overview, 168 scored daily results, 365 completed trades, 730 execution legs, 2,354 signal rows, April 2 Noise and volatility arithmetic, sensitivity, concentration, and the three original SPY source sheets.
- Excel formulas independently recalculate all trade gross P&L, commission, slippage and net P&L; daily SUMIFS reconcile trade P&L to each model's frozen daily result; the April 2 tables recalculate the 14-observation Noise Area, lagged volatility, leverage and shares. Full historical state transitions and scenario outputs are labeled as frozen Python results, not a live Excel backtester.
- Source workbook SHA-256 matched the original run manifest. Validation found zero daily trade-net reconciliation differences above $0.000001 across all three models, zero missing signal-to-source row mappings, zero Excel error cells, and all ten selected formula checks passed. The export has been visually reviewed. Native Microsoft Excel recalculation remains untested.
- Presentation correction during build: balanced the overview columns and moved the method-sheet section header below the live parameter cells. This did not change any model calculations or baseline/validation files.
- Frozen baseline returns remain A 3.59421%, B 4.47404%, C 11.13927%; SPY gross 21.96250%. No optimization or baseline assumption change was made.

## 2026-09-22 — v0.4 Git commit preparation

- Prompt: prepare the completed project for a Git commit. The repository was on unborn `main` with no tracked files or prior commits.
- Updated `.gitignore` to exclude local dependencies, temporary JSON staging, workbook inspection files and previews, large generated scenario ledgers, duplicate ZIP archives, and extracted source-document text. Retained the final workbook, implementation and validation code, documentation, and auditable baseline/validation outputs.
- Updated `README.md` to describe the single-file Excel deliverable and clarify that it includes copied source-data sheets while the original input workbook and PDFs are not committed.
- Staged 73 project files without creating a commit. Git's whitespace check passed, all eight strategy tests passed, and the staged set contains no dependency symlinks or inspection dumps. Baseline strategy files and results were not changed during this preparation.
