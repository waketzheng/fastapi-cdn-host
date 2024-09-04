#!/bin/sh -e
set -x

[ -f ../pyproject.toml ] && cd ..
ruff format fastapi_cdn_host examples
ruff check --fix fastapi_cdn_host examples
