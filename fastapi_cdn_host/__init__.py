from .client import AssetUrl, CdnHostEnum, CdnHostItem, monkey_patch_for_docs_ui
from .utils import today_lock, weekday_lock

patch_docs = monkey_patch = monkey_patch_for_docs_ui
__version__ = "0.7.5"
__all__ = (
    "__version__",
    "AssetUrl",
    "CdnHostEnum",
    "CdnHostItem",
    "monkey_patch",
    "monkey_patch_for_docs_ui",
    "patch_docs",
    "today_lock",
    "weekday_lock",
)
