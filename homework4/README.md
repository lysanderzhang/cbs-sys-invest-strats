# Homework 4: inverse FX returns, doubling time and crash-neutral carry

Hanyu Zhang · FINCB9339 · Fall 2026

## Submission

**[HW4_Hanyu_Zhang_FINCB9339.pdf](submission/HW4_Hanyu_Zhang_FINCB9339.pdf)**
is the complete eight-page write-up. It summarizes all answers on page one and
contains every derivation, empirical comparison, sensitivity result and figure.
Submit this single PDF as the report.

The canonical editable source is [report/main.tex](report/main.tex).
`submission/HW4_Hanyu_Zhang_FINCB9339.tex` is a matching local convenience copy,
ignored by Git. The source references the project's figures with relative paths.
`submission/research_project.zip` is the optional complete local handoff archive,
also ignored by Git; it includes the report source, compiled report, original
inputs, reference PDFs, Python code, tests and numerical outputs.

## Main results

- The exact arithmetic inverse return is `-R/(1+R)`; gross returns, rather than
  net returns, are reciprocal. A second-order mean and leading-order variance
  approximation use only the original mean and variance.
- On 2,980 return dates, the centered inverse-mean errors are −0.00762 and
  +0.00876 basis points/day for the two directions. Relative variance errors are
  −1.35172% and +1.32057%. These are approximation errors, not performance estimates.
- The Rule of 72 equals exact fractional doubling time at **7.84687% per period**,
  implying **9.17563 periods**. Five approximations are compared on the same rate grid.
- Jurek's put quantity insures the foreign deposit at maturity, including its
  initial delta-hedging position. The resulting funded call representation gives
  the floor and steeper terminal upside. Omitting the delta hedge retains the put;
  a zero strike additionally removes the protection.

## Reproduce from this project root

Use the existing shared course interpreter, **`$HOME/.venvs/sys-inv/bin/python`**.
Do not create `.venv` or `venv`, run `uv sync`, or synchronize this environment to
the recorded dependency versions. If a required package is missing, install only
that package with `uv pip install --python "$HOME/.venvs/sys-inv/bin/python" PACKAGE`.
`pyproject.toml` lists requirements; `requirements-lock.txt` records the versions
used. No network or new market-data acquisition is needed for the analysis.

```sh
"$HOME/.venvs/sys-inv/bin/python" -c 'import sys; print(sys.executable)'
"$HOME/.venvs/sys-inv/bin/python" -m src.run
"$HOME/.venvs/sys-inv/bin/python" -m src.verify
"$HOME/.venvs/sys-inv/bin/python" -m pytest -q > results/verification/pytest.txt
"$HOME/.venvs/sys-inv/bin/python" -m src.report
tectonic --keep-logs report/main.tex
"$HOME/.venvs/sys-inv/bin/python" -m src.validate_report
# Inspect every page of report/main.pdf before recording visual review:
"$HOME/.venvs/sys-inv/bin/python" -m src.package --record-reviewed
```

Tectonic 0.17.0 compiled the delivered PDF. A standard TeX installation can instead
run `pdflatex main.tex` twice from `report/`. The report uses standard article,
amsmath/amssymb, geometry, booktabs, array, graphicx, float, microtype, hyperref packages. A compiler is unnecessary to read the delivered PDF or reproduce
numerical results. Optional previews can be rendered with
`pdftoppm -png report/main.pdf tmp/pdfs/report` after creating `tmp/pdfs/`.

`src.package` requires successful mathematical/report checks and a visual review
record matching the compiled PDF. Use `--record-reviewed` only after inspecting
all pages. It refreshes the submission PDF, ignored LaTeX copy, concise handoff
record, file-integrity manifest and ZIP archive.

## Method choices and source provenance

1. **Input workbook.** Question 1(c) refers to the HW3 data by a shortened filename.
   This project uses an unchanged copy of the previously supplied
   `hw3.data.carry.FX.dly.xlsx`, worksheet `Data`, second-row headers. NZD is USD per
   NZD; JPY is JPY per USD. NZD/JPY is their product, in JPY per NZD. The opposite
   direction is its reciprocal. Source paths and SHA-256 hashes are in
   [data/manifest.json](data/manifest.json). The original HW3 project is not a runtime
   dependency and is not changed.
2. **Dates and moments.** All 2,981 supplied levels are retained, including holidays.
   Consecutive-date arithmetic spot returns give 2,980 observations. No returns
   are fabricated for the first date, no spot levels are imputed, and no funding
   is added to the quotation-inversion exercise. Means/variances are daily and
   unannualized; empirical-distribution variance uses divisor N. The unbiased
   N−1 alternative is also exported, clearly labeled.
3. **Moment approximations.** The mean uses a second-order Taylor expansion around
   the observed mean; variance retains the linear random term. A polynomial
   variance involving third/fourth moments is additional explanatory evidence,
   not a complete higher-order approximation using only the first two moments.
4. **Five doubling approximations.** The two approximation families are
   `L/r` and `L*(1/r+1/2)`, each evaluated using `L=ln(2)` or `L=0.69`, plus
   the Rule of 72. This interprets the handout's five-approximation request as four
   derived formulas and the original rule. Rates are decimal r, percentage p=100r,
   and the rule is `72/p`. Doubling times are fractional periods; first actual
   integer-period doubling is their ceiling. Grid: 0.1%–50%, step 0.01 percentage
   points. No fitted coefficients or optimized approximations are introduced.
5. **Option overlay.** The signed put delta is negative, the initial hedge is static,
   the premium and foreign deposit are funded in currency I, and the position-size
   denominator must be positive. The numerical payoff plot is illustrative,
   with disclosed lognormal FX-pricing parameters; it is not a historical hedge
   backtest or an estimate of a carry premium.

## Project map

| Location | Contents |
|---|---|
| `data/raw/`, `references/` | Unchanged workbook, assignment and Jurek paper |
| `src/fx.py` | Cross rates, return inversion and moment approximations |
| `src/doubling.py` | Five formulas, exact doubling time and unique Rule of 72 root |
| `src/options.py` | Funded initial delta hedge, option quantity, payoff and floor |
| `src/run.py` | Tables, daily time series, figures and dependency record |
| `src/verify.py` | Separate Decimal/scalar reconstruction, without production finance imports |
| `src/report.py`, `src/validate_report.py` | LaTeX and source-specific numerical bindings |
| `src/package.py` | Final local handoff and integrity manifest |
| `tests/` | Return-domain, approximation-order, compounding and option-exposure tests |
| `results/timeseries/` | Cross levels, daily arithmetic returns and illustrative option payoffs |
| `results/tables/` | Empirical moments, both-direction errors, five-method sensitivity and root |
| `results/figures/` | Three vector PDF figures, all included in the report |
| `results/verification/` | Source integrity, representative dates, reconstruction and report records |
| `report/` | Canonical LaTeX and compiled local build |
| `submission/` | Final PDF, ignored source copy and complete handoff archive |

## Verification scope and limitations

The separate reconstruction reads the workbook directly through openpyxl and
recomputes every daily cross return with Decimal arithmetic. It also reconstructs
moments, all five approximations at representative rates, the optimal rate by
bisection, FX put–call parity, hedge sizing and every illustrative payoff. It
performs 9,642 scalar comparisons; 24 focused pytest cases pass. Technical records
are kept outside the academic PDF.

The inverse-moment formulas are local approximations, not an identification result
from two moments. Near −100% returns, inverse moments can be unstable or infinite.
The 72-rule intersection depends on fractional-time and rate-unit conventions.
Jurek's option floor assumes the disclosed funding, settlement and static-position
conventions; matching initial delta is not a universal guarantee of a better floor.
