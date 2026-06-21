"""Pydantic models for LS Securities OpenAPI t1514 (업종기간별추이(t1514)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1514RequestHeader(BlockRequestHeader):
    pass


class T1514ResponseHeader(BlockResponseHeader):
    pass

class T1514InBlock(BaseModel):
    """t1514InBlock — input block. 기본입력"""

    upcode: str = Field(
        ...,
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )
    gubun1: str = Field(
        ...,
        title="구분1",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    gubun2: str = Field(
        ...,
        title="구분2",
        description="gubun2 — char(1). Consume as returned by LS.",
    )
    cts_date: str = Field(
        ...,
        title="CTS_일자",
        description="cts_date — char(8). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="조회건수",
        description="cnt — int(4). Consume as returned by LS.",
    )
    rate_gbn: str = Field(
        ...,
        title="비중구분",
        description="rate_gbn — char(1). Consume as returned by LS.",
    )

class T1514OutBlock(BaseModel):
    """t1514OutBlock — output block. 기본출력"""

    cts_date: str = Field(
        default="",
        title="CTS_일자",
        description="cts_date — char(8). Consume as returned by LS.",
    )

class T1514OutBlock1(BaseModel):
    """t1514OutBlock1 — output block (occurs — list of rows). 기본출력1"""

    date: str = Field(
        default="",
        title="일자",
        description="date — char(8). Consume as returned by LS.",
    )
    jisu: float = Field(
        default=0.0,
        title="지수",
        description="jisu — float(12.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(7.2). Consume as returned by LS.",
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
    diff_vol: float = Field(
        default=0.0,
        title="거래증가율",
        description="diff_vol — float(12.2). Consume as returned by LS.",
    )
    value1: int = Field(
        default=0,
        title="거래대금1",
        description="value1 — long(12). Consume as returned by LS.",
    )
    high: int = Field(
        default=0,
        title="상승",
        description="high — long(4). Consume as returned by LS.",
    )
    unchg: int = Field(
        default=0,
        title="보합",
        description="unchg — long(4). Consume as returned by LS.",
    )
    low: int = Field(
        default=0,
        title="하락",
        description="low — long(4). Consume as returned by LS.",
    )
    uprate: float = Field(
        default=0.0,
        title="상승종목비율",
        description="uprate — float(6.2). Consume as returned by LS.",
    )
    frgsvolume: int = Field(
        default=0,
        title="외인순매수",
        description="frgsvolume — long(8). Consume as returned by LS.",
    )
    openjisu: float = Field(
        default=0.0,
        title="시가",
        description="openjisu — float(12.2). Consume as returned by LS.",
    )
    highjisu: float = Field(
        default=0.0,
        title="고가",
        description="highjisu — float(12.2). Consume as returned by LS.",
    )
    lowjisu: float = Field(
        default=0.0,
        title="저가",
        description="lowjisu — float(12.2). Consume as returned by LS.",
    )
    value2: int = Field(
        default=0,
        title="거래대금2",
        description="value2 — long(12). Consume as returned by LS.",
    )
    up: int = Field(
        default=0,
        title="상한",
        description="up — long(4). Consume as returned by LS.",
    )
    down: int = Field(
        default=0,
        title="하한",
        description="down — long(4). Consume as returned by LS.",
    )
    totjo: int = Field(
        default=0,
        title="종목수",
        description="totjo — long(4). Consume as returned by LS.",
    )
    orgsvolume: int = Field(
        default=0,
        title="기관순매수",
        description="orgsvolume — long(8). Consume as returned by LS.",
    )
    upcode: str = Field(
        default="",
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )
    rate: float = Field(
        default=0.0,
        title="거래비중",
        description="rate — float(7.2). Consume as returned by LS.",
    )
    divrate: float = Field(
        default=0.0,
        title="업종배당수익률",
        description="divrate — float(7.2). Consume as returned by LS.",
    )

class T1514Request(BaseModel):
    """Request envelope for t1514."""

    header: T1514RequestHeader = T1514RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1514",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1514",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1514Response(BaseModel):
    """Response envelope for t1514."""

    header: Optional[T1514ResponseHeader] = None
    block: Optional[T1514OutBlock] = None
    block1: List[T1514OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1514RequestHeader",
    "T1514ResponseHeader",
    "T1514InBlock",
    "T1514OutBlock",
    "T1514OutBlock1",
    "T1514Request",
    "T1514Response",
]