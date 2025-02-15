import shutil
import subprocess
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import pytest


@contextmanager
def ensure_not_exist(path: Path) -> Generator:
    if path.exists():
        shutil.rmtree(path)
        print(f"{path} removed.")
    try:
        yield
    finally:
        if path.exists():
            shutil.rmtree(path)


@pytest.fixture(scope="session", autouse=True)
def prepare():
    static_root = Path(__file__).parent / "static"
    with ensure_not_exist(static_root):
        r = subprocess.run(["fastcdn", "offline"])
        assert r.returncode == 0
        assert static_root.exists()
        yield
