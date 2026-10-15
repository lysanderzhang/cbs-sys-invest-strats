# Updated HW2 investor presentation

The preferred compiled deck is `../../submission/Investor_Presentation.pdf`.
This source folder contains the editable LaTeX, generated numerical tables and
macros, vector figures, speaker notes, and asset/rendering scripts. Its financial
content and the delivered PDF are preserved during project restructuring.

From `homework2/`:

```sh
cd report/presentation
"$HOME/.venvs/sys-inv/bin/python" scripts/build_assets.py
pdflatex -output-directory=../../submission Investor_Presentation.tex
pdflatex -output-directory=../../submission Investor_Presentation.tex
sh scripts/render_pages.sh build/pages
```

The default data source is `../../results/tables/`; `--tables` can override it.
The asset builder checks frozen headline performance/capacity figures and chart
drawdowns against the preserved CSVs. It does not rerun the investment models or
fetch data. Use only the existing shared FINCB9339 Python environment; install
missing packages with `uv pip install --python "$HOME/.venvs/sys-inv/bin/python" <packages>`.
Do not create a local environment or synchronize shared dependencies to a lock file.

The deck uses Beamer's 16:9 layout on a 192mm × 108mm canvas. Its TeX dependencies
include beamer, lmodern, amsmath, amssymb, booktabs, tabularx, array, colortbl,
xcolor, graphicx, tikz, microtype and geometry. The chart script uses pandas and
matplotlib; Latin Modern fonts are preferred, with DejaVu Serif as fallback.
`pdftoppm` is needed only for optional page rendering. The existing PDF can be
reviewed directly without installing any build dependencies.
