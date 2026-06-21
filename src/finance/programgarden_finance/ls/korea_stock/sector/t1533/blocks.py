"""Pydantic models for LS Securities OpenAPI t1533 (특이테마(t1533)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1533RequestHeader(BlockRequestHeader):
    pass


class T1533ResponseHeader(BlockResponseHeader):
    pass

class T1533InBlock(BaseModel):
    """t1533InBlock — input block. 기본입력"""

    gubun: str = Field(
        ...,
        title="구분",
        description="gubun — char(1). Consume as returned by LS.",
    )
    chgdate: int = Field(
        ...,
        title="대비일자",
        description="chgdate — long(2). Consume as returned by LS.",
    )

class T1533OutBlock(BaseModel):
    """t1533OutBlock — output block. 기본출력"""

    bdate: str = Field(
        default="",
        title="일자",
        description="bdate — char(8). Consume as returned by LS.",
    )

class T1533OutBlock1(BaseModel):
    """t1533OutBlock1 — output block (occurs — list of rows). 출력1"""

    tmname: str = Field(
        default="",
        title="테마명",
        description="tmname — char(36). Consume as returned by LS.",
    )
    totcnt: int = Field(
        default=0,
        title="전체",
        description="totcnt — long(4). Consume as returned by LS.",
    )
    upcnt: int = Field(
        default=0,
        title="상승",
        description="upcnt — long(4). Consume as returned by LS.",
    )
    dncnt: int = Field(
        default=0,
        title="하락",
        description="dncnt — long(4). Consume as returned by LS.",
    )
    uprate: float = Field(
        default=0.0,
        title="상승비율",
        description="uprate — float(6.2). Consume as returned by LS.",
    )
    diff_vol: float = Field(
        default=0.0,
        title="거래증가율",
        description="diff_vol — float(10.2). Consume as returned by LS.",
    )
    avgdiff: float = Field(
        default=0.0,
        title="평균등락율",
        description="avgdiff — float(6.2). Consume as returned by LS.",
    )
    chgdiff: float = Field(
        default=0.0,
        title="대비등락율",
        description="chgdiff — float(6.2). Consume as returned by LS.",
    )
    tmcode: str = Field(
        default="",
        title="테마코드",
        description="tmcode — char(4). Consume as returned by LS.",
    )

class T1533Request(BaseModel):
    """Request envelope for t1533."""

    header: T1533RequestHeader = T1533RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1533",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1533",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1533Response(BaseModel):
    """Response envelope for t1533."""

    header: Optional[T1533ResponseHeader] = None
    block: Optional[T1533OutBlock] = None
    block1: List[T1533OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1533RequestHeader",
    "T1533ResponseHeader",
    "T1533InBlock",
    "T1533OutBlock",
    "T1533OutBlock1",
    "T1533Request",
    "T1533Response",
]