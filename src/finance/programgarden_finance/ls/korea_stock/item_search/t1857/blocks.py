"""Pydantic models for LS Securities OpenAPI t1857 (e종목검색(신버전API용)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1857RequestHeader(BlockRequestHeader):
    pass


class T1857ResponseHeader(BlockResponseHeader):
    pass

class T1857InBlock(BaseModel):
    """t1857InBlock — input block. In(*EMPTY*)"""


class T1857OutBlock(BaseModel):
    """t1857OutBlock — output block. Out(*EMPTY*)"""


class T1857OutBlock1(BaseModel):
    """t1857OutBlock1 — output block (occurs — list of rows). Out(*EMPTY*)"""


class T1857Request(BaseModel):
    """Request envelope for t1857."""

    header: T1857RequestHeader = T1857RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1857",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1857",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1857Response(BaseModel):
    """Response envelope for t1857."""

    header: Optional[T1857ResponseHeader] = None
    block: Optional[T1857OutBlock] = None
    block1: List[T1857OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1857RequestHeader",
    "T1857ResponseHeader",
    "T1857InBlock",
    "T1857OutBlock",
    "T1857OutBlock1",
    "T1857Request",
    "T1857Response",
]