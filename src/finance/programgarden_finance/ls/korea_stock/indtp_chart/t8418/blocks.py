"""Pydantic models for LS Securities OpenAPI t8418 (업종챠트(N분)(t8418)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8418RequestHeader(BlockRequestHeader):
    pass


class T8418ResponseHeader(BlockResponseHeader):
    pass

class T8418InBlock(BaseModel):
    """t8418InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(3). Consume as returned by LS.",
    )
    ncnt: int = Field(
        ...,
        title="단위(n분)",
        description="ncnt — long(4). Consume as returned by LS.",
    )
    qrycnt: int = Field(
        ...,
        title="요청건수(최대-압축:2000비압축:500)",
        description="qrycnt — long(4). Consume as returned by LS.",
    )
    nday: str = Field(
        ...,
        title="조회영업일수(0:미사용1>=사용)",
        description="nday — char(1). Consume as returned by LS.",
    )
    sdate: str = Field(
        ...,
        title="시작일자",
        description="sdate — char(8). Consume as returned by LS.",
    )
    stime: str = Field(
        ...,
        title="시작시간(현재미사용)",
        description="stime — char(6). Consume as returned by LS.",
    )
    edate: str = Field(
        ...,
        title="종료일자",
        description="edate — char(8). Consume as returned by LS.",
    )
    etime: str = Field(
        ...,
        title="종료시간(현재미사용)",
        description="etime — char(6). Consume as returned by LS.",
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
    comp_yn: str = Field(
        ...,
        title="압축여부(Y:압축N:비압축)",
        description="comp_yn — char(1). Consume as returned by LS.",
    )

class T8418OutBlock(BaseModel):
    """t8418OutBlock — output block. 출력"""

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
    s_time: str = Field(
        default="",
        title="업종시작시간(HHMMSS)",
        description="s_time — char(6). Consume as returned by LS.",
    )
    e_time: str = Field(
        default="",
        title="업종종료시간(HHMMSS)",
        description="e_time — char(6). Consume as returned by LS.",
    )
    dshmin: str = Field(
        default="",
        title="동시호가처리시간(MM:분)",
        description="dshmin — char(2). Consume as returned by LS.",
    )
    rec_count: int = Field(
        default=0,
        title="레코드카운트",
        description="rec_count — long(7). Consume as returned by LS.",
    )

class T8418OutBlock1(BaseModel):
    """t8418OutBlock1 — output block (occurs — list of rows). 출력1"""

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

class T8418Request(BaseModel):
    """Request envelope for t8418."""

    header: T8418RequestHeader = T8418RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8418",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8418",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8418Response(BaseModel):
    """Response envelope for t8418."""

    header: Optional[T8418ResponseHeader] = None
    block: Optional[T8418OutBlock] = None
    block1: List[T8418OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8418RequestHeader",
    "T8418ResponseHeader",
    "T8418InBlock",
    "T8418OutBlock",
    "T8418OutBlock1",
    "T8418Request",
    "T8418Response",
]