"""Pydantic models for LS Securities OpenAPI t8404 (주식선물시간대별체결조회(API용)(t8404)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8404RequestHeader(BlockRequestHeader):
    pass


class T8404ResponseHeader(BlockResponseHeader):
    pass

class T8404InBlock(BaseModel):
    """t8404InBlock — input block. 기본입력"""

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
    cts_time: str = Field(
        ...,
        title="시간CTS",
        description="cts_time — char(10). Consume as returned by LS.",
    )

class T8404OutBlock(BaseModel):
    """t8404OutBlock — output block. 출력"""

    cts_time: str = Field(
        default="",
        title="시간CTS",
        description="cts_time — char(10). Consume as returned by LS.",
    )

class T8404OutBlock1(BaseModel):
    """t8404OutBlock1 — output block (occurs — list of rows). 출력1"""

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
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(8). Consume as returned by LS.",
    )
    cvolume: int = Field(
        default=0,
        title="체결수량",
        description="cvolume — long(8). Consume as returned by LS.",
    )
    chdegree: float = Field(
        default=0.0,
        title="체결강도",
        description="chdegree — float(8.2). Consume as returned by LS.",
    )
    offerho: int = Field(
        default=0,
        title="매도호가",
        description="offerho — long(8). Consume as returned by LS.",
    )
    bidho: int = Field(
        default=0,
        title="매수호가",
        description="bidho — long(8). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — double(12.0). Consume as returned by LS.",
    )
    openyak: int = Field(
        default=0,
        title="미결수량",
        description="openyak — long(8). Consume as returned by LS.",
    )
    jnilopenupdn: int = Field(
        default=0,
        title="미결전일증감",
        description="jnilopenupdn — long(8). Consume as returned by LS.",
    )
    ibasis: int = Field(
        default=0,
        title="이론BASIS",
        description="ibasis — long(8). Consume as returned by LS.",
    )
    sbasis: int = Field(
        default=0,
        title="시장BASIS",
        description="sbasis — long(8). Consume as returned by LS.",
    )
    kasis: float = Field(
        default=0.0,
        title="괴리율",
        description="kasis — float(6.2). Consume as returned by LS.",
    )
    value: float = Field(
        default=0.0,
        title="거래대금",
        description="value — double(12.0). Consume as returned by LS.",
    )
    j_openupdn: int = Field(
        default=0,
        title="미결직전증감",
        description="j_openupdn — long(8). Consume as returned by LS.",
    )
    n_msvolume: float = Field(
        default=0.0,
        title="누적매수체결량",
        description="n_msvolume — double(12.0). Consume as returned by LS.",
    )
    n_mdvolume: float = Field(
        default=0.0,
        title="누적매도체결량",
        description="n_mdvolume — double(12.0). Consume as returned by LS.",
    )
    s_msvolume: float = Field(
        default=0.0,
        title="누적순매수체결량",
        description="s_msvolume — double(12.0). Consume as returned by LS.",
    )
    n_mschecnt: int = Field(
        default=0,
        title="누적매수체결건수",
        description="n_mschecnt — long(8). Consume as returned by LS.",
    )
    n_mdchecnt: int = Field(
        default=0,
        title="누적매도체결건수",
        description="n_mdchecnt — long(8). Consume as returned by LS.",
    )
    s_mschecnt: int = Field(
        default=0,
        title="누적순매수체결건수",
        description="s_mschecnt — long(8). Consume as returned by LS.",
    )

class T8404Request(BaseModel):
    """Request envelope for t8404."""

    header: T8404RequestHeader = T8404RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8404",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8404",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8404Response(BaseModel):
    """Response envelope for t8404."""

    header: Optional[T8404ResponseHeader] = None
    block: Optional[T8404OutBlock] = None
    block1: List[T8404OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8404RequestHeader",
    "T8404ResponseHeader",
    "T8404InBlock",
    "T8404OutBlock",
    "T8404OutBlock1",
    "T8404Request",
    "T8404Response",
]