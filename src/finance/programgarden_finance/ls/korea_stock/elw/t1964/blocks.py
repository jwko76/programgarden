"""Pydantic models for LS Securities OpenAPI t1964 (ELW전광판(t1964)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1964RequestHeader(BlockRequestHeader):
    pass


class T1964ResponseHeader(BlockResponseHeader):
    pass

class T1964InBlock(BaseModel):
    """t1964InBlock — input block. 기본입력"""

    item: str = Field(
        ...,
        title="기초자산코드",
        description="item — char(12). Consume as returned by LS.",
    )
    issuercd: str = Field(
        ...,
        title="발행사",
        description="issuercd — char(12). Consume as returned by LS.",
    )
    lastmonth: str = Field(
        ...,
        title="만기월물",
        description="lastmonth — char(6). Consume as returned by LS.",
    )
    elwopt: str = Field(
        ...,
        title="콜풋구분",
        description="elwopt — char(1). Consume as returned by LS.",
    )
    atmgubun: str = Field(
        ...,
        title="머니구분",
        description="atmgubun — char(1). Consume as returned by LS.",
    )
    elwtype: str = Field(
        ...,
        title="권리행사방식",
        description="elwtype — char(2). Consume as returned by LS.",
    )
    settletype: str = Field(
        ...,
        title="결제방법",
        description="settletype — char(2). Consume as returned by LS.",
    )
    elwexecgubun: str = Field(
        ...,
        title="행사기초자산구분",
        description="elwexecgubun — char(1). Consume as returned by LS.",
    )
    fromrat: str = Field(
        ...,
        title="시작비율",
        description="fromrat — char(5). Consume as returned by LS.",
    )
    torat: str = Field(
        ...,
        title="종료비율",
        description="torat — char(5). Consume as returned by LS.",
    )
    volume: str = Field(
        ...,
        title="거래량",
        description="volume — char(12). Consume as returned by LS.",
    )

class T1964OutBlock1(BaseModel):
    """t1964OutBlock1 — output block (occurs — list of rows). 출력1"""

    shcode: str = Field(
        default="",
        title="ELW코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(40). Consume as returned by LS.",
    )
    item1: str = Field(
        default="",
        title="기초자산코드",
        description="item1 — char(6). Consume as returned by LS.",
    )
    itemnm: str = Field(
        default="",
        title="기초자산명",
        description="itemnm — char(20). Consume as returned by LS.",
    )
    issuernmk: str = Field(
        default="",
        title="발행사",
        description="issuernmk — char(40). Consume as returned by LS.",
    )
    elwopt: str = Field(
        default="",
        title="콜풋구분",
        description="elwopt — char(4). Consume as returned by LS.",
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
    volume: int = Field(
        default=0,
        title="거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    elwexec: float = Field(
        default=0.0,
        title="행사가",
        description="elwexec — float(10.2). Consume as returned by LS.",
    )
    jandatecnt: int = Field(
        default=0,
        title="잔존일수",
        description="jandatecnt — long(8). Consume as returned by LS.",
    )
    convrate: float = Field(
        default=0.0,
        title="전환비율",
        description="convrate — float(8.4). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="최종거래일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    mmsdate: str = Field(
        default="",
        title="행사개시일",
        description="mmsdate — char(8). Consume as returned by LS.",
    )
    payday: str = Field(
        default="",
        title="지급일",
        description="payday — char(8). Consume as returned by LS.",
    )
    listing: int = Field(
        default=0,
        title="발행수량",
        description="listing — long(8). Consume as returned by LS.",
    )
    atmgbnm: str = Field(
        default="",
        title="머니구분",
        description="atmgbnm — char(10). Consume as returned by LS.",
    )
    parity: float = Field(
        default=0.0,
        title="패리티",
        description="parity — float(6.2). Consume as returned by LS.",
    )
    preminum: float = Field(
        default=0.0,
        title="프리미엄",
        description="preminum — float(10.2). Consume as returned by LS.",
    )
    spread: float = Field(
        default=0.0,
        title="스프래드",
        description="spread — float(3.2). Consume as returned by LS.",
    )
    berate: float = Field(
        default=0.0,
        title="손익분기율",
        description="berate — float(6.2). Consume as returned by LS.",
    )
    capt: float = Field(
        default=0.0,
        title="자본지지율",
        description="capt — float(6.2). Consume as returned by LS.",
    )
    gearing: float = Field(
        default=0.0,
        title="기어링",
        description="gearing — float(6.2). Consume as returned by LS.",
    )
    egearing: float = Field(
        default=0.0,
        title="e기어링",
        description="egearing — float(6.2). Consume as returned by LS.",
    )
    itemprice: int = Field(
        default=0,
        title="기초자산현재가",
        description="itemprice — long(8). Consume as returned by LS.",
    )
    itemsign: str = Field(
        default="",
        title="기초자산전일대비구분",
        description="itemsign — char(1). Consume as returned by LS.",
    )
    itemchange: int = Field(
        default=0,
        title="기초자산전일대비",
        description="itemchange — long(8). Consume as returned by LS.",
    )
    itemdiff: float = Field(
        default=0.0,
        title="기초자산등락율",
        description="itemdiff — float(6.2). Consume as returned by LS.",
    )
    itemvolume: int = Field(
        default=0,
        title="기초자산거래량",
        description="itemvolume — long(12). Consume as returned by LS.",
    )
    jnilvolume: int = Field(
        default=0,
        title="전일거래량",
        description="jnilvolume — long(12). Consume as returned by LS.",
    )
    theoryprice: float = Field(
        default=0.0,
        title="이론가",
        description="theoryprice — float(10.2). Consume as returned by LS.",
    )
    lp_rate: float = Field(
        default=0.0,
        title="LP보유비율",
        description="lp_rate — float(5.2). Consume as returned by LS.",
    )
    impv: float = Field(
        default=0.0,
        title="내재변동성",
        description="impv — float(6.2). Consume as returned by LS.",
    )
    delta: float = Field(
        default=0.0,
        title="델타",
        description="delta — float(10.6). Consume as returned by LS.",
    )
    theta: float = Field(
        default=0.0,
        title="쎄타",
        description="theta — float(10.6). Consume as returned by LS.",
    )

class T1964Request(BaseModel):
    """Request envelope for t1964."""

    header: T1964RequestHeader = T1964RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1964",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1964",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1964Response(BaseModel):
    """Response envelope for t1964."""

    header: Optional[T1964ResponseHeader] = None
    block1: List[T1964OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1964RequestHeader",
    "T1964ResponseHeader",
    "T1964InBlock",
    "T1964OutBlock1",
    "T1964Request",
    "T1964Response",
]