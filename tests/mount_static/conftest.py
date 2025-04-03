import shutil
from pathlib import Path

import pytest


def _remove_dirs(ps: list[Path]) -> None:
    for p in ps:
        if p.exists():
            shutil.rmtree(p)


@pytest.fixture(scope="session")
def clean_folders():
    ds = ("static", "media", "pictures", "assets")
    ps = [Path(__file__).parent / name for name in ds]
    _remove_dirs(ps)
    yield
    _remove_dirs(ps)
