#!/usr/bin/env bash

set -e
set -x

isort --check-only --src=fastapi_cdn_host .
black --check --fast .
ruff .
mypy .
bandit -r fastapi_cdn_host
echo Done. ✨ 🍰 ✨ 
