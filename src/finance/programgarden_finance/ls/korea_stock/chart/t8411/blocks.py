"""Pydantic models for LS Securities OpenAPI t8411 (주식챠트(틱/n틱)(t8411)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8411RequestHeader(BlockRequestHeader):
    pass


class T8411ResponseHeader(BlockResponseHeader):
    pass

class T8411InBlock(BaseModel):
    """t8411InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    ncnt: int = Field(
        ...,
        title="단위(n틱)",
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

class T8411OutBlock(BaseModel):
    """t8411OutBlock — output block. 출력"""

    shcode: str = Field(
        default="",
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    jisiga: int = Field(
        default=0,
        title="전일시가",
        description="jisiga — long(8). Consume as returned by LS.",
    )
    jihigh: int = Field(
        default=0,
        title="전일고가",
        description="jihigh — long(8). Consume as returned by LS.",
    )
    jilow: int = Field(
        default=0,
        title="전일저가",
        description="jilow — long(8). Consume as returned by LS.",
    )
    jiclose: int = Field(
        default=0,
        title="전일종가",
        description="jiclose — long(8). Consume as returned by LS.",
    )
    jivolume: int = Field(
        default=0,
        title="전일거래량",
        description="jivolume — long(12). Consume as returned by LS.",
    )
    disiga: int = Field(
        default=0,
        title="당일시가",
        description="disiga — long(8). Consume as returned by LS.",
    )
    dihigh: int = Field(
        default=0,
        title="당일고가",
        description="dihigh — long(8). Consume as returned by LS.",
    )
    dilow: int = Field(
        default=0,
        title="당일저가",
        description="dilow — long(8). Consume as returned by LS.",
    )
    diclose: int = Field(
        default=0,
        title="당일종가",
        description="diclose — long(8). Consume as returned by LS.",
    )

class T8411OutBlock1(BaseModel):
    """t8411OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    time: str = Field(
        default="",
        title="시간",
        description="time — char(10). Consume as returned by LS.",
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
    jdiff_vol: int = Field(
        default=0,
        title="거래량",
        description="jdiff_vol — long(12). Consume as returned by LS.",
    )
    jongchk: int = Field(
        default=0,
        title="수정구분",
        description="jongchk — long(13). Consume as returned by LS.",
    )
    rate: float = Field(
        default=0.0,
        title="수정비율",
        description="rate — double(6.2). Consume as returned by LS.",
    )
    pricechk: int = Field(
        default=0,
        title="수정주가반영항목",
        description="pricechk — long(13). Consume as returned by LS.",
    )

class T8411Request(BaseModel):
    """Request envelope for t8411."""

    header: T8411RequestHeader = T8411RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8411",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8411",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8411Response(BaseModel):
    """Response envelope for t8411."""

    header: Optional[T8411ResponseHeader] = None
    block: Optional[T8411OutBlock] = None
    block1: List[T8411OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8411RequestHeader",
    "T8411ResponseHeader",
    "T8411InBlock",
    "T8411OutBlock",
    "T8411OutBlock1",
    "T8411Request",
    "T8411Response",
]