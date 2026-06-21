"""Pydantic models for LS Securities OpenAPI t1615 (투자자매매종합1(t1615)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1615RequestHeader(BlockRequestHeader):
    pass


class T1615ResponseHeader(BlockResponseHeader):
    pass

class T1615InBlock(BaseModel):
    """t1615InBlock — input block. 기본입력"""

    gubun1: str = Field(
        ...,
        title="주식구분",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    gubun2: str = Field(
        ...,
        title="옵션구분",
        description="gubun2 — char(1). Consume as returned by LS.",
    )
    exchgubun: str = Field(
        ...,
        title="거래소구분코드",
        description="exchgubun — char(1). Consume as returned by LS.",
    )

class T1615OutBlock(BaseModel):
    """t1615OutBlock — output block. 출력"""

    dwvolume: int = Field(
        default=0,
        title="위탁매도수량",
        description="dwvolume — long(12). Consume as returned by LS.",
    )
    dwvalue: int = Field(
        default=0,
        title="위탁매도금액",
        description="dwvalue — long(12). Consume as returned by LS.",
    )
    djvolume: int = Field(
        default=0,
        title="자기매도수량",
        description="djvolume — long(12). Consume as returned by LS.",
    )
    djvalue: int = Field(
        default=0,
        title="자기매도금액",
        description="djvalue — long(12). Consume as returned by LS.",
    )
    sum_volume: int = Field(
        default=0,
        title="합계수량",
        description="sum_volume — long(12). Consume as returned by LS.",
    )
    sum_value: int = Field(
        default=0,
        title="합계금액",
        description="sum_value — long(12). Consume as returned by LS.",
    )

class T1615OutBlock1(BaseModel):
    """t1615OutBlock1 — output block (occurs — list of rows). 출력1"""

    hname: str = Field(
        default="",
        title="시장명",
        description="hname — char(20). Consume as returned by LS.",
    )
    sv_08: int = Field(
        default=0,
        title="개인",
        description="sv_08 — long(12). Consume as returned by LS.",
    )
    sv_17: int = Field(
        default=0,
        title="외국인",
        description="sv_17 — long(12). Consume as returned by LS.",
    )
    sv_18: int = Field(
        default=0,
        title="기관계",
        description="sv_18 — long(12). Consume as returned by LS.",
    )
    sv_07: int = Field(
        default=0,
        title="증권",
        description="sv_07 — long(12). Consume as returned by LS.",
    )

class T1615Request(BaseModel):
    """Request envelope for t1615."""

    header: T1615RequestHeader = T1615RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1615",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1615",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1615Response(BaseModel):
    """Response envelope for t1615."""

    header: Optional[T1615ResponseHeader] = None
    block: Optional[T1615OutBlock] = None
    block1: List[T1615OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1615RequestHeader",
    "T1615ResponseHeader",
    "T1615InBlock",
    "T1615OutBlock",
    "T1615OutBlock1",
    "T1615Request",
    "T1615Response",
]