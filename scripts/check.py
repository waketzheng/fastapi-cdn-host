#!/usr/bin/env python
"""
Check style by `ruff` and verify type hints by `mypy`,
then run `bandit -r <package>` to find security issue.


Usage::
    ./scripts/check.py

"""

import os
import sys

CMD = "fast check"
TOOL = ("poetry", "pdm", "")[0]
BANDIT = True
parent = os.path.abspath(os.path.dirname(__file__))
work_dir = os.path.dirname(parent)
if os.getcwd() != work_dir:
    os.chdir(work_dir)

cmd = "{} run {}".format(TOOL, CMD) if TOOL else CMD
if os.system(cmd) != 0:
    print("\033[1m Please run './scripts/format.py' to auto-fix style issues \033[0m")
    sys.exit(1)

if BANDIT:
    package_name = os.path.basename(work_dir).replace("-", "_")
    cmd = "{}bandit -r {}".format(TOOL and f"{TOOL} run ", package_name)
    print("-->", cmd)
    if os.system(cmd) != 0:
        sys.exit(1)
print("Done. ✨ 🍰 ✨")
