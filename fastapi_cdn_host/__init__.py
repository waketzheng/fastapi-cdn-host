from .client import (
    AssetUrl,
    CdnHostEnum,
    CdnHostItem,
    monkey_patch_for_docs_ui,
    mount_static,
    patch_docs,
)
from .utils import today_lock, weekday_lock

monkey_patch = monkey_patch_for_docs_ui
__version__ = "0.10.1"
__all__ = (
    "AssetUrl",
    "CdnHostEnum",
    "CdnHostItem",
    "__version__",
    "monkey_patch",
    "monkey_patch_for_docs_ui",
    "mount_static",
    "patch_docs",
    "today_lock",
    "weekday_lock",
)
