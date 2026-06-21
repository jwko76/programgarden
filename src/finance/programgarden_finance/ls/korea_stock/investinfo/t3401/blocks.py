"""Pydantic models for LS Securities OpenAPI t3401 (투자의견(t3401)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T3401RequestHeader(BlockRequestHeader):
    pass


class T3401ResponseHeader(BlockResponseHeader):
    pass

class T3401InBlock(BaseModel):
    """t3401InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(9). Consume as returned by LS.",
    )
    gubun1: str = Field(
        ...,
        title="구분",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    tradno: str = Field(
        ...,
        title="회원사코드",
        description="tradno — char(3). Consume as returned by LS.",
    )
    cts_date: str = Field(
        ...,
        title="IDXDATE",
        description="cts_date — char(8). Consume as returned by LS.",
    )

class T3401OutBlock(BaseModel):
    """t3401OutBlock — output block. 출력"""

    cts_date: str = Field(
        default="",
        title="IDXDATE",
        description="cts_date — char(8). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="현재가",
        description="price — long(8). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="대비속성",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: int = Field(
        default=0,
        title="대비",
        description="change — long(8). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    value: int = Field(
        default=0,
        title="거래대금",
        description="value — long(12). Consume as returned by LS.",
    )

class T3401OutBlock1(BaseModel):
    """t3401OutBlock1 — output block (occurs — list of rows). 출력1"""

    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(9). Consume as returned by LS.",
    )
    tradno: str = Field(
        default="",
        title="회원사코드",
        description="tradno — char(3). Consume as returned by LS.",
    )
    date: str = Field(
        default="",
        title="의견일자",
        description="date — char(8). Consume as returned by LS.",
    )
    tradname: str = Field(
        default="",
        title="회원사명",
        description="tradname — char(30). Consume as returned by LS.",
    )
    bopn: str = Field(
        default="",
        title="투자의견변경후",
        description="bopn — char(30). Consume as returned by LS.",
    )
    nopn: str = Field(
        default="",
        title="투자의견변경전",
        description="nopn — char(30). Consume as returned by LS.",
    )
    boga: int = Field(
        default=0,
        title="목표가변경전",
        description="boga — long(12). Consume as returned by LS.",
    )
    noga: int = Field(
        default=0,
        title="목표가변경후",
        description="noga — long(12). Consume as returned by LS.",
    )
    close: int = Field(
        default=0,
        title="의견일종가",
        description="close — long(8). Consume as returned by LS.",
    )

class T3401Request(BaseModel):
    """Request envelope for t3401."""

    header: T3401RequestHeader = T3401RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t3401",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t3401",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T3401Response(BaseModel):
    """Response envelope for t3401."""

    header: Optional[T3401ResponseHeader] = None
    block: Optional[T3401OutBlock] = None
    block1: List[T3401OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T3401RequestHeader",
    "T3401ResponseHeader",
    "T3401InBlock",
    "T3401OutBlock",
    "T3401OutBlock1",
    "T3401Request",
    "T3401Response",
]