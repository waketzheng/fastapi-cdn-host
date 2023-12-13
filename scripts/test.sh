#!/usr/bin/env bash

set -e
set -x

cd tests/online_cdn && coverage run -m pytest test_*.py
cd ../favicon_online_cdn && coverage run -m pytest test_*.py
cd ../static_auto && coverage run -m pytest test_*.py
cd ../static_mounted && coverage run -m pytest test_*.py
cd ../custom_static_root && coverage run -m pytest test_*.py
cd ../static_with_favicon && coverage run -m pytest test_*.py
cd ../defined_root_path && coverage run -m pytest test_*.py
cd ../http_race && coverage run -m pytest test_*.py
cd ../.. && coverage combine tests/*/.coverage
coverage report -m
