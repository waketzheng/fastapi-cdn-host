#!/bin/sh -e
set -x

[ -f ../pyproject.toml ] && cd ..
ruff format fastapi_cdn_host examples
ruff check --fix --extend-select=I,B,SIM fastapi_cdn_host examples
