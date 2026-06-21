"""Pydantic models for LS Securities OpenAPI t4203 (업종챠트(종합)(t4203)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T4203RequestHeader(BlockRequestHeader):
    pass


class T4203ResponseHeader(BlockResponseHeader):
    pass

class T4203InBlock(BaseModel):
    """t4203InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(3). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="주기구분(0:틱1:분2:일3:주4:월)",
        description="gubun — char(1). Consume as returned by LS.",
    )
    ncnt: int = Field(
        ...,
        title="틱개수",
        description="ncnt — long(4). Consume as returned by LS.",
    )
    qrycnt: int = Field(
        ...,
        title="건수",
        description="qrycnt — long(4). Consume as returned by LS.",
    )
    tdgb: str = Field(
        ...,
        title="당일구분(0:전체1:당일만)",
        description="tdgb — char(1). Consume as returned by LS.",
    )
    sdate: str = Field(
        ...,
        title="시작일자",
        description="sdate — char(8). Consume as returned by LS.",
    )
    edate: str = Field(
        ...,
        title="종료일자",
        description="edate — char(8). Consume as returned by LS.",
    )
    cts_date: str = Field(
        ...,
        title="연속일자",
        description="cts_date — char(8). Consume as returned by LS.",
    )
    cts_time: str = Field(
        ...,
        title="연속시간",
        description="cts_time — char(10). Consume as returned by LS.",
    )
    cts_daygb: str = Field(
        ...,
        title="연속당일구분(0:연속전체1:연속당일만2:연속전일만)",
        description="cts_daygb — char(1). Consume as returned by LS.",
    )

class T4203OutBlock(BaseModel):
    """t4203OutBlock — output block. 출력"""

    shcode: str = Field(
        default="",
        title="단축코드",
        description="shcode — char(3). Consume as returned by LS.",
    )
    jisiga: float = Field(
        default=0.0,
        title="전일시가",
        description="jisiga — float(7.2). Consume as returned by LS.",
    )
    jihigh: float = Field(
        default=0.0,
        title="전일고가",
        description="jihigh — float(7.2). Consume as returned by LS.",
    )
    jilow: float = Field(
        default=0.0,
        title="전일저가",
        description="jilow — float(7.2). Consume as returned by LS.",
    )
    jiclose: float = Field(
        default=0.0,
        title="전일종가",
        description="jiclose — float(7.2). Consume as returned by LS.",
    )
    jivolume: int = Field(
        default=0,
        title="전일거래량",
        description="jivolume — long(12). Consume as returned by LS.",
    )
    disiga: float = Field(
        default=0.0,
        title="당일시가",
        description="disiga — float(7.2). Consume as returned by LS.",
    )
    dihigh: float = Field(
        default=0.0,
        title="당일고가",
        description="dihigh — float(7.2). Consume as returned by LS.",
    )
    dilow: float = Field(
        default=0.0,
        title="당일저가",
        description="dilow — float(7.2). Consume as returned by LS.",
    )
    diclose: float = Field(
        default=0.0,
        title="당일종가",
        description="diclose — float(7.2). Consume as returned by LS.",
    )
    disvalue: int = Field(
        default=0,
        title="당일거래대금",
        description="disvalue — long(12). Consume as returned by LS.",
    )
    cts_date: str = Field(
        default="",
        title="연속일자",
        description="cts_date — char(8). Consume as returned by LS.",
    )
    cts_time: str = Field(
        default="",
        title="연속시간",
        description="cts_time — char(10). Consume as returned by LS.",
    )
    cts_daygb: str = Field(
        default="",
        title="연속당일구분",
        description="cts_daygb — char(1). Consume as returned by LS.",
    )

class T4203OutBlock1(BaseModel):
    """t4203OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    time: str = Field(
        default="",
        title="시간",
        description="time — char(6). Consume as returned by LS.",
    )
    open: float = Field(
        default=0.0,
        title="시가",
        description="open — float(7.2). Consume as returned by LS.",
    )
    high: float = Field(
        default=0.0,
        title="고가",
        description="high — float(7.2). Consume as returned by LS.",
    )
    low: float = Field(
        default=0.0,
        title="저가",
        description="low — float(7.2). Consume as returned by LS.",
    )
    close: float = Field(
        default=0.0,
        title="종가",
        description="close — float(7.2). Consume as returned by LS.",
    )
    jdiff_vol: int = Field(
        default=0,
        title="거래량",
        description="jdiff_vol — long(12). Consume as returned by LS.",
    )
    value: int = Field(
        default=0,
        title="거래대금",
        description="value — long(12). Consume as returned by LS.",
    )

class T4203Request(BaseModel):
    """Request envelope for t4203."""

    header: T4203RequestHeader = T4203RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t4203",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t4203",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T4203Response(BaseModel):
    """Response envelope for t4203."""

    header: Optional[T4203ResponseHeader] = None
    block: Optional[T4203OutBlock] = None
    block1: List[T4203OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T4203RequestHeader",
    "T4203ResponseHeader",
    "T4203InBlock",
    "T4203OutBlock",
    "T4203OutBlock1",
    "T4203Request",
    "T4203Response",
]