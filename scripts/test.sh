#!/usr/bin/env bash

set -e
set -x

#export PYTHONPATH=./docs_src
pytest tests/online_cdn
pytest tests/favicon_online_cdn
