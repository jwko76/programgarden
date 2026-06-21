"""Pydantic models for LS Securities OpenAPI t8410 (API전용주식챠트(일주월년)(t8410)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8410RequestHeader(BlockRequestHeader):
    pass


class T8410ResponseHeader(BlockResponseHeader):
    pass

class T8410InBlock(BaseModel):
    """t8410InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="주기구분(2:일3:주4:월5:년)",
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
    sujung: str = Field(
        ...,
        title="수정주가여부(Y:적용N:비적용)",
        description="sujung — char(1). Consume as returned by LS.",
    )

class T8410OutBlock(BaseModel):
    """t8410OutBlock — output block. 출력"""

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

class T8410OutBlock1(BaseModel):
    """t8410OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    open: int = Field(
        default=0,
        title="시가",
        description="open — long(12). Consume as returned by LS.",
    )
    high: int = Field(
        default=0,
        title="고가",
        description="high — long(12). Consume as returned by LS.",
    )
    low: int = Field(
        default=0,
        title="저가",
        description="low — long(12). Consume as returned by LS.",
    )
    close: int = Field(
        default=0,
        title="종가",
        description="close — long(12). Consume as returned by LS.",
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
    ratevalue: int = Field(
        default=0,
        title="수정비율반영거래대금",
        description="ratevalue — long(12). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="종가등락구분(1:상한2:상승3:보합4:하한5:하락주식일만사용)",
        description="sign — char(1). Consume as returned by LS.",
    )

class T8410Request(BaseModel):
    """Request envelope for t8410."""

    header: T8410RequestHeader = T8410RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8410",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8410",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8410Response(BaseModel):
    """Response envelope for t8410."""

    header: Optional[T8410ResponseHeader] = None
    block: Optional[T8410OutBlock] = None
    block1: List[T8410OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8410RequestHeader",
    "T8410ResponseHeader",
    "T8410InBlock",
    "T8410OutBlock",
    "T8410OutBlock1",
    "T8410Request",
    "T8410Response",
]