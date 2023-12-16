#!/usr/bin/env bash

set -e
set -x

python tests/prepare_media.py
cd tests/online_cdn && coverage run -m pytest test_*.py
cd ../favicon_online_cdn && coverage run -m pytest test_*.py
cd ../static_auto && coverage run -m pytest test_*.py
cd ../static_mounted && coverage run -m pytest test_*.py
cd ../custom_static_root && coverage run -m pytest test_*.py
cd ../static_with_favicon && coverage run -m pytest test_*.py
cd ../defined_root_path && coverage run -m pytest test_*.py
cd ../http_race && coverage run -m pytest test_*.py
cd ../root_path_without_static && coverage run -m pytest test_*.py
cd ../static_favicon_without_swagger_ui && coverage run -m pytest test_*.py
cd ../private_cdn && coverage run -m pytest test_*.py
cd ../cdn_with_default_asset_path && coverage run -m pytest test_*.py
cd ../explicit_cdn_host && coverage run -m pytest test_*.py
cd ../simple_asset_path && coverage run -m pytest test_*.py

cd ../.. && coverage combine tests/*/.coverage
coverage report -m
