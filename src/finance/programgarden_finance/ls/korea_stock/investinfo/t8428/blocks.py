"""Pydantic models for LS Securities OpenAPI t8428 (증시주변자금추이(t8428)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8428RequestHeader(BlockRequestHeader):
    pass


class T8428ResponseHeader(BlockResponseHeader):
    pass

class T8428InBlock(BaseModel):
    """t8428InBlock — input block. 기본입력"""

    fdate: str = Field(
        ...,
        title="from일자",
        description="fdate — char(8). Consume as returned by LS.",
    )
    tdate: str = Field(
        ...,
        title="to일자",
        description="tdate — char(8). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="구분",
        description="gubun — char(1). Consume as returned by LS.",
    )
    key_date: str = Field(
        ...,
        title="날짜",
        description="key_date — char(8). Consume as returned by LS.",
    )
    upcode: str = Field(
        ...,
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="조회건수",
        description="cnt — int(3). Consume as returned by LS.",
    )

class T8428OutBlock(BaseModel):
    """t8428OutBlock — output block. 출력"""

    date: str = Field(
        default="",
        title="날짜CTS",
        description="date — char(8). Consume as returned by LS.",
    )
    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T8428OutBlock1(BaseModel):
    """t8428OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="일자",
        description="date — char(8). Consume as returned by LS.",
    )
    jisu: float = Field(
        default=0.0,
        title="지수",
        description="jisu — float(7.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="대비",
        description="change — float(6.2). Consume as returned by LS.",
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
    custmoney: int = Field(
        default=0,
        title="고객예탁금_억원",
        description="custmoney — long(12). Consume as returned by LS.",
    )
    yecha: int = Field(
        default=0,
        title="예탁증감_억원",
        description="yecha — long(12). Consume as returned by LS.",
    )
    vol: float = Field(
        default=0.0,
        title="회전율",
        description="vol — float(6.2). Consume as returned by LS.",
    )
    outmoney: int = Field(
        default=0,
        title="미수금_억원",
        description="outmoney — long(12). Consume as returned by LS.",
    )
    trjango: int = Field(
        default=0,
        title="신용잔고_억원",
        description="trjango — long(12). Consume as returned by LS.",
    )
    futymoney: int = Field(
        default=0,
        title="선물예수금_억원",
        description="futymoney — long(12). Consume as returned by LS.",
    )
    stkmoney: int = Field(
        default=0,
        title="주식형_억원",
        description="stkmoney — long(8). Consume as returned by LS.",
    )
    mstkmoney: int = Field(
        default=0,
        title="혼합형_억원(주식)",
        description="mstkmoney — long(8). Consume as returned by LS.",
    )
    mbndmoney: int = Field(
        default=0,
        title="혼합형_억원(채권)",
        description="mbndmoney — long(8). Consume as returned by LS.",
    )
    bndmoney: int = Field(
        default=0,
        title="채권형_억원",
        description="bndmoney — long(8). Consume as returned by LS.",
    )
    bndsmoney: int = Field(
        default=0,
        title="필러(구.단기채권)",
        description="bndsmoney — long(8). Consume as returned by LS.",
    )
    mmfmoney: int = Field(
        default=0,
        title="MMF_억원(주식)",
        description="mmfmoney — long(8). Consume as returned by LS.",
    )

class T8428Request(BaseModel):
    """Request envelope for t8428."""

    header: T8428RequestHeader = T8428RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8428",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8428",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8428Response(BaseModel):
    """Response envelope for t8428."""

    header: Optional[T8428ResponseHeader] = None
    block: Optional[T8428OutBlock] = None
    block1: List[T8428OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8428RequestHeader",
    "T8428ResponseHeader",
    "T8428InBlock",
    "T8428OutBlock",
    "T8428OutBlock1",
    "T8428Request",
    "T8428Response",
]