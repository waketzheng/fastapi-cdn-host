#!/bin/sh -e
set -x

[ -f ../pyproject.toml ] && cd ..
fast lint fastapi_cdn_host examples
