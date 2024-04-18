import importlib.metadata
from pathlib import Path

from .client import CdnHostEnum, CdnHostItem, monkey_patch_for_docs_ui

patch_docs = monkey_patch = monkey_patch_for_docs_ui
__version__ = importlib.metadata.version(Path(__file__).parent.name)
__all__ = (
    "__version__",
    "CdnHostEnum",
    "CdnHostItem",
    "monkey_patch",
    "monkey_patch_for_docs_ui",
    "patch_docs",
)
