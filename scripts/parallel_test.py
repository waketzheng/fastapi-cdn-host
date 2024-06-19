#!/usr/bin/env python
"""
Run test_*.py files in tests/ with multi processes
"""

import concurrent.futures
import os
import sys
from pathlib import Path

WORK_DIR = Path(__file__).parent.parent


def main() -> int:
    ds = [p.name for p in Path("tests").glob("*") if p.is_dir()]
    cmd = "coverage run -m pytest -s test_*.py"
    res = 0
    with concurrent.futures.ProcessPoolExecutor() as executor:
        future_to_folder = {
            executor.submit(os.system, f"cd tests/{d} && {cmd}"): d for d in ds
        }
        for future in concurrent.futures.as_completed(future_to_folder):
            folder = future_to_folder[future]
            try:
                rc = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (folder, exc))
            else:
                print("%r page is %d" % (folder, rc))
            res += rc
    return res


if __name__ == "__main__":
    sys.exit(main())
