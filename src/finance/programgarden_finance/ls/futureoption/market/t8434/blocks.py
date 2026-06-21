"""Pydantic models for LS Securities OpenAPI t8434 (선물/옵션멀티현재가조회(t8434)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8434RequestHeader(BlockRequestHeader):
    pass


class T8434ResponseHeader(BlockResponseHeader):
    pass

class T8434InBlock(BaseModel):
    """t8434InBlock — input block. 기본입력"""

    qrycnt: int = Field(
        ...,
        title="건수",
        description="qrycnt — long(3). Consume as returned by LS.",
    )
    focode: str = Field(
        ...,
        title="단축코드",
        description="focode — char(400). Consume as returned by LS.",
    )

class T8434OutBlock1(BaseModel):
    """t8434OutBlock1 — output block (occurs — list of rows). 출력1"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(20). Consume as returned by LS.",
    )
    price: float = Field(
        default=0.0,
        title="현재가",
        description="price — float(6.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(6.2). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="누적거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    checnt: int = Field(
        default=0,
        title="체결건수",
        description="checnt — long(8). Consume as returned by LS.",
    )
    focode: str = Field(
        default="",
        title="단축코드",
        description="focode — char(8). Consume as returned by LS.",
    )

class T8434Request(BaseModel):
    """Request envelope for t8434."""

    header: T8434RequestHeader = T8434RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8434",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8434",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8434Response(BaseModel):
    """Response envelope for t8434."""

    header: Optional[T8434ResponseHeader] = None
    block1: List[T8434OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8434RequestHeader",
    "T8434ResponseHeader",
    "T8434InBlock",
    "T8434OutBlock1",
    "T8434Request",
    "T8434Response",
]