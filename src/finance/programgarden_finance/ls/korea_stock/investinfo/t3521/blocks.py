"""Pydantic models for LS Securities OpenAPI t3521 (해외지수조회(API용)(t3521)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T3521RequestHeader(BlockRequestHeader):
    pass


class T3521ResponseHeader(BlockResponseHeader):
    pass

class T3521InBlock(BaseModel):
    """t3521InBlock — input block. 기본입력"""

    kind: str = Field(
        ...,
        title="종목종류",
        description="kind — char(1). Consume as returned by LS.",
    )
    symbol: str = Field(
        ...,
        title="SYMBOL",
        description="symbol — char(16). Consume as returned by LS.",
    )

class T3521OutBlock(BaseModel):
    """t3521OutBlock — output block. 출력"""

    symbol: str = Field(
        default="",
        title="심벌",
        description="symbol — char(16). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="지수명",
        description="hname — char(20). Consume as returned by LS.",
    )
    close: float = Field(
        default=0.0,
        title="지수",
        description="close — float(12.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="대비",
        description="change — float(6.2). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    date: str = Field(
        default="",
        title="일자",
        description="date — char(8). Consume as returned by LS.",
    )

class T3521Request(BaseModel):
    """Request envelope for t3521."""

    header: T3521RequestHeader = T3521RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t3521",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t3521",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T3521Response(BaseModel):
    """Response envelope for t3521."""

    header: Optional[T3521ResponseHeader] = None
    block: Optional[T3521OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T3521RequestHeader",
    "T3521ResponseHeader",
    "T3521InBlock",
    "T3521OutBlock",
    "T3521Request",
    "T3521Response",
]