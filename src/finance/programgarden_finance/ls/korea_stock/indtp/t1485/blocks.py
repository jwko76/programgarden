"""Pydantic models for LS Securities OpenAPI t1485 (예상지수(t1485)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1485RequestHeader(BlockRequestHeader):
    pass


class T1485ResponseHeader(BlockResponseHeader):
    pass

class T1485InBlock(BaseModel):
    """t1485InBlock — input block. 기본입력"""

    upcode: str = Field(
        ...,
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="조회구분",
        description="gubun — char(1). Consume as returned by LS.",
    )

class T1485OutBlock(BaseModel):
    """t1485OutBlock — output block. 출력"""

    pricejisu: float = Field(
        default=0.0,
        title="현재지수",
        description="pricejisu — float(10.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="지수전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(10.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    yhighjo: int = Field(
        default=0,
        title="상승종목수",
        description="yhighjo — long(4). Consume as returned by LS.",
    )
    yupjo: int = Field(
        default=0,
        title="상한종목수",
        description="yupjo — long(4). Consume as returned by LS.",
    )
    yunchgjo: int = Field(
        default=0,
        title="보합종목수",
        description="yunchgjo — long(4). Consume as returned by LS.",
    )
    ylowjo: int = Field(
        default=0,
        title="하락종목수",
        description="ylowjo — long(4). Consume as returned by LS.",
    )
    ydownjo: int = Field(
        default=0,
        title="하한종목수",
        description="ydownjo — long(4). Consume as returned by LS.",
    )
    ytrajo: int = Field(
        default=0,
        title="거래형성수",
        description="ytrajo — long(4). Consume as returned by LS.",
    )

class T1485OutBlock1(BaseModel):
    """t1485OutBlock1 — output block (occurs — list of rows). 출력1"""

    chetime: str = Field(
        default="",
        title="시간",
        description="chetime — char(6). Consume as returned by LS.",
    )
    jisu: float = Field(
        default=0.0,
        title="예상지수",
        description="jisu — float(10.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(10.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="예상체결량",
        description="volume — long(12). Consume as returned by LS.",
    )
    volcha: int = Field(
        default=0,
        title="예상체결량직전대비",
        description="volcha — long(12). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="예상등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )

class T1485Request(BaseModel):
    """Request envelope for t1485."""

    header: T1485RequestHeader = T1485RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1485",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1485",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1485Response(BaseModel):
    """Response envelope for t1485."""

    header: Optional[T1485ResponseHeader] = None
    block: Optional[T1485OutBlock] = None
    block1: List[T1485OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1485RequestHeader",
    "T1485ResponseHeader",
    "T1485InBlock",
    "T1485OutBlock",
    "T1485OutBlock1",
    "T1485Request",
    "T1485Response",
]