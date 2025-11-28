import os
import sys
from pathlib import Path

import pytest

if sys.version_info >= (3, 11):
    from contextlib import chdir
else:
    from contextlib import contextmanager

    @contextmanager
    def chdir(dst: Path):
        src = Path.cwd()
        os.chdir(dst)
        try:
            yield
        finally:
            os.chdir(src)


@pytest.fixture
def tmp_workdir(tmp_path):
    with chdir(tmp_path):
        yield
