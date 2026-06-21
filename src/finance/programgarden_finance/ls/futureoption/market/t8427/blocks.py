"""Pydantic models for LS Securities OpenAPI t8427 (과거데이터시간대별조회(t8427)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8427RequestHeader(BlockRequestHeader):
    pass


class T8427ResponseHeader(BlockResponseHeader):
    pass

class T8427InBlock(BaseModel):
    """t8427InBlock — input block. 기본입력"""

    fo_gbn: str = Field(
        ...,
        title="선물옵션구분",
        description="fo_gbn — char(1). Consume as returned by LS.",
    )
    yyyy: str = Field(
        ...,
        title="조회년도",
        description="yyyy — char(4). Consume as returned by LS.",
    )
    mm: str = Field(
        ...,
        title="조회월",
        description="mm — char(2). Consume as returned by LS.",
    )
    cp_gbn: str = Field(
        ...,
        title="옵션콜풋구분",
        description="cp_gbn — char(1). Consume as returned by LS.",
    )
    actprice: float = Field(
        ...,
        title="옵션행사가",
        description="actprice — float(6.2). Consume as returned by LS.",
    )
    focode: str = Field(
        ...,
        title="선물옵션코드",
        description="focode — char(8). Consume as returned by LS.",
    )
    dt_gbn: str = Field(
        ...,
        title="일분구분",
        description="dt_gbn — char(1). Consume as returned by LS.",
    )
    min_term: str = Field(
        ...,
        title="분간격",
        description="min_term — char(2). Consume as returned by LS.",
    )
    date: str = Field(
        ...,
        title="날짜",
        description="date — char(8). Consume as returned by LS.",
    )
    time: str = Field(
        ...,
        title="시간",
        description="time — char(6). Consume as returned by LS.",
    )

class T8427OutBlock(BaseModel):
    """t8427OutBlock — output block. 출력"""

    focode: str = Field(
        default="",
        title="선물옵션코드",
        description="focode — char(8). Consume as returned by LS.",
    )
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

class T8427OutBlock1(BaseModel):
    """t8427OutBlock1 — output block (occurs — list of rows). 출력1"""

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
        description="open — float(6.2). Consume as returned by LS.",
    )
    high: float = Field(
        default=0.0,
        title="고가",
        description="high — float(6.2). Consume as returned by LS.",
    )
    low: float = Field(
        default=0.0,
        title="저가",
        description="low — float(6.2). Consume as returned by LS.",
    )
    close: float = Field(
        default=0.0,
        title="종가",
        description="close — float(6.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
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

class T8427Request(BaseModel):
    """Request envelope for t8427."""

    header: T8427RequestHeader = T8427RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8427",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8427",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8427Response(BaseModel):
    """Response envelope for t8427."""

    header: Optional[T8427ResponseHeader] = None
    block: Optional[T8427OutBlock] = None
    block1: List[T8427OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8427RequestHeader",
    "T8427ResponseHeader",
    "T8427InBlock",
    "T8427OutBlock",
    "T8427OutBlock1",
    "T8427Request",
    "T8427Response",
]