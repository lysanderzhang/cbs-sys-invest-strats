# FINCB9339 Python environment policy

Use the existing shared course interpreter `$HOME/.venvs/sys-inv/bin/python` for all Python execution across HW1, HW2, HW3 and other course assignments. Verify `sys.executable` before work.

- Do not create project-local `.venv` or `venv`, especially in OneDrive.
- Install only missing packages with `uv pip install --python "$HOME/.venvs/sys-inv/bin/python" <packages>`.
- Do not run `uv sync` in homework projects.
- Do not unnecessarily upgrade, replace or uninstall shared dependencies.
- Keep dependency specifications for reproducibility, but do not synchronize the shared environment to a homework lock file.
- Keep environments outside OneDrive and coursework files in their respective project directories.
- Inspect and verify a redundant local environment's location and contents before removing it.
