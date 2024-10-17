#!/usr/bin/env bash

set -e
set -x

[ -f pyproject.toml ] || ([ -f ../pyproject.toml ] && cd ..)

RUFF=ruff
if ! [ -x "$(command -v ruff)" ]; then
    poetry run ruff --version || poetry install
    RUFF="poetry run ruff"
fi
$RUFF check --extend-select=I,B,SIM .
$RUFF format --check .

MYPY="dmypy run"
if ! [ -x "$(command -v dmypy)" ]; then
    MYPY="poetry run dmypy run"
fi
$MYPY .

BANDIT=bandit
if ! [ -x "$(command -v bandit)" ]; then
    BANDIT="poetry run bandit"
fi
$BANDIT -r fastapi_cdn_host

echo Done. ✨ 🍰 ✨
