"""Pydantic models for LS Securities OpenAPI t1954 (ELW일별주가(t1954)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1954RequestHeader(BlockRequestHeader):
    pass


class T1954ResponseHeader(BlockResponseHeader):
    pass

class T1954InBlock(BaseModel):
    """t1954InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    date: str = Field(
        ...,
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="건수",
        description="cnt — long(3). Consume as returned by LS.",
    )

class T1954OutBlock(BaseModel):
    """t1954OutBlock — output block. 출력"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    bsjgubun: str = Field(
        default="",
        title="기초자산구분",
        description="bsjgubun — char(1). Consume as returned by LS.",
    )
    bscode: str = Field(
        default="",
        title="기초자산코드(현물)",
        description="bscode — char(6). Consume as returned by LS.",
    )
    bjcode: str = Field(
        default="",
        title="기초자산코드(지수)",
        description="bjcode — char(3). Consume as returned by LS.",
    )

class T1954OutBlock1(BaseModel):
    """t1954OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    open: int = Field(
        default=0,
        title="시가",
        description="open — long(8). Consume as returned by LS.",
    )
    high: int = Field(
        default=0,
        title="고가",
        description="high — long(8). Consume as returned by LS.",
    )
    low: int = Field(
        default=0,
        title="저가",
        description="low — long(8). Consume as returned by LS.",
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
    change: int = Field(
        default=0,
        title="전일대비",
        description="change — long(8). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — float(12). Consume as returned by LS.",
    )
    bsprice: int = Field(
        default=0,
        title="기초자산(현물)",
        description="bsprice — long(8). Consume as returned by LS.",
    )
    bjprice: float = Field(
        default=0.0,
        title="기초자산(지수)",
        description="bjprice — float(8.2). Consume as returned by LS.",
    )
    bsign: str = Field(
        default="",
        title="전일대비구분",
        description="bsign — char(1). Consume as returned by LS.",
    )
    bschange: int = Field(
        default=0,
        title="전일대비(현물)",
        description="bschange — long(8). Consume as returned by LS.",
    )
    bjchange: float = Field(
        default=0.0,
        title="전일대비(지수)",
        description="bjchange — float(8.2). Consume as returned by LS.",
    )
    bdiff: float = Field(
        default=0.0,
        title="등락율",
        description="bdiff — float(6.2). Consume as returned by LS.",
    )
    bvolume: float = Field(
        default=0.0,
        title="기초자산거래량",
        description="bvolume — float(12). Consume as returned by LS.",
    )
    parity: float = Field(
        default=0.0,
        title="패리티",
        description="parity — float(6.2). Consume as returned by LS.",
    )
    egearing: float = Field(
        default=0.0,
        title="e.기어링",
        description="egearing — float(6.2). Consume as returned by LS.",
    )
    premium: float = Field(
        default=0.0,
        title="프리미엄",
        description="premium — float(6.2). Consume as returned by LS.",
    )
    berate: float = Field(
        default=0.0,
        title="손익분기",
        description="berate — float(6.2). Consume as returned by LS.",
    )
    capt: float = Field(
        default=0.0,
        title="자본지지",
        description="capt — float(6.2). Consume as returned by LS.",
    )
    gearing: float = Field(
        default=0.0,
        title="기어링",
        description="gearing — float(6.2). Consume as returned by LS.",
    )
    mness: str = Field(
        default="",
        title="Moneyness",
        description="mness — char(1). Consume as returned by LS.",
    )

class T1954Request(BaseModel):
    """Request envelope for t1954."""

    header: T1954RequestHeader = T1954RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1954",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1954",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1954Response(BaseModel):
    """Response envelope for t1954."""

    header: Optional[T1954ResponseHeader] = None
    block: Optional[T1954OutBlock] = None
    block1: List[T1954OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1954RequestHeader",
    "T1954ResponseHeader",
    "T1954InBlock",
    "T1954OutBlock",
    "T1954OutBlock1",
    "T1954Request",
    "T1954Response",
]