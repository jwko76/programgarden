"""Pydantic models for LS Securities OpenAPI t8406 (주식선물틱분별체결조회(API용)(t8406)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8406RequestHeader(BlockRequestHeader):
    pass


class T8406ResponseHeader(BlockResponseHeader):
    pass

class T8406InBlock(BaseModel):
    """t8406InBlock — input block. 기본입력"""

    focode: str = Field(
        ...,
        title="단축코드",
        description="focode — char(8). Consume as returned by LS.",
    )
    cgubun: str = Field(
        ...,
        title="챠트구분",
        description="cgubun — char(1). Consume as returned by LS.",
    )
    bgubun: int = Field(
        ...,
        title="분구분",
        description="bgubun — int(3). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="조회건수",
        description="cnt — int(3). Consume as returned by LS.",
    )

class T8406OutBlock1(BaseModel):
    """t8406OutBlock1 — output block (occurs — list of rows). 출력1"""

    chetime: str = Field(
        default="",
        title="시간",
        description="chetime — char(10). Consume as returned by LS.",
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
    open: int = Field(
        default=0,
        title="시가",
        description="open — long(8). Consume as returned by LS.",
    )
    high: int = Field(
        default=0,
        title="고가",
        description="high — long(8). Consume as returned by LS.",
    )
    low: int = Field(
        default=0,
        title="저가",
        description="low — long(8). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — double(12.0). Consume as returned by LS.",
    )
    value: float = Field(
        default=0.0,
        title="거래대금",
        description="value — double(12.0). Consume as returned by LS.",
    )
    openyak: int = Field(
        default=0,
        title="미결수량",
        description="openyak — long(8). Consume as returned by LS.",
    )
    openupdn: int = Field(
        default=0,
        title="미결증감",
        description="openupdn — long(8). Consume as returned by LS.",
    )
    cvolume: int = Field(
        default=0,
        title="체결수량",
        description="cvolume — long(8). Consume as returned by LS.",
    )
    s_mschecnt: int = Field(
        default=0,
        title="매수순간체결건수",
        description="s_mschecnt — long(8). Consume as returned by LS.",
    )
    s_mdchecnt: int = Field(
        default=0,
        title="매도순간체결건수",
        description="s_mdchecnt — long(8). Consume as returned by LS.",
    )
    ss_mschecnt: int = Field(
        default=0,
        title="순매수순간체결건수",
        description="ss_mschecnt — long(8). Consume as returned by LS.",
    )
    s_mschevol: float = Field(
        default=0.0,
        title="매수순간체결량",
        description="s_mschevol — double(12.0). Consume as returned by LS.",
    )
    s_mdchevol: float = Field(
        default=0.0,
        title="매도순간체결량",
        description="s_mdchevol — double(12.0). Consume as returned by LS.",
    )
    ss_mschevol: float = Field(
        default=0.0,
        title="순매수순간체결량",
        description="ss_mschevol — double(12.0). Consume as returned by LS.",
    )
    chdegvol: float = Field(
        default=0.0,
        title="체결강도(거래량)",
        description="chdegvol — float(8.2). Consume as returned by LS.",
    )
    chdegcnt: float = Field(
        default=0.0,
        title="체결강도(건수)",
        description="chdegcnt — float(8.2). Consume as returned by LS.",
    )

class T8406Request(BaseModel):
    """Request envelope for t8406."""

    header: T8406RequestHeader = T8406RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8406",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8406",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8406Response(BaseModel):
    """Response envelope for t8406."""

    header: Optional[T8406ResponseHeader] = None
    block1: List[T8406OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8406RequestHeader",
    "T8406ResponseHeader",
    "T8406InBlock",
    "T8406OutBlock1",
    "T8406Request",
    "T8406Response",
]