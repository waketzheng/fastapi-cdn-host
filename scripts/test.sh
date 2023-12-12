#!/usr/bin/env bash

set -e
set -x

coverage run -m pytest tests/online_cdn
coverage run -m pytest tests/favicon_online_cdn
cd tests/static_auto && coverage run -m pytest test_*.py
cd ../static_mounted && coverage run -m pytest test_*.py
cd ../custom_static_root && coverage run -m pytest test_*.py
cd ../static_with_favicon && coverage run -m pytest test_*.py
cd ../defined_root_path && coverage run -m pytest test_*.py
cd ../.. && coverage combine
coverage report -m
