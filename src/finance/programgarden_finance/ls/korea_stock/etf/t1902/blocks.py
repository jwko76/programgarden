"""Pydantic models for LS Securities OpenAPI t1902 (ETF시간별추이(t1902)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1902RequestHeader(BlockRequestHeader):
    pass


class T1902ResponseHeader(BlockResponseHeader):
    pass

class T1902InBlock(BaseModel):
    """t1902InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    time: str = Field(
        ...,
        title="시간",
        description="time — char(6). Consume as returned by LS.",
    )

class T1902OutBlock(BaseModel):
    """t1902OutBlock — output block. 출력"""

    time: str = Field(
        default="",
        title="시간",
        description="time — char(6). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(20). Consume as returned by LS.",
    )
    upname: str = Field(
        default="",
        title="업종지수명",
        description="upname — char(20). Consume as returned by LS.",
    )

class T1902OutBlock1(BaseModel):
    """t1902OutBlock1 — output block (occurs — list of rows). 출력1"""

    time: str = Field(
        default="",
        title="시간",
        description="time — char(8). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="현재가",
        description="price — long(8). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: int = Field(
        default=0,
        title="전일대비",
        description="change — long(8). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="누적거래량",
        description="volume — float(12). Consume as returned by LS.",
    )
    navdiff: float = Field(
        default=0.0,
        title="NAV대비",
        description="navdiff — float(12.2). Consume as returned by LS.",
    )
    nav: float = Field(
        default=0.0,
        title="NAV",
        description="nav — float(12.2). Consume as returned by LS.",
    )
    navchange: float = Field(
        default=0.0,
        title="전일대비",
        description="navchange — float(12.2). Consume as returned by LS.",
    )
    crate: float = Field(
        default=0.0,
        title="추적오차",
        description="crate — float(9.2). Consume as returned by LS.",
    )
    grate: float = Field(
        default=0.0,
        title="괴리",
        description="grate — float(9.2). Consume as returned by LS.",
    )
    jisu: float = Field(
        default=0.0,
        title="지수",
        description="jisu — float(8.2). Consume as returned by LS.",
    )
    jichange: float = Field(
        default=0.0,
        title="전일대비",
        description="jichange — float(8.2). Consume as returned by LS.",
    )
    jirate: float = Field(
        default=0.0,
        title="전일대비율",
        description="jirate — float(8.2). Consume as returned by LS.",
    )

class T1902Request(BaseModel):
    """Request envelope for t1902."""

    header: T1902RequestHeader = T1902RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1902",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1902",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1902Response(BaseModel):
    """Response envelope for t1902."""

    header: Optional[T1902ResponseHeader] = None
    block: Optional[T1902OutBlock] = None
    block1: List[T1902OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1902RequestHeader",
    "T1902ResponseHeader",
    "T1902InBlock",
    "T1902OutBlock",
    "T1902OutBlock1",
    "T1902Request",
    "T1902Response",
]