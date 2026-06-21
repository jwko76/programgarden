"""Pydantic models for LS Securities OpenAPI t8403 (주식선물호가조회(API용)(t8403)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8403RequestHeader(BlockRequestHeader):
    pass


class T8403ResponseHeader(BlockResponseHeader):
    pass

class T8403InBlock(BaseModel):
    """t8403InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(8). Consume as returned by LS.",
    )

class T8403OutBlock(BaseModel):
    """t8403OutBlock — output block. 출력"""

    hname: str = Field(
        default="",
        title="종목명",
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
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    stimeqrt: float = Field(
        default=0.0,
        title="거래량전일동시간비율",
        description="stimeqrt — float(6.2). Consume as returned by LS.",
    )
    jnilclose: int = Field(
        default=0,
        title="전일종가",
        description="jnilclose — long(8). Consume as returned by LS.",
    )
    offerho1: int = Field(
        default=0,
        title="매도호가1",
        description="offerho1 — long(8). Consume as returned by LS.",
    )
    bidho1: int = Field(
        default=0,
        title="매수호가1",
        description="bidho1 — long(8). Consume as returned by LS.",
    )
    offerrem1: int = Field(
        default=0,
        title="매도호가수량1",
        description="offerrem1 — long(8). Consume as returned by LS.",
    )
    bidrem1: int = Field(
        default=0,
        title="매수호가수량1",
        description="bidrem1 — long(8). Consume as returned by LS.",
    )
    dcnt1: int = Field(
        default=0,
        title="매도호가건수1",
        description="dcnt1 — long(8). Consume as returned by LS.",
    )
    scnt1: int = Field(
        default=0,
        title="매수호가건수1",
        description="scnt1 — long(8). Consume as returned by LS.",
    )
    offerho2: int = Field(
        default=0,
        title="매도호가2",
        description="offerho2 — long(8). Consume as returned by LS.",
    )
    bidho2: int = Field(
        default=0,
        title="매수호가2",
        description="bidho2 — long(8). Consume as returned by LS.",
    )
    offerrem2: int = Field(
        default=0,
        title="매도호가수량2",
        description="offerrem2 — long(8). Consume as returned by LS.",
    )
    bidrem2: int = Field(
        default=0,
        title="매수호가수량2",
        description="bidrem2 — long(8). Consume as returned by LS.",
    )
    dcnt2: int = Field(
        default=0,
        title="매도호가건수2",
        description="dcnt2 — long(8). Consume as returned by LS.",
    )
    scnt2: int = Field(
        default=0,
        title="매수호가건수2",
        description="scnt2 — long(8). Consume as returned by LS.",
    )
    offerho3: int = Field(
        default=0,
        title="매도호가3",
        description="offerho3 — long(8). Consume as returned by LS.",
    )
    bidho3: int = Field(
        default=0,
        title="매수호가3",
        description="bidho3 — long(8). Consume as returned by LS.",
    )
    offerrem3: int = Field(
        default=0,
        title="매도호가수량3",
        description="offerrem3 — long(8). Consume as returned by LS.",
    )
    bidrem3: int = Field(
        default=0,
        title="매수호가수량3",
        description="bidrem3 — long(8). Consume as returned by LS.",
    )
    dcnt3: int = Field(
        default=0,
        title="매도호가건수3",
        description="dcnt3 — long(8). Consume as returned by LS.",
    )
    scnt3: int = Field(
        default=0,
        title="매수호가건수3",
        description="scnt3 — long(8). Consume as returned by LS.",
    )
    offerho4: int = Field(
        default=0,
        title="매도호가4",
        description="offerho4 — long(8). Consume as returned by LS.",
    )
    bidho4: int = Field(
        default=0,
        title="매수호가4",
        description="bidho4 — long(8). Consume as returned by LS.",
    )
    offerrem4: int = Field(
        default=0,
        title="매도호가수량4",
        description="offerrem4 — long(8). Consume as returned by LS.",
    )
    bidrem4: int = Field(
        default=0,
        title="매수호가수량4",
        description="bidrem4 — long(8). Consume as returned by LS.",
    )
    dcnt4: int = Field(
        default=0,
        title="매도호가건수4",
        description="dcnt4 — long(8). Consume as returned by LS.",
    )
    scnt4: int = Field(
        default=0,
        title="매수호가건수4",
        description="scnt4 — long(8). Consume as returned by LS.",
    )
    offerho5: int = Field(
        default=0,
        title="매도호가5",
        description="offerho5 — long(8). Consume as returned by LS.",
    )
    bidho5: int = Field(
        default=0,
        title="매수호가5",
        description="bidho5 — long(8). Consume as returned by LS.",
    )
    offerrem5: int = Field(
        default=0,
        title="매도호가수량5",
        description="offerrem5 — long(8). Consume as returned by LS.",
    )
    bidrem5: int = Field(
        default=0,
        title="매수호가수량5",
        description="bidrem5 — long(8). Consume as returned by LS.",
    )
    dcnt5: int = Field(
        default=0,
        title="매도호가건수5",
        description="dcnt5 — long(8). Consume as returned by LS.",
    )
    scnt5: int = Field(
        default=0,
        title="매수호가건수5",
        description="scnt5 — long(8). Consume as returned by LS.",
    )
    offerho6: int = Field(
        default=0,
        title="매도호가6",
        description="offerho6 — long(8). Consume as returned by LS.",
    )
    bidho6: int = Field(
        default=0,
        title="매수호가6",
        description="bidho6 — long(8). Consume as returned by LS.",
    )
    offerrem6: int = Field(
        default=0,
        title="매도호가수량6",
        description="offerrem6 — long(8). Consume as returned by LS.",
    )
    bidrem6: int = Field(
        default=0,
        title="매수호가수량6",
        description="bidrem6 — long(8). Consume as returned by LS.",
    )
    dcnt6: int = Field(
        default=0,
        title="매도호가건수6",
        description="dcnt6 — long(8). Consume as returned by LS.",
    )
    scnt6: int = Field(
        default=0,
        title="매수호가건수6",
        description="scnt6 — long(8). Consume as returned by LS.",
    )
    offerho7: int = Field(
        default=0,
        title="매도호가7",
        description="offerho7 — long(8). Consume as returned by LS.",
    )
    bidho7: int = Field(
        default=0,
        title="매수호가7",
        description="bidho7 — long(8). Consume as returned by LS.",
    )
    offerrem7: int = Field(
        default=0,
        title="매도호가수량7",
        description="offerrem7 — long(8). Consume as returned by LS.",
    )
    bidrem7: int = Field(
        default=0,
        title="매수호가수량7",
        description="bidrem7 — long(8). Consume as returned by LS.",
    )
    dcnt7: int = Field(
        default=0,
        title="매도호가건수7",
        description="dcnt7 — long(8). Consume as returned by LS.",
    )
    scnt7: int = Field(
        default=0,
        title="매수호가건수7",
        description="scnt7 — long(8). Consume as returned by LS.",
    )
    offerho8: int = Field(
        default=0,
        title="매도호가8",
        description="offerho8 — long(8). Consume as returned by LS.",
    )
    bidho8: int = Field(
        default=0,
        title="매수호가8",
        description="bidho8 — long(8). Consume as returned by LS.",
    )
    offerrem8: int = Field(
        default=0,
        title="매도호가수량8",
        description="offerrem8 — long(8). Consume as returned by LS.",
    )
    bidrem8: int = Field(
        default=0,
        title="매수호가수량8",
        description="bidrem8 — long(8). Consume as returned by LS.",
    )
    dcnt8: int = Field(
        default=0,
        title="매도호가건수8",
        description="dcnt8 — long(8). Consume as returned by LS.",
    )
    scnt8: int = Field(
        default=0,
        title="매수호가건수8",
        description="scnt8 — long(8). Consume as returned by LS.",
    )
    offerho9: int = Field(
        default=0,
        title="매도호가9",
        description="offerho9 — long(8). Consume as returned by LS.",
    )
    bidho9: int = Field(
        default=0,
        title="매수호가9",
        description="bidho9 — long(8). Consume as returned by LS.",
    )
    offerrem9: int = Field(
        default=0,
        title="매도호가수량9",
        description="offerrem9 — long(8). Consume as returned by LS.",
    )
    bidrem9: int = Field(
        default=0,
        title="매수호가수량9",
        description="bidrem9 — long(8). Consume as returned by LS.",
    )
    dcnt9: int = Field(
        default=0,
        title="매도호가건수9",
        description="dcnt9 — long(8). Consume as returned by LS.",
    )
    scnt9: int = Field(
        default=0,
        title="매수호가건수9",
        description="scnt9 — long(8). Consume as returned by LS.",
    )
    offerho10: int = Field(
        default=0,
        title="매도호가10",
        description="offerho10 — long(8). Consume as returned by LS.",
    )
    bidho10: int = Field(
        default=0,
        title="매수호가10",
        description="bidho10 — long(8). Consume as returned by LS.",
    )
    offerrem10: int = Field(
        default=0,
        title="매도호가수량10",
        description="offerrem10 — long(8). Consume as returned by LS.",
    )
    bidrem10: int = Field(
        default=0,
        title="매수호가수량10",
        description="bidrem10 — long(8). Consume as returned by LS.",
    )
    dcnt10: int = Field(
        default=0,
        title="매도호가건수10",
        description="dcnt10 — long(8). Consume as returned by LS.",
    )
    scnt10: int = Field(
        default=0,
        title="매수호가건수10",
        description="scnt10 — long(8). Consume as returned by LS.",
    )
    dvol: int = Field(
        default=0,
        title="매도호가총수량",
        description="dvol — long(8). Consume as returned by LS.",
    )
    svol: int = Field(
        default=0,
        title="매수호가총수량",
        description="svol — long(8). Consume as returned by LS.",
    )
    toffernum: int = Field(
        default=0,
        title="총매도호가건수",
        description="toffernum — long(8). Consume as returned by LS.",
    )
    tbidnum: int = Field(
        default=0,
        title="총매수호가건수",
        description="tbidnum — long(8). Consume as returned by LS.",
    )
    time: str = Field(
        default="",
        title="수신시간",
        description="time — char(6). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T8403Request(BaseModel):
    """Request envelope for t8403."""

    header: T8403RequestHeader = T8403RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8403",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8403",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8403Response(BaseModel):
    """Response envelope for t8403."""

    header: Optional[T8403ResponseHeader] = None
    block: Optional[T8403OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8403RequestHeader",
    "T8403ResponseHeader",
    "T8403InBlock",
    "T8403OutBlock",
    "T8403Request",
    "T8403Response",
]