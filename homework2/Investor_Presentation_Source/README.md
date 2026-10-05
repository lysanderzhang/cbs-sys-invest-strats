# Investor presentation: build instructions

Author: Hanyu Zhang, Columbia University. October 5, 2026.

This folder is separate from the original research package. It reads the package's canonical CSVs and changes nothing in it.

## Layout

```
Investor_Presentation_Source/
  Investor_Presentation.tex     Beamer source (16:9, 11pt, Latin Modern)
  Investor_Presentation.pdf     compiled deck: 12 main slides + appendix contents + 8 appendix slides
  scripts/build_assets.py   CSV -> generated/*.tex tables and macros, figures/*.pdf charts, with checks
  scripts/render_pages.sh   renders every page to PNG for visual QA
  generated/                number macros, table bodies, verification.json (all script-generated)
  figures/                  vector charts (script-generated)
  Presenter_Notes.md        brief notes for every slide and likely questions
  CHANGELOG.md              what changed relative to the original presentation
```

## Build

The script expects the original package beside this folder (`../hw2_momentum/outputs/tables`). Pass `--tables` to point elsewhere.

```bash
cd Investor_Presentation_Source
python3 scripts/build_assets.py            # or: --tables /path/to/hw2_momentum/outputs/tables
pdflatex Investor_Presentation.tex
pdflatex Investor_Presentation.tex             # second pass for stable references
sh scripts/render_pages.sh build/pages     # optional visual QA
```

`build_assets.py` stops with an error if any frozen headline value (B1, B2, B3 and 60/40 CAGR, Sharpe and maximum daily drawdown; B3 turnover; peak DBC participation) or any chart drawdown disagrees with `performance.csv` / `capacity_summary.csv`.

## Requirements

- Python 3.10+ with pandas and matplotlib (tested: Python 3.13, pandas 3.0, matplotlib 3.11).
- Latin Modern fonts: the charts use the OpenType files (`fonts-lmodern` / `lmodern` package, `lmroman*.otf`). If they are missing, matplotlib falls back to DejaVu Serif.
- TeX Live with pdflatex and these packages: beamer, lmodern, amsmath, amssymb, booktabs, tabularx, array, colortbl, xcolor, graphicx, tikz (arrows.meta, positioning), microtype, geometry. On Debian/Ubuntu: `texlive-latex-recommended texlive-latex-extra texlive-pictures lmodern`.
- poppler-utils (`pdftoppm`) only for page rendering.

## Page size

The deck uses Beamer's 16:9 aspect ratio on a 192 mm × 108 mm canvas (`\geometry{papersize={192mm,108mm}}`) with an 11pt base font. That keeps tables readable without shrinking them below footnote size. Delete that line to return to Beamer's default 160 mm × 90 mm; several slides would then need trimming.
