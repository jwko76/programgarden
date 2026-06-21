"""Pydantic models for LS Securities OpenAPI t8419 (업종챠트(일주월)(t8419)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8419RequestHeader(BlockRequestHeader):
    pass


class T8419ResponseHeader(BlockResponseHeader):
    pass

class T8419InBlock(BaseModel):
    """t8419InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(3). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="주기구분(2:일3:주4:월)",
        description="gubun — char(1). Consume as returned by LS.",
    )
    qrycnt: int = Field(
        ...,
        title="요청건수(최대-압축:2000비압축:500)",
        description="qrycnt — long(4). Consume as returned by LS.",
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
    comp_yn: str = Field(
        ...,
        title="압축여부(Y:압축N:비압축)",
        description="comp_yn — char(1). Consume as returned by LS.",
    )

class T8419OutBlock(BaseModel):
    """t8419OutBlock — output block. 출력"""

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
    s_time: str = Field(
        default="",
        title="업종시작시간",
        description="s_time — char(6). Consume as returned by LS.",
    )
    e_time: str = Field(
        default="",
        title="업종종료시간",
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

class T8419OutBlock1(BaseModel):
    """t8419OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
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

class T8419Request(BaseModel):
    """Request envelope for t8419."""

    header: T8419RequestHeader = T8419RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8419",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8419",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8419Response(BaseModel):
    """Response envelope for t8419."""

    header: Optional[T8419ResponseHeader] = None
    block: Optional[T8419OutBlock] = None
    block1: List[T8419OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8419RequestHeader",
    "T8419ResponseHeader",
    "T8419InBlock",
    "T8419OutBlock",
    "T8419OutBlock1",
    "T8419Request",
    "T8419Response",
]