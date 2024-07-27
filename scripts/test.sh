#!/usr/bin/env bash

set -e
set -x

[ -f ../pyproject.toml ] && cd ..
WORK_DIR="$PWD"
python tests/prepare_media.py

if [[ "$1" == '--no-parallel' ]]; then
    directories=`python -c 'from pathlib import Path;ds=[p.name for p in Path("tests").glob("*") if p.is_dir()];print(" ".join(ds))'`

    cd tests/online_cdn
    for folder in $directories
    do
        cd ../$folder && coverage run -m pytest -s test_*.py
    done
else
    python scripts/parallel_test.py
fi

for EG_DIR in 'examples/normal' 'examples/offline'
do
    cd $WORK_DIR/$EG_DIR
    coverage run -m pytest -s test_*.py
done

cd $WORK_DIR
coverage combine examples/*/.coverage tests/*/.coverage
coverage report -m
