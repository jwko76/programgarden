"""Pydantic models for LS Securities OpenAPI t1764 (회원사리스트(t1764)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1764RequestHeader(BlockRequestHeader):
    pass


class T1764ResponseHeader(BlockResponseHeader):
    pass

class T1764InBlock(BaseModel):
    """t1764InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    gubun1: str = Field(
        ...,
        title="구분1",
        description="gubun1 — char(1). Consume as returned by LS.",
    )

class T1764OutBlock(BaseModel):
    """t1764OutBlock — output block (occurs — list of rows). 출력1"""

    rank: int = Field(
        default=0,
        title="순위",
        description="rank — long(4). Consume as returned by LS.",
    )
    tradno: str = Field(
        default="",
        title="거래원번호",
        description="tradno — char(3). Consume as returned by LS.",
    )
    tradname: str = Field(
        default="",
        title="거래원이름",
        description="tradname — char(20). Consume as returned by LS.",
    )

class T1764Request(BaseModel):
    """Request envelope for t1764."""

    header: T1764RequestHeader = T1764RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1764",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1764",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1764Response(BaseModel):
    """Response envelope for t1764."""

    header: Optional[T1764ResponseHeader] = None
    block: List[T1764OutBlock] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1764RequestHeader",
    "T1764ResponseHeader",
    "T1764InBlock",
    "T1764OutBlock",
    "T1764Request",
    "T1764Response",
]