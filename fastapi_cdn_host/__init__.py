import importlib.metadata
from pathlib import Path

from .client import CdnHostEnum, monkey_patch_for_docs_ui

monkey_patch = monkey_patch_for_docs_ui
__version__ = importlib.metadata.version(Path(__file__).parent.name)
__all__ = ("__version__", "CdnHostEnum", "monkey_patch", "monkey_patch_for_docs_ui")
