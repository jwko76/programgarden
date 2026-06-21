"""Pydantic models for LS Securities OpenAPI t1492 (단일가예상등락율상위(t1492)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1492RequestHeader(BlockRequestHeader):
    pass


class T1492ResponseHeader(BlockResponseHeader):
    pass

class T1492InBlock(BaseModel):
    """t1492InBlock — input block. 기본입력"""

    gubun1: str = Field(
        ...,
        title="구분",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    gubun2: str = Field(
        ...,
        title="상승하락",
        description="gubun2 — char(1). Consume as returned by LS.",
    )
    jongchk: str = Field(
        ...,
        title="종목체크",
        description="jongchk — char(1). Consume as returned by LS.",
    )
    volume: str = Field(
        ...,
        title="거래량",
        description="volume — char(1). Consume as returned by LS.",
    )
    idx: int = Field(
        ...,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1492OutBlock(BaseModel):
    """t1492OutBlock — output block. 출력"""

    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1492OutBlock1(BaseModel):
    """t1492OutBlock1 — output block (occurs — list of rows). 출력1"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(20). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="예상체결가",
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
    yevolume: int = Field(
        default=0,
        title="예상체결량",
        description="yevolume — long(12). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="누적거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    offerrem1: int = Field(
        default=0,
        title="매도잔량",
        description="offerrem1 — long(12). Consume as returned by LS.",
    )
    bidrem1: int = Field(
        default=0,
        title="매수잔량",
        description="bidrem1 — long(12). Consume as returned by LS.",
    )
    offerho1: int = Field(
        default=0,
        title="매도호가",
        description="offerho1 — long(12). Consume as returned by LS.",
    )
    bidho1: int = Field(
        default=0,
        title="매수호가",
        description="bidho1 — long(12). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    value: int = Field(
        default=0,
        title="누적거래대금",
        description="value — long(12). Consume as returned by LS.",
    )

class T1492Request(BaseModel):
    """Request envelope for t1492."""

    header: T1492RequestHeader = T1492RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1492",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1492",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1492Response(BaseModel):
    """Response envelope for t1492."""

    header: Optional[T1492ResponseHeader] = None
    block: Optional[T1492OutBlock] = None
    block1: List[T1492OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1492RequestHeader",
    "T1492ResponseHeader",
    "T1492InBlock",
    "T1492OutBlock",
    "T1492OutBlock1",
    "T1492Request",
    "T1492Response",
]