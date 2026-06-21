"""Pydantic models for LS Securities OpenAPI t1951 (ELW시간대별체결조회(t1951)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1951RequestHeader(BlockRequestHeader):
    pass


class T1951ResponseHeader(BlockResponseHeader):
    pass

class T1951InBlock(BaseModel):
    """t1951InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    cvolume: int = Field(
        ...,
        title="특이거래량",
        description="cvolume — long(12). Consume as returned by LS.",
    )
    starttime: str = Field(
        ...,
        title="시작시간",
        description="starttime — char(4). Consume as returned by LS.",
    )

class T1951OutBlock(BaseModel):
    """t1951OutBlock — output block. 출력"""

    cts_time: str = Field(
        default="",
        title="시간CTS",
        description="cts_time — char(8). Consume as returned by LS.",
    )

class T1951OutBlock1(BaseModel):
    """t1951OutBlock1 — output block (occurs — list of rows). 출력1"""

    chetime: str = Field(
        default="",
        title="시간",
        description="chetime — char(8). Consume as returned by LS.",
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
    cvolume: int = Field(
        default=0,
        title="체결수량",
        description="cvolume — long(12). Consume as returned by LS.",
    )
    chdegree: float = Field(
        default=0.0,
        title="체결강도",
        description="chdegree — float(8.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    mdvolume: int = Field(
        default=0,
        title="매도체결수량",
        description="mdvolume — long(12). Consume as returned by LS.",
    )
    mdchecnt: int = Field(
        default=0,
        title="매도체결건수",
        description="mdchecnt — long(8). Consume as returned by LS.",
    )
    msvolume: int = Field(
        default=0,
        title="매수체결수량",
        description="msvolume — long(12). Consume as returned by LS.",
    )
    mschecnt: int = Field(
        default=0,
        title="매수체결건수",
        description="mschecnt — long(8). Consume as returned by LS.",
    )
    revolume: int = Field(
        default=0,
        title="순체결량",
        description="revolume — long(12). Consume as returned by LS.",
    )
    rechecnt: int = Field(
        default=0,
        title="순체결건수",
        description="rechecnt — long(8). Consume as returned by LS.",
    )

class T1951Request(BaseModel):
    """Request envelope for t1951."""

    header: T1951RequestHeader = T1951RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1951",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1951",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1951Response(BaseModel):
    """Response envelope for t1951."""

    header: Optional[T1951ResponseHeader] = None
    block: Optional[T1951OutBlock] = None
    block1: List[T1951OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1951RequestHeader",
    "T1951ResponseHeader",
    "T1951InBlock",
    "T1951OutBlock",
    "T1951OutBlock1",
    "T1951Request",
    "T1951Response",
]