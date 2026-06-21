"""Pydantic models for LS Securities OpenAPI t1771 (종목별회원사추이(t1771)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1771RequestHeader(BlockRequestHeader):
    pass


class T1771ResponseHeader(BlockResponseHeader):
    pass

class T1771InBlock(BaseModel):
    """t1771InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    tradno: str = Field(
        ...,
        title="거래원코드",
        description="tradno — char(3). Consume as returned by LS.",
    )
    gubun1: str = Field(
        ...,
        title="구분1",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    traddate1: str = Field(
        ...,
        title="거래원날짜1",
        description="traddate1 — char(8). Consume as returned by LS.",
    )
    traddate2: str = Field(
        ...,
        title="거래원날짜2",
        description="traddate2 — char(8). Consume as returned by LS.",
    )
    cts_idx: int = Field(
        ...,
        title="CTSIDX",
        description="cts_idx — long(4). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="요청건수",
        description="cnt — int(3). Consume as returned by LS.",
    )
    exchgubun: str = Field(
        ...,
        title="거래소구분",
        description="exchgubun — char(1). Consume as returned by LS.",
    )

class T1771OutBlock(BaseModel):
    """t1771OutBlock — output block. 기본출력"""

    cts_idx: int = Field(
        default=0,
        title="CTSIDX",
        description="cts_idx — long(4). Consume as returned by LS.",
    )

class T1771OutBlock2(BaseModel):
    """t1771OutBlock2 — output block (occurs — list of rows). 출력2"""

    traddate: str = Field(
        default="",
        title="날짜",
        description="traddate — char(8). Consume as returned by LS.",
    )
    tradtime: str = Field(
        default="",
        title="시간",
        description="tradtime — char(8). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="현재가",
        description="price — long(8). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: int = Field(
        default=0,
        title="대비",
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
    tradmdcha: int = Field(
        default=0,
        title="매도",
        description="tradmdcha — long(12). Consume as returned by LS.",
    )
    tradmscha: int = Field(
        default=0,
        title="매수",
        description="tradmscha — long(12). Consume as returned by LS.",
    )
    tradmdval: int = Field(
        default=0,
        title="매도대금",
        description="tradmdval — long(18). Consume as returned by LS.",
    )
    tradmsval: int = Field(
        default=0,
        title="매수대금",
        description="tradmsval — long(18). Consume as returned by LS.",
    )
    tradmsscha: int = Field(
        default=0,
        title="순매수",
        description="tradmsscha — long(12). Consume as returned by LS.",
    )
    tradmttvolume: int = Field(
        default=0,
        title="누적순매수",
        description="tradmttvolume — long(12). Consume as returned by LS.",
    )
    tradavg: int = Field(
        default=0,
        title="평균단가",
        description="tradavg — long(8). Consume as returned by LS.",
    )
    tradmttavg: int = Field(
        default=0,
        title="누적평균단가",
        description="tradmttavg — long(8). Consume as returned by LS.",
    )
    exchname: str = Field(
        default="",
        title="거래소명",
        description="exchname — char(3). Consume as returned by LS.",
    )
    ex_shcode: str = Field(
        default="",
        title="거래소별단축코드",
        description="ex_shcode — char(10). Consume as returned by LS.",
    )

class T1771Request(BaseModel):
    """Request envelope for t1771."""

    header: T1771RequestHeader = T1771RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1771",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1771",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1771Response(BaseModel):
    """Response envelope for t1771."""

    header: Optional[T1771ResponseHeader] = None
    block: Optional[T1771OutBlock] = None
    block2: List[T1771OutBlock2] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1771RequestHeader",
    "T1771ResponseHeader",
    "T1771InBlock",
    "T1771OutBlock",
    "T1771OutBlock2",
    "T1771Request",
    "T1771Response",
]