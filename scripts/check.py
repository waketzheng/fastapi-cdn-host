#!/usr/bin/env python
"""
Check style by `ruff` and verify type hints by `mypy`,
then run `bandit -r <package>` to find security issue.


Usage::
    ./scripts/check.py

"""

import os
import sys

PREPARE = "poetry run ruff --version || poetry install"
CMD = "ruff format --check . && ruff check . && dmypy run . && bandit -c pyproject.toml -r ."
TOOL = ("poetry", "pdm", "")[0]

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

# Ensure lint tools installed
for cmd in PREPARE.split("||"):
    if os.system(cmd.strip()) == 0:
        break

# Run lints
prefix = TOOL and "{} run ".format(TOOL)
for cmd in CMD.split("&&"):
    if os.system(prefix + cmd.strip()) == 0:
        continue
    if "ruff" in cmd:
        print(
            "\033[1m Please run './scripts/format.py' to auto-fix style issues \033[0m"
        )
    sys.exit(1)

print("Done. ✨ 🍰 ✨")
