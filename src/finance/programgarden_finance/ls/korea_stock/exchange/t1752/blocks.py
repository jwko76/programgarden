"""Pydantic models for LS Securities OpenAPI t1752 (종목별상위회원사(t1752)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1752RequestHeader(BlockRequestHeader):
    pass


class T1752ResponseHeader(BlockResponseHeader):
    pass

class T1752InBlock(BaseModel):
    """t1752InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    traddate1: str = Field(
        ...,
        title="조회날짜1",
        description="traddate1 — char(8). Consume as returned by LS.",
    )
    traddate2: str = Field(
        ...,
        title="조회날짜2",
        description="traddate2 — char(8). Consume as returned by LS.",
    )
    fwgubun1: str = Field(
        ...,
        title="외국계구분",
        description="fwgubun1 — char(1). Consume as returned by LS.",
    )
    cts_idx: int = Field(
        ...,
        title="CTSIDX",
        description="cts_idx — long(4). Consume as returned by LS.",
    )
    exchgubun: str = Field(
        ...,
        title="거래소구분코드",
        description="exchgubun — char(1). Consume as returned by LS.",
    )

class T1752OutBlock(BaseModel):
    """t1752OutBlock — output block. 기본출력"""

    fwdvl: int = Field(
        default=0,
        title="외국계매도",
        description="fwdvl — long(12). Consume as returned by LS.",
    )
    fwsvl: int = Field(
        default=0,
        title="외국계매수",
        description="fwsvl — long(12). Consume as returned by LS.",
    )
    cts_idx: int = Field(
        default=0,
        title="CTSIDX",
        description="cts_idx — long(4). Consume as returned by LS.",
    )

class T1752OutBlock1(BaseModel):
    """t1752OutBlock1 — output block (occurs — list of rows). 출력1"""

    tradname: str = Field(
        default="",
        title="회원사",
        description="tradname — char(20). Consume as returned by LS.",
    )
    tradmdvol: int = Field(
        default=0,
        title="매도수량",
        description="tradmdvol — long(12). Consume as returned by LS.",
    )
    tradmsvol: int = Field(
        default=0,
        title="매수수량",
        description="tradmsvol — long(12). Consume as returned by LS.",
    )
    tradmssvol: int = Field(
        default=0,
        title="순매수",
        description="tradmssvol — long(12). Consume as returned by LS.",
    )
    wintrd: int = Field(
        default=0,
        title="창구거래",
        description="wintrd — long(12). Consume as returned by LS.",
    )
    winrat: float = Field(
        default=0.0,
        title="비중",
        description="winrat — float(6.1). Consume as returned by LS.",
    )
    tradno: str = Field(
        default="",
        title="회원사코드",
        description="tradno — char(3). Consume as returned by LS.",
    )
    wgubun: str = Field(
        default="",
        title="외국계여부",
        description="wgubun — char(1). Consume as returned by LS.",
    )
    swinrat: float = Field(
        default=0.0,
        title="순비중",
        description="swinrat — float(6.1). Consume as returned by LS.",
    )

class T1752Request(BaseModel):
    """Request envelope for t1752."""

    header: T1752RequestHeader = T1752RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1752",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1752",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1752Response(BaseModel):
    """Response envelope for t1752."""

    header: Optional[T1752ResponseHeader] = None
    block: Optional[T1752OutBlock] = None
    block1: List[T1752OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1752RequestHeader",
    "T1752ResponseHeader",
    "T1752InBlock",
    "T1752OutBlock",
    "T1752OutBlock1",
    "T1752Request",
    "T1752Response",
]