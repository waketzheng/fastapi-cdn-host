import os
import shutil
from pathlib import Path

import pytest


def ensure_not_exist(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
        print(f"{path} removed.")


@pytest.fixture(scope="session", autouse=True)
def prepare():
    static_root = Path(__file__).parent / "static"
    ensure_not_exist(static_root)
    rc = os.system("fastcdn offline")
    assert rc == 0
    assert static_root.exists()
    yield
    ensure_not_exist(static_root)
