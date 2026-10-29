# Columbia FINCB9339 — Systematic Investment Strategies

Hanyu Zhang · Fall 2026

This repository collects the course homework in numbered `homeworkN/` folders. Each homework keeps its own methods, dependencies, results, and reproduction instructions.

| Project | Subject | Start here |
|---|---|---|
| [Homework 1](homework1/) | SPY intraday strategy replication, Models A/B/C | [README](homework1/README.md) · [Submitted report](homework1/submission/HW1_Hanyu_Zhang_FINCB9339.pdf) · [Results and validation](homework1/report/RESULTS_AND_VALIDATION.md) · [Submitted workbook](homework1/submission/original_submitted/FINCB9339_HW1_Submission.xlsx) |
| [Homework 2](homework2/) | Crash-aware equity momentum and cross-asset ETF dual momentum | [README](homework2/README.md) · [Investor presentation](homework2/submission/Investor_Presentation.pdf) · [Complete project report](homework2/submission/HW2_Hanyu_Zhang_FINCB9339.pdf) |
| [Homework 3](homework3/) | Daily G10 FX carry and volatility conditioning | [README](homework3/README.md) · [Complete report with figure appendix](homework3/submission/HW3_Hanyu_Zhang_FINCB9339.pdf) |
| [Homework 4](homework4/) | Inverse FX returns, doubling-time approximations and crash-neutral carry | [README](homework4/README.md) · [Complete report](homework4/submission/HW4_Hanyu_Zhang_FINCB9339.pdf) |

## Working with the projects

Run each project's commands from its own directory. HW1 uses `homework1/requirements.txt`; HW2 uses `homework2/requirements.lock.txt`; HW3 uses `homework3/pyproject.toml` and `requirements-lock.txt`. All Python execution uses the existing shared `$HOME/.venvs/sys-inv/bin/python`. Do not create homework-local environments or run `uv sync`; install only missing packages with `uv pip install --python "$HOME/.venvs/sys-inv/bin/python" <packages>`. Dependency files document requirements and historical versions, not targets for replacing shared dependencies. See [AGENTS.md](AGENTS.md). Transient build files, generated ZIP packages and local market-data caches are excluded from Git. Final PDFs and canonical report sources are tracked. HW3 and HW4 also create Git-ignored submission source copies for convenience.

For future assignments, add `homework5/`, `homework6/`, and so on, with a project README and an entry in the table above. Keep assignment-specific code, data, and outputs inside the corresponding folder. The existing course environment stays outside OneDrive; root and homework dependency files are specifications only.

The repository includes historical research outputs and verification records, not a live trading system. Costs and capacity estimates have stated limitations. No trades or assignment submissions are performed by this repository.
