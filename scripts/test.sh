#!/usr/bin/env bash

set -e
set -x

python tests/prepare_media.py

directories=`python -c 'from pathlib import Path;ds=[p.name for p in Path("tests").glob("*") if p.is_dir()];print(" ".join(ds))'`

cd tests/online_cdn
for folder in $directories
do
    cd ../$folder && coverage run -m pytest -s test_*.py
done

cd ../.. && coverage combine tests/*/.coverage
coverage report -m
