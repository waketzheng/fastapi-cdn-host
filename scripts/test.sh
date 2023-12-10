#!/usr/bin/env bash

set -e
set -x

pytest tests/online_cdn
pytest tests/favicon_online_cdn
cd tests/static_auto && pytest test_*.py
cd ../static_mounted && pytest test_*.py
cd ../custom_static_root && pytest test_*.py
cd ../static_with_favicon && pytest test_*.py
cd ../defined_root_path && pytest test_*.py
