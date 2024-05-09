#!/usr/bin/env bash

set -e
set -x

[ -f ../pyproject.toml ] && cd ..
ruff check --extend-select=I .
ruff format --check .
mypy .
bandit -r fastapi_cdn_host
echo Done. ✨ 🍰 ✨
