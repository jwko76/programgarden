"""Pydantic models for LS Securities OpenAPI t8424 (전체업종(t8424)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8424RequestHeader(BlockRequestHeader):
    pass


class T8424ResponseHeader(BlockResponseHeader):
    pass

class T8424InBlock(BaseModel):
    """t8424InBlock — input block. 기본입력"""

    gubun1: str = Field(
        ...,
        title="구분1",
        description="gubun1 — char(1). Consume as returned by LS.",
    )

class T8424OutBlock(BaseModel):
    """t8424OutBlock — output block (occurs — list of rows). 출력"""

    hname: str = Field(
        default="",
        title="업종명",
        description="hname — char(20). Consume as returned by LS.",
    )
    upcode: str = Field(
        default="",
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )

class T8424Request(BaseModel):
    """Request envelope for t8424."""

    header: T8424RequestHeader = T8424RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8424",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8424",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8424Response(BaseModel):
    """Response envelope for t8424."""

    header: Optional[T8424ResponseHeader] = None
    block: List[T8424OutBlock] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8424RequestHeader",
    "T8424ResponseHeader",
    "T8424InBlock",
    "T8424OutBlock",
    "T8424Request",
    "T8424Response",
]