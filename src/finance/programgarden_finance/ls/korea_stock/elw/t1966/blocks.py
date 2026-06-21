"""Pydantic models for LS Securities OpenAPI t1966 (ELW거래대금상위(t1966)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1966RequestHeader(BlockRequestHeader):
    pass


class T1966ResponseHeader(BlockResponseHeader):
    pass

class T1966InBlock(BaseModel):
    """t1966InBlock — input block. 기본입력"""

    gubun: str = Field(
        ...,
        title="당일전일(0:당일1:전일)",
        description="gubun — char(1). Consume as returned by LS.",
    )
    ggubun: str = Field(
        ...,
        title="권리유형구분(00:EX01:콜02:풋'':전체)",
        description="ggubun — char(2). Consume as returned by LS.",
    )
    itemcode: str = Field(
        ...,
        title="기초자산종목",
        description="itemcode — char(12). Consume as returned by LS.",
    )
    lastdate: str = Field(
        ...,
        title="조회만기일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    exgubun: str = Field(
        ...,
        title="대상제외",
        description="exgubun — char(6). Consume as returned by LS.",
    )
    sprice: int = Field(
        ...,
        title="시작가격",
        description="sprice — long(8). Consume as returned by LS.",
    )
    eprice: int = Field(
        ...,
        title="종료가격",
        description="eprice — long(8). Consume as returned by LS.",
    )
    volume: int = Field(
        ...,
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    sjanday: int = Field(
        ...,
        title="잔존시작일수",
        description="sjanday — long(8). Consume as returned by LS.",
    )
    ejanday: int = Field(
        ...,
        title="잔존종료일수",
        description="ejanday — long(8). Consume as returned by LS.",
    )
    idx: int = Field(
        ...,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1966OutBlock(BaseModel):
    """t1966OutBlock — output block. 출력"""

    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1966OutBlock1(BaseModel):
    """t1966OutBlock1 — output block (occurs — list of rows). 출력1"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(40). Consume as returned by LS.",
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
    value: float = Field(
        default=0.0,
        title="누적거래대금",
        description="value — double(12.0). Consume as returned by LS.",
    )
    jnilvalue: float = Field(
        default=0.0,
        title="전일거래대금",
        description="jnilvalue — double(12.0). Consume as returned by LS.",
    )
    elwexec: float = Field(
        default=0.0,
        title="행사가",
        description="elwexec — double(10.2). Consume as returned by LS.",
    )
    convrate: float = Field(
        default=0.0,
        title="전환비율",
        description="convrate — double(12.4). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="만기일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    itemcode: str = Field(
        default="",
        title="기초자산종목코드",
        description="itemcode — char(12). Consume as returned by LS.",
    )
    itemshcode: str = Field(
        default="",
        title="기초자산단축코드",
        description="itemshcode — char(9). Consume as returned by LS.",
    )
    itemname: str = Field(
        default="",
        title="기초자산종목명",
        description="itemname — char(20). Consume as returned by LS.",
    )
    itemprice: str = Field(
        default="",
        title="기초자산현재가",
        description="itemprice — char(10). Consume as returned by LS.",
    )
    itemsign: str = Field(
        default="",
        title="기초자산대비구분",
        description="itemsign — char(1). Consume as returned by LS.",
    )
    itemchange: str = Field(
        default="",
        title="기초자산전일대비",
        description="itemchange — char(10). Consume as returned by LS.",
    )
    itemdiff: float = Field(
        default=0.0,
        title="기초자산등락율",
        description="itemdiff — double(6.2). Consume as returned by LS.",
    )
    elwshcode: str = Field(
        default="",
        title="ELW종목코드",
        description="elwshcode — char(6). Consume as returned by LS.",
    )

class T1966Request(BaseModel):
    """Request envelope for t1966."""

    header: T1966RequestHeader = T1966RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1966",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1966",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1966Response(BaseModel):
    """Response envelope for t1966."""

    header: Optional[T1966ResponseHeader] = None
    block: Optional[T1966OutBlock] = None
    block1: List[T1966OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1966RequestHeader",
    "T1966ResponseHeader",
    "T1966InBlock",
    "T1966OutBlock",
    "T1966OutBlock1",
    "T1966Request",
    "T1966Response",
]