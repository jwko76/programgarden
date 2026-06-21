"""Pydantic models for LS Securities OpenAPI t1988 (기초자산리스트조회(t1988)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1988RequestHeader(BlockRequestHeader):
    pass


class T1988ResponseHeader(BlockResponseHeader):
    pass

class T1988InBlock(BaseModel):
    """t1988InBlock — input block. 기본입력"""

    mkt_gb: str = Field(
        ...,
        title="시장구분(0:전체1:코스피2:코스닥)",
        description="mkt_gb — char(1). Consume as returned by LS.",
    )
    chk_price: str = Field(
        ...,
        title="가격설정(0:전체1:조건설정)",
        description="chk_price — char(1). Consume as returned by LS.",
    )
    from_price: str = Field(
        ...,
        title="가격1",
        description="from_price — char(12). Consume as returned by LS.",
    )
    to_price: str = Field(
        ...,
        title="가격2",
        description="to_price — char(12). Consume as returned by LS.",
    )
    chk_vol: str = Field(
        ...,
        title="거래량설정(0:전체1:조건설정)",
        description="chk_vol — char(1). Consume as returned by LS.",
    )
    from_vol: str = Field(
        ...,
        title="거래량1",
        description="from_vol — char(12). Consume as returned by LS.",
    )
    to_vol: str = Field(
        ...,
        title="거래량2",
        description="to_vol — char(12). Consume as returned by LS.",
    )
    chk_rate: str = Field(
        ...,
        title="등락율설정(0:전체1:조건설정)",
        description="chk_rate — char(1). Consume as returned by LS.",
    )
    from_rate: float = Field(
        ...,
        title="등락율1",
        description="from_rate — float(5.2). Consume as returned by LS.",
    )
    to_rate: float = Field(
        ...,
        title="등락율2",
        description="to_rate — float(5.2). Consume as returned by LS.",
    )
    chk_amt: str = Field(
        ...,
        title="거래대금설정(0:전체1:조건설정)",
        description="chk_amt — char(1). Consume as returned by LS.",
    )
    from_amt: str = Field(
        ...,
        title="거래대금1",
        description="from_amt — char(12). Consume as returned by LS.",
    )
    to_amt: str = Field(
        ...,
        title="거래대금2",
        description="to_amt — char(12). Consume as returned by LS.",
    )
    chk_up: str = Field(
        ...,
        title="양봉설정(0:전체1:조건설정)",
        description="chk_up — char(1). Consume as returned by LS.",
    )
    chk_down: str = Field(
        ...,
        title="음봉설정(0:전체1:조건설정)",
        description="chk_down — char(1). Consume as returned by LS.",
    )

class T1988OutBlock(BaseModel):
    """t1988OutBlock — output block. 출력1"""

    ksp_cnt: str = Field(
        default="",
        title="코스피종목건수",
        description="ksp_cnt — char(4). Consume as returned by LS.",
    )
    ksd_cnt: str = Field(
        default="",
        title="코스닥종목건수",
        description="ksd_cnt — char(4). Consume as returned by LS.",
    )

class T1988OutBlock1(BaseModel):
    """t1988OutBlock1 — output block (occurs — list of rows). 출력1"""

    shcode: str = Field(
        default="",
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    expcode: str = Field(
        default="",
        title="표준코드",
        description="expcode — char(12). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(20). Consume as returned by LS.",
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
        title="누적거래량(주)",
        description="volume — char(12). Consume as returned by LS.",
    )
    value: str = Field(
        default="",
        title="누적거래대금(백만)",
        description="value — char(12). Consume as returned by LS.",
    )
    mkt_gb: str = Field(
        default="",
        title="시장구분",
        description="mkt_gb — char(1). Consume as returned by LS.",
    )
    jvolume: str = Field(
        default="",
        title="전일동시간대거래량(주)",
        description="jvolume — char(12). Consume as returned by LS.",
    )

class T1988Request(BaseModel):
    """Request envelope for t1988."""

    header: T1988RequestHeader = T1988RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1988",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1988",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1988Response(BaseModel):
    """Response envelope for t1988."""

    header: Optional[T1988ResponseHeader] = None
    block: Optional[T1988OutBlock] = None
    block1: List[T1988OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1988RequestHeader",
    "T1988ResponseHeader",
    "T1988InBlock",
    "T1988OutBlock",
    "T1988OutBlock1",
    "T1988Request",
    "T1988Response",
]