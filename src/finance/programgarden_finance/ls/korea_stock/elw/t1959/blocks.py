"""Pydantic models for LS Securities OpenAPI t1959 (LP대상종목정보조회(t1959)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1959RequestHeader(BlockRequestHeader):
    pass


class T1959ResponseHeader(BlockResponseHeader):
    pass

class T1959InBlock(BaseModel):
    """t1959InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1959OutBlock1(BaseModel):
    """t1959OutBlock1 — output block (occurs — list of rows). LP대상전종목정보"""

    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(40). Consume as returned by LS.",
    )
    price: str = Field(
        default="",
        title="현재가",
        description="price — char(12). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="부호",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: str = Field(
        default="",
        title="대비",
        description="change — char(12). Consume as returned by LS.",
    )
    rate: float = Field(
        default=0.0,
        title="등락율",
        description="rate — float(5.2). Consume as returned by LS.",
    )
    volume: str = Field(
        default="",
        title="누적거래량",
        description="volume — char(12). Consume as returned by LS.",
    )
    value: str = Field(
        default="",
        title="누적거래대금",
        description="value — char(12). Consume as returned by LS.",
    )
    lp_gb: str = Field(
        default="",
        title="LP주문가능여부",
        description="lp_gb — char(4). Consume as returned by LS.",
    )
    lp_mem_nm1: str = Field(
        default="",
        title="LP회원사명1",
        description="lp_mem_nm1 — char(20). Consume as returned by LS.",
    )
    lp_mem_nm2: str = Field(
        default="",
        title="LP회원사명2",
        description="lp_mem_nm2 — char(20). Consume as returned by LS.",
    )
    lp_mem_nm3: str = Field(
        default="",
        title="LP회원사명3",
        description="lp_mem_nm3 — char(20). Consume as returned by LS.",
    )
    lp_mem_nm4: str = Field(
        default="",
        title="LP회원사명4",
        description="lp_mem_nm4 — char(20). Consume as returned by LS.",
    )
    lp_mem_nm5: str = Field(
        default="",
        title="LP회원사명5",
        description="lp_mem_nm5 — char(20). Consume as returned by LS.",
    )
    lp_min_qty: str = Field(
        default="",
        title="LP최소호가수량",
        description="lp_min_qty — char(10). Consume as returned by LS.",
    )
    lp_st_date: str = Field(
        default="",
        title="LP시작일",
        description="lp_st_date — char(8). Consume as returned by LS.",
    )

class T1959Request(BaseModel):
    """Request envelope for t1959."""

    header: T1959RequestHeader = T1959RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1959",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1959",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1959Response(BaseModel):
    """Response envelope for t1959."""

    header: Optional[T1959ResponseHeader] = None
    block1: List[T1959OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1959RequestHeader",
    "T1959ResponseHeader",
    "T1959InBlock",
    "T1959OutBlock1",
    "T1959Request",
    "T1959Response",
]