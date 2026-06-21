"""Pydantic models for LS Securities OpenAPI t8405 (주식선물기간별주가(API용)(t8405)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8405RequestHeader(BlockRequestHeader):
    pass


class T8405ResponseHeader(BlockResponseHeader):
    pass

class T8405InBlock(BaseModel):
    """t8405InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(8). Consume as returned by LS.",
    )
    futcheck: str = Field(
        ...,
        title="선물최근월물",
        description="futcheck — char(1). Consume as returned by LS.",
    )
    date: str = Field(
        ...,
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    cts_code: str = Field(
        ...,
        title="CTS종목코드",
        description="cts_code — char(8). Consume as returned by LS.",
    )
    lastdate: str = Field(
        ...,
        title="전종목만기일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="조회요청건수",
        description="cnt — int(3). Consume as returned by LS.",
    )

class T8405OutBlock(BaseModel):
    """t8405OutBlock — output block. 출력"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    cts_code: str = Field(
        default="",
        title="CTS종목코드",
        description="cts_code — char(8). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="전종목만기일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    nowfutyn: str = Field(
        default="",
        title="최근월선물여부",
        description="nowfutyn — char(1). Consume as returned by LS.",
    )

class T8405OutBlock1(BaseModel):
    """t8405OutBlock1 — output block (occurs — list of rows). 출력1"""

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
    volume: int = Field(
        default=0,
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    diff_vol: float = Field(
        default=0.0,
        title="거래증가율",
        description="diff_vol — float(10.2). Consume as returned by LS.",
    )
    openyak: int = Field(
        default=0,
        title="미결수량",
        description="openyak — long(8). Consume as returned by LS.",
    )
    openyakupdn: int = Field(
        default=0,
        title="미결증감",
        description="openyakupdn — long(8). Consume as returned by LS.",
    )
    value: float = Field(
        default=0.0,
        title="거래대금",
        description="value — float(12). Consume as returned by LS.",
    )

class T8405Request(BaseModel):
    """Request envelope for t8405."""

    header: T8405RequestHeader = T8405RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8405",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8405",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8405Response(BaseModel):
    """Response envelope for t8405."""

    header: Optional[T8405ResponseHeader] = None
    block: Optional[T8405OutBlock] = None
    block1: List[T8405OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8405RequestHeader",
    "T8405ResponseHeader",
    "T8405InBlock",
    "T8405OutBlock",
    "T8405OutBlock1",
    "T8405Request",
    "T8405Response",
]