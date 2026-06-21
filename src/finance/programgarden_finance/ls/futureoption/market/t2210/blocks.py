"""Pydantic models for LS Securities OpenAPI t2210 (선물옵션시간대별체결조회(단일출력용)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T2210RequestHeader(BlockRequestHeader):
    pass


class T2210ResponseHeader(BlockResponseHeader):
    pass

class T2210InBlock(BaseModel):
    """t2210InBlock — input block. 기본입력"""

    focode: str = Field(
        ...,
        title="단축코드",
        description="focode — char(8). Consume as returned by LS.",
    )
    cvolume: int = Field(
        ...,
        title="특이거래량",
        description="cvolume — long(12). Consume as returned by LS.",
    )
    stime: str = Field(
        ...,
        title="시작시간",
        description="stime — char(4). Consume as returned by LS.",
    )
    etime: str = Field(
        ...,
        title="종료시간",
        description="etime — char(4). Consume as returned by LS.",
    )

class T2210OutBlock(BaseModel):
    """t2210OutBlock — output block. 출력"""

    mdvolume: int = Field(
        default=0,
        title="매도체결수량",
        description="mdvolume — long(8). Consume as returned by LS.",
    )
    mdchecnt: int = Field(
        default=0,
        title="매도체결건수",
        description="mdchecnt — long(8). Consume as returned by LS.",
    )
    msvolume: int = Field(
        default=0,
        title="매수체결수량",
        description="msvolume — long(8). Consume as returned by LS.",
    )
    mschecnt: int = Field(
        default=0,
        title="매수체결건수",
        description="mschecnt — long(8). Consume as returned by LS.",
    )

class T2210Request(BaseModel):
    """Request envelope for t2210."""

    header: T2210RequestHeader = T2210RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t2210",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t2210",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T2210Response(BaseModel):
    """Response envelope for t2210."""

    header: Optional[T2210ResponseHeader] = None
    block: Optional[T2210OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T2210RequestHeader",
    "T2210ResponseHeader",
    "T2210InBlock",
    "T2210OutBlock",
    "T2210Request",
    "T2210Response",
]