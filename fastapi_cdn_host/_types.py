from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    TypeVar,
    Union,
)

if sys.version_info >= (3, 11):
    from typing import ParamSpec, TypeVarTuple, Unpack
else:
    from typing_extensions import ParamSpec, TypeVarTuple, Unpack  # NOQA:F401

if TYPE_CHECKING:
    from fastapi import Request

    from .client import AssetUrl, CdnHostEnum

CdnPathInfoType = tuple[
    Annotated[str, "swagger-ui module path info(must startswith '/')"],
    Annotated[str, "redoc path or url info(must startswith '/')"],
]
CdnDomainType = Annotated[str, "Host for swagger-ui/redoc"]
StrictCdnHostInfoType = tuple[CdnDomainType, CdnPathInfoType]
CdnHostInfoType = Union[
    Annotated[CdnDomainType, "Will use DEFAULT_ASSET_PATH"],
    tuple[CdnDomainType, Annotated[str, "In case of swagger/redoc has the same path"]],
    StrictCdnHostInfoType,
]
DocsCdnHostType = Union[
    Path, "CdnHostEnum", str, list[CdnHostInfoType], CdnHostInfoType
]
ExtendCdnHostType = Union[
    Path, "CdnHostEnum", "AssetUrl", list[CdnHostInfoType], CdnHostInfoType
]
T_Retval = TypeVar("T_Retval")
PosArgsT = TypeVarTuple("PosArgsT")
LockFunc = Callable[["Request"], Any]
P = ParamSpec("P")
