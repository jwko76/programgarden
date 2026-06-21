"""Pydantic models for LS Securities OpenAPI t1973 (ELW시간대별예상체결조회(t1973)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1973RequestHeader(BlockRequestHeader):
    pass


class T1973ResponseHeader(BlockResponseHeader):
    pass

class T1973InBlock(BaseModel):
    """t1973InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    cts_time: str = Field(
        ...,
        title="시간CTS",
        description="cts_time — char(8). Consume as returned by LS.",
    )

class T1973OutBlock(BaseModel):
    """t1973OutBlock — output block. 출력"""

    cts_time: str = Field(
        default="",
        title="시간CTS",
        description="cts_time — char(8). Consume as returned by LS.",
    )

class T1973OutBlock1(BaseModel):
    """t1973OutBlock1 — output block (occurs — list of rows). 출력1"""

    chetime: str = Field(
        default="",
        title="시간",
        description="chetime — char(8). Consume as returned by LS.",
    )
    yeprice: int = Field(
        default=0,
        title="예상체결가격",
        description="yeprice — long(8). Consume as returned by LS.",
    )
    yegubun: str = Field(
        default="",
        title="예상체결구분",
        description="yegubun — char(1). Consume as returned by LS.",
    )
    jnilysign: str = Field(
        default="",
        title="전일종가대비구분",
        description="jnilysign — char(1). Consume as returned by LS.",
    )
    jnilychange: int = Field(
        default=0,
        title="전일종가대비",
        description="jnilychange — long(8). Consume as returned by LS.",
    )
    yediff: float = Field(
        default=0.0,
        title="예상체결등락율",
        description="yediff — float(6.2). Consume as returned by LS.",
    )
    yevolume: int = Field(
        default=0,
        title="예상체결량",
        description="yevolume — long(12). Consume as returned by LS.",
    )
    ymdvolume: int = Field(
        default=0,
        title="예상매도체결량",
        description="ymdvolume — long(12). Consume as returned by LS.",
    )
    ymsvolume: int = Field(
        default=0,
        title="예상매수체결량",
        description="ymsvolume — long(12). Consume as returned by LS.",
    )

class T1973Request(BaseModel):
    """Request envelope for t1973."""

    header: T1973RequestHeader = T1973RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1973",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1973",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1973Response(BaseModel):
    """Response envelope for t1973."""

    header: Optional[T1973ResponseHeader] = None
    block: Optional[T1973OutBlock] = None
    block1: List[T1973OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1973RequestHeader",
    "T1973ResponseHeader",
    "T1973InBlock",
    "T1973OutBlock",
    "T1973OutBlock1",
    "T1973Request",
    "T1973Response",
]