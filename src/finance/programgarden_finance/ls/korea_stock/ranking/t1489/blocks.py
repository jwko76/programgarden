"""Pydantic models for LS Securities OpenAPI t1489 (예상체결량상위조회(t1489)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1489RequestHeader(BlockRequestHeader):
    pass


class T1489ResponseHeader(BlockResponseHeader):
    pass

class T1489InBlock(BaseModel):
    """t1489InBlock — input block. 기본입력"""

    gubun: str = Field(
        ...,
        title="거래소구분",
        description="gubun — char(1). Consume as returned by LS.",
    )
    jgubun: str = Field(
        ...,
        title="장구분",
        description="jgubun — char(1). Consume as returned by LS.",
    )
    jongchk: str = Field(
        ...,
        title="종목체크",
        description="jongchk — char(12). Consume as returned by LS.",
    )
    idx: int = Field(
        ...,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )
    yesprice: int = Field(
        ...,
        title="예상체결시작가격",
        description="yesprice — long(8). Consume as returned by LS.",
    )
    yeeprice: int = Field(
        ...,
        title="예상체결종료가격",
        description="yeeprice — long(8). Consume as returned by LS.",
    )
    yevolume: int = Field(
        ...,
        title="예상체결량",
        description="yevolume — long(12). Consume as returned by LS.",
    )

class T1489OutBlock(BaseModel):
    """t1489OutBlock — output block. 출력"""

    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1489OutBlock1(BaseModel):
    """t1489OutBlock1 — output block (occurs — list of rows). 출력1"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(20). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="현재가",
        description="price — long(8). Consume as returned by LS.",
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
        title="예상거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    offerho: int = Field(
        default=0,
        title="매도호가",
        description="offerho — long(8). Consume as returned by LS.",
    )
    bidho: int = Field(
        default=0,
        title="매수호가",
        description="bidho — long(8). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    jnilvolume: int = Field(
        default=0,
        title="전일거래량",
        description="jnilvolume — long(12). Consume as returned by LS.",
    )

class T1489Request(BaseModel):
    """Request envelope for t1489."""

    header: T1489RequestHeader = T1489RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1489",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1489",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1489Response(BaseModel):
    """Response envelope for t1489."""

    header: Optional[T1489ResponseHeader] = None
    block: Optional[T1489OutBlock] = None
    block1: List[T1489OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1489RequestHeader",
    "T1489ResponseHeader",
    "T1489InBlock",
    "T1489OutBlock",
    "T1489OutBlock1",
    "T1489Request",
    "T1489Response",
]