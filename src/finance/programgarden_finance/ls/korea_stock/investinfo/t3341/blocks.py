"""Pydantic models for LS Securities OpenAPI t3341 (재무순위종합(t3341)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T3341RequestHeader(BlockRequestHeader):
    pass


class T3341ResponseHeader(BlockResponseHeader):
    pass

class T3341InBlock(BaseModel):
    """t3341InBlock — input block. 기본입력"""

    gubun: str = Field(
        ...,
        title="시장구분",
        description="gubun — char(1). Consume as returned by LS.",
    )
    gubun1: str = Field(
        ...,
        title="순위구분(1:매출액증가율2:영업이익증가율3:세전계속이익증가율4:부채비율5:유보율6:EPS7:BPS8:ROE9:PERa:PBRb:PEG)",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    gubun2: str = Field(
        ...,
        title="대비구분",
        description="gubun2 — char(1). Consume as returned by LS.",
    )
    idx: int = Field(
        ...,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T3341OutBlock(BaseModel):
    """t3341OutBlock — output block. 출력"""

    cnt: int = Field(
        default=0,
        title="CNT",
        description="cnt — long(4). Consume as returned by LS.",
    )
    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T3341OutBlock1(BaseModel):
    """t3341OutBlock1 — output block (occurs — list of rows). 출력1"""

    rank: int = Field(
        default=0,
        title="순위",
        description="rank — long(4). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="기업명",
        description="hname — char(20). Consume as returned by LS.",
    )
    salesgrowth: int = Field(
        default=0,
        title="매출액증가율",
        description="salesgrowth — long(12). Consume as returned by LS.",
    )
    operatingincomegrowt: int = Field(
        default=0,
        title="영업이익증가율",
        description="operatingincomegrowt — long(12). Consume as returned by LS.",
    )
    ordinaryincomegrowth: int = Field(
        default=0,
        title="경상이익증가율",
        description="ordinaryincomegrowth — long(12). Consume as returned by LS.",
    )
    liabilitytoequity: int = Field(
        default=0,
        title="부채비율",
        description="liabilitytoequity — long(12). Consume as returned by LS.",
    )
    enterpriseratio: int = Field(
        default=0,
        title="유보율",
        description="enterpriseratio — long(12). Consume as returned by LS.",
    )
    eps: int = Field(
        default=0,
        title="EPS",
        description="eps — long(12). Consume as returned by LS.",
    )
    bps: int = Field(
        default=0,
        title="BPS",
        description="bps — long(12). Consume as returned by LS.",
    )
    roe: int = Field(
        default=0,
        title="ROE",
        description="roe — long(12). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    per: float = Field(
        default=0.0,
        title="PER",
        description="per — float(13.2). Consume as returned by LS.",
    )
    pbr: float = Field(
        default=0.0,
        title="PBR",
        description="pbr — float(13.2). Consume as returned by LS.",
    )
    peg: float = Field(
        default=0.0,
        title="PEG",
        description="peg — float(13.2). Consume as returned by LS.",
    )

class T3341Request(BaseModel):
    """Request envelope for t3341."""

    header: T3341RequestHeader = T3341RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t3341",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t3341",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T3341Response(BaseModel):
    """Response envelope for t3341."""

    header: Optional[T3341ResponseHeader] = None
    block: Optional[T3341OutBlock] = None
    block1: List[T3341OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T3341RequestHeader",
    "T3341ResponseHeader",
    "T3341InBlock",
    "T3341OutBlock",
    "T3341OutBlock1",
    "T3341Request",
    "T3341Response",
]