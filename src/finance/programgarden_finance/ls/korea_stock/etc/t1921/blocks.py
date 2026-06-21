"""Pydantic models for LS Securities OpenAPI t1921 (신용거래동향(t1921)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1921RequestHeader(BlockRequestHeader):
    pass


class T1921ResponseHeader(BlockResponseHeader):
    pass

class T1921InBlock(BaseModel):
    """t1921InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="융자대주구분",
        description="gubun — char(1). Consume as returned by LS.",
    )
    date: str = Field(
        ...,
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    idx: int = Field(
        ...,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1921OutBlock(BaseModel):
    """t1921OutBlock — output block. 출력"""

    cnt: int = Field(
        default=0,
        title="CNT",
        description="cnt — long(4). Consume as returned by LS.",
    )
    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1921OutBlock1(BaseModel):
    """t1921OutBlock1 — output block (occurs — list of rows). 출력1"""

    mmdate: str = Field(
        default="",
        title="날짜",
        description="mmdate — char(8). Consume as returned by LS.",
    )
    close: int = Field(
        default=0,
        title="종가",
        description="close — long(8). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    jchange: int = Field(
        default=0,
        title="전일대비",
        description="jchange — long(8). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    nvolume: int = Field(
        default=0,
        title="신규",
        description="nvolume — long(8). Consume as returned by LS.",
    )
    svolume: int = Field(
        default=0,
        title="상환",
        description="svolume — long(8). Consume as returned by LS.",
    )
    jvolume: int = Field(
        default=0,
        title="잔고",
        description="jvolume — long(8). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="금액",
        description="price — long(8). Consume as returned by LS.",
    )
    change: int = Field(
        default=0,
        title="대비",
        description="change — long(8). Consume as returned by LS.",
    )
    gyrate: float = Field(
        default=0.0,
        title="공여율",
        description="gyrate — float(6.2). Consume as returned by LS.",
    )
    jkrate: float = Field(
        default=0.0,
        title="잔고율",
        description="jkrate — float(6.2). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1921Request(BaseModel):
    """Request envelope for t1921."""

    header: T1921RequestHeader = T1921RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1921",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1921",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1921Response(BaseModel):
    """Response envelope for t1921."""

    header: Optional[T1921ResponseHeader] = None
    block: Optional[T1921OutBlock] = None
    block1: List[T1921OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1921RequestHeader",
    "T1921ResponseHeader",
    "T1921InBlock",
    "T1921OutBlock",
    "T1921OutBlock1",
    "T1921Request",
    "T1921Response",
]