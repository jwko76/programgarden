"""Pydantic models for LS Securities OpenAPI t3518 (해외실시간지수(t3518)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T3518RequestHeader(BlockRequestHeader):
    pass


class T3518ResponseHeader(BlockResponseHeader):
    pass

class T3518InBlock(BaseModel):
    """t3518InBlock — input block. 입력"""

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
    cnt: int = Field(
        ...,
        title="입력건수",
        description="cnt — long(4). Consume as returned by LS.",
    )
    jgbn: str = Field(
        ...,
        title="조회구분",
        description="jgbn — char(1). Consume as returned by LS.",
    )
    nmin: int = Field(
        ...,
        title="N분",
        description="nmin — long(3). Consume as returned by LS.",
    )
    cts_date: str = Field(
        ...,
        title="CTS_DATE",
        description="cts_date — char(8). Consume as returned by LS.",
    )
    cts_time: str = Field(
        ...,
        title="CTS_TIME",
        description="cts_time — char(6). Consume as returned by LS.",
    )

class T3518OutBlock(BaseModel):
    """t3518OutBlock — output block. 단일출력"""

    cts_date: str = Field(
        default="",
        title="CTS_DATE",
        description="cts_date — char(8). Consume as returned by LS.",
    )
    cts_time: str = Field(
        default="",
        title="CTS_TIME",
        description="cts_time — char(6). Consume as returned by LS.",
    )

class T3518OutBlock1(BaseModel):
    """t3518OutBlock1 — output block (occurs — list of rows). 멀티출력"""

    date: str = Field(
        default="",
        title="일자",
        description="date — char(8). Consume as returned by LS.",
    )
    time: str = Field(
        default="",
        title="시간",
        description="time — char(8). Consume as returned by LS.",
    )
    open: float = Field(
        default=0.0,
        title="시가",
        description="open — double(9.4). Consume as returned by LS.",
    )
    high: float = Field(
        default=0.0,
        title="고가",
        description="high — double(9.4). Consume as returned by LS.",
    )
    low: float = Field(
        default=0.0,
        title="저가",
        description="low — double(9.4). Consume as returned by LS.",
    )
    price: float = Field(
        default=0.0,
        title="현재가",
        description="price — double(9.4). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — double(9.4). Consume as returned by LS.",
    )
    uprate: float = Field(
        default=0.0,
        title="등락율",
        description="uprate — double(9.4). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="누적거래량",
        description="volume — double(12.0). Consume as returned by LS.",
    )
    bidho: float = Field(
        default=0.0,
        title="매수호가",
        description="bidho — double(9.4). Consume as returned by LS.",
    )
    offerho: float = Field(
        default=0.0,
        title="매도호가",
        description="offerho — double(9.4). Consume as returned by LS.",
    )
    bidrem: float = Field(
        default=0.0,
        title="매수잔량",
        description="bidrem — double(12.0). Consume as returned by LS.",
    )
    offerrem: float = Field(
        default=0.0,
        title="매도잔량",
        description="offerrem — double(12.0). Consume as returned by LS.",
    )
    kind: str = Field(
        default="",
        title="종목종류",
        description="kind — char(1). Consume as returned by LS.",
    )
    symbol: str = Field(
        default="",
        title="SYMBOL",
        description="symbol — char(16). Consume as returned by LS.",
    )
    exid: str = Field(
        default="",
        title="EXID",
        description="exid — char(4). Consume as returned by LS.",
    )
    kodate: str = Field(
        default="",
        title="한국일자",
        description="kodate — char(8). Consume as returned by LS.",
    )
    kotime: str = Field(
        default="",
        title="한국시간",
        description="kotime — char(8). Consume as returned by LS.",
    )

class T3518Request(BaseModel):
    """Request envelope for t3518."""

    header: T3518RequestHeader = T3518RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t3518",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t3518",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T3518Response(BaseModel):
    """Response envelope for t3518."""

    header: Optional[T3518ResponseHeader] = None
    block: Optional[T3518OutBlock] = None
    block1: List[T3518OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T3518RequestHeader",
    "T3518ResponseHeader",
    "T3518InBlock",
    "T3518OutBlock",
    "T3518OutBlock1",
    "T3518Request",
    "T3518Response",
]