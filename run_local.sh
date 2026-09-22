#!/bin/zsh
set -eu
cd "${0:A:h}"
export PYTHONPATH="$PWD/.python-deps${PYTHONPATH:+:$PYTHONPATH}"
exec /Users/lysanzh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 strategy.py "$@"
