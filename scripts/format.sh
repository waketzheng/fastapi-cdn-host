#!/bin/sh -e
set -x

[ -f pyproject.toml ] || ([ -f ../pyproject.toml ] && cd ..)

RUFF=ruff
if ! [ -x "$(command -v ruff)" ]; then
    poetry run ruff --version || poetry install
    RUFF="poetry run ruff"
fi
$RUFF format .
$RUFF check --fix --extend-select=I,B,SIM .
