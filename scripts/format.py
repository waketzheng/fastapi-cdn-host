#!/usr/bin/env python
"""
Run `ruff format` to make style and `ruff check --fix` to remove unused imports

Usage:
    ./scripts/format.py

"""

import os
import sys

PREPARE = "poetry run ruff --version || poetry install"
CMD = "ruff format . && ruff check --fix --extend-select=I,B,SIM ."
TOOL = ("poetry", "pdm", "")[0]

parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

# Ensure lint tools installed
for cmd in PREPARE.split("||"):
    if os.system(cmd.strip()) == 0:
        break

# Reformat files
prefix = TOOL and "{} run ".format(TOOL)
for cmd in CMD.split("&&"):
    if os.system(prefix + cmd.strip()) != 0:
        sys.exit(1)
