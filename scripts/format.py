#!/usr/bin/env python
"""
Run `ruff format` to make style and `ruff check --fix` to remove unused imports

Usage:
    ./scripts/format.py

"""

import os
import shlex
import subprocess
import sys
from pathlib import Path

CMD = "fast lint"
TOOL = ("poetry", "pdm", "")[0]
work_dir = Path(__file__).parent.resolve().parent
if Path.cwd() != work_dir:
    os.chdir(str(work_dir))

cmd = (TOOL and f"{TOOL} run ") + CMD
r = subprocess.run(shlex.split(cmd), env=dict(os.environ, SKIP_MYPY="1"))
sys.exit(None if r.returncode == 0 else 1)
