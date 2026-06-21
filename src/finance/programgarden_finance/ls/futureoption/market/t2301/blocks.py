"""Pydantic models for LS Securities OpenAPI t2301 (옵션전광판(t2301)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T2301RequestHeader(BlockRequestHeader):
    pass


class T2301ResponseHeader(BlockResponseHeader):
    pass

class T2301InBlock(BaseModel):
    """t2301InBlock — input block. 기본입력"""

    yyyymm: str = Field(
        ...,
        title="월물",
        description="yyyymm — char(6). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="미니구분(M:미니G:정규)",
        description="gubun — char(1). Consume as returned by LS.",
    )

class T2301OutBlock(BaseModel):
    """t2301OutBlock — output block. 출력"""

    histimpv: int = Field(
        default=0,
        title="역사적변동성",
        description="histimpv — long(4). Consume as returned by LS.",
    )
    jandatecnt: int = Field(
        default=0,
        title="옵션잔존일",
        description="jandatecnt — long(4). Consume as returned by LS.",
    )
    cimpv: float = Field(
        default=0.0,
        title="콜옵션대표IV",
        description="cimpv — float(6.3). Consume as returned by LS.",
    )
    pimpv: float = Field(
        default=0.0,
        title="풋옵션대표IV",
        description="pimpv — float(6.3). Consume as returned by LS.",
    )
    gmprice: float = Field(
        default=0.0,
        title="근월물현재가",
        description="gmprice — float(6.2). Consume as returned by LS.",
    )
    gmsign: str = Field(
        default="",
        title="근월물전일대비구분",
        description="gmsign — char(1). Consume as returned by LS.",
    )
    gmchange: float = Field(
        default=0.0,
        title="근월물전일대비",
        description="gmchange — float(6.2). Consume as returned by LS.",
    )
    gmdiff: float = Field(
        default=0.0,
        title="근월물등락율",
        description="gmdiff — float(6.2). Consume as returned by LS.",
    )
    gmvolume: int = Field(
        default=0,
        title="근월물거래량",
        description="gmvolume — long(12). Consume as returned by LS.",
    )
    gmshcode: str = Field(
        default="",
        title="근월물선물코드",
        description="gmshcode — char(8). Consume as returned by LS.",
    )

class T2301OutBlock1(BaseModel):
    """t2301OutBlock1 — output block (occurs — list of rows). 출력1"""

    actprice: float = Field(
        default=0.0,
        title="행사가",
        description="actprice — float(6.2). Consume as returned by LS.",
    )
    optcode: str = Field(
        default="",
        title="콜옵션코드",
        description="optcode — char(8). Consume as returned by LS.",
    )
    price: float = Field(
        default=0.0,
        title="현재가",
        description="price — float(6.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(6.2). Consume as returned by LS.",
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
    iv: float = Field(
        default=0.0,
        title="IV",
        description="iv — float(6.2). Consume as returned by LS.",
    )
    mgjv: int = Field(
        default=0,
        title="미결제약정",
        description="mgjv — long(12). Consume as returned by LS.",
    )
    mgjvupdn: int = Field(
        default=0,
        title="미결제약정증감",
        description="mgjvupdn — long(12). Consume as returned by LS.",
    )
    offerho1: float = Field(
        default=0.0,
        title="매도호가",
        description="offerho1 — float(6.2). Consume as returned by LS.",
    )
    bidho1: float = Field(
        default=0.0,
        title="매수호가",
        description="bidho1 — float(6.2). Consume as returned by LS.",
    )
    cvolume: int = Field(
        default=0,
        title="체결량",
        description="cvolume — long(12). Consume as returned by LS.",
    )
    delt: float = Field(
        default=0.0,
        title="델타",
        description="delt — float(6.4). Consume as returned by LS.",
    )
    gama: float = Field(
        default=0.0,
        title="감마",
        description="gama — float(6.4). Consume as returned by LS.",
    )
    vega: float = Field(
        default=0.0,
        title="베가",
        description="vega — float(6.4). Consume as returned by LS.",
    )
    ceta: float = Field(
        default=0.0,
        title="쎄타",
        description="ceta — float(6.4). Consume as returned by LS.",
    )
    rhox: float = Field(
        default=0.0,
        title="로우",
        description="rhox — float(6.4). Consume as returned by LS.",
    )
    theoryprice: float = Field(
        default=0.0,
        title="이론가",
        description="theoryprice — float(6.2). Consume as returned by LS.",
    )
    impv: float = Field(
        default=0.0,
        title="내재가치",
        description="impv — float(6.2). Consume as returned by LS.",
    )
    timevl: float = Field(
        default=0.0,
        title="시간가치",
        description="timevl — float(6.2). Consume as returned by LS.",
    )
    jvolume: int = Field(
        default=0,
        title="잔고수량",
        description="jvolume — long(12). Consume as returned by LS.",
    )
    parpl: int = Field(
        default=0,
        title="평가손익",
        description="parpl — long(12). Consume as returned by LS.",
    )
    jngo: int = Field(
        default=0,
        title="청산가능수량",
        description="jngo — long(6). Consume as returned by LS.",
    )
    offerrem1: int = Field(
        default=0,
        title="매도잔량",
        description="offerrem1 — long(12). Consume as returned by LS.",
    )
    bidrem1: int = Field(
        default=0,
        title="매수잔량",
        description="bidrem1 — long(12). Consume as returned by LS.",
    )
    open: float = Field(
        default=0.0,
        title="시가",
        description="open — float(6.2). Consume as returned by LS.",
    )
    high: float = Field(
        default=0.0,
        title="고가",
        description="high — float(6.2). Consume as returned by LS.",
    )
    low: float = Field(
        default=0.0,
        title="저가",
        description="low — float(6.2). Consume as returned by LS.",
    )
    atmgubun: str = Field(
        default="",
        title="ATM구분",
        description="atmgubun — char(1). Consume as returned by LS.",
    )
    jisuconv: float = Field(
        default=0.0,
        title="지수환산",
        description="jisuconv — float(6.2). Consume as returned by LS.",
    )
    value: float = Field(
        default=0.0,
        title="거래대금",
        description="value — float(12). Consume as returned by LS.",
    )

class T2301OutBlock2(BaseModel):
    """t2301OutBlock2 — output block (occurs — list of rows). 출력2"""

    actprice: float = Field(
        default=0.0,
        title="행사가",
        description="actprice — float(6.2). Consume as returned by LS.",
    )
    optcode: str = Field(
        default="",
        title="풋옵션코드",
        description="optcode — char(8). Consume as returned by LS.",
    )
    price: float = Field(
        default=0.0,
        title="현재가",
        description="price — float(6.2). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: float = Field(
        default=0.0,
        title="전일대비",
        description="change — float(6.2). Consume as returned by LS.",
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
    iv: float = Field(
        default=0.0,
        title="IV",
        description="iv — float(6.2). Consume as returned by LS.",
    )
    mgjv: int = Field(
        default=0,
        title="미결제약정",
        description="mgjv — long(12). Consume as returned by LS.",
    )
    mgjvupdn: int = Field(
        default=0,
        title="미결제약정증감",
        description="mgjvupdn — long(12). Consume as returned by LS.",
    )
    offerho1: float = Field(
        default=0.0,
        title="매도호가",
        description="offerho1 — float(6.2). Consume as returned by LS.",
    )
    bidho1: float = Field(
        default=0.0,
        title="매수호가",
        description="bidho1 — float(6.2). Consume as returned by LS.",
    )
    cvolume: int = Field(
        default=0,
        title="체결량",
        description="cvolume — long(12). Consume as returned by LS.",
    )
    delt: float = Field(
        default=0.0,
        title="델타",
        description="delt — float(6.4). Consume as returned by LS.",
    )
    gama: float = Field(
        default=0.0,
        title="감마",
        description="gama — float(6.4). Consume as returned by LS.",
    )
    vega: float = Field(
        default=0.0,
        title="베가",
        description="vega — float(6.4). Consume as returned by LS.",
    )
    ceta: float = Field(
        default=0.0,
        title="쎄타",
        description="ceta — float(6.4). Consume as returned by LS.",
    )
    rhox: float = Field(
        default=0.0,
        title="로우",
        description="rhox — float(6.4). Consume as returned by LS.",
    )
    theoryprice: float = Field(
        default=0.0,
        title="이론가",
        description="theoryprice — float(6.2). Consume as returned by LS.",
    )
    impv: float = Field(
        default=0.0,
        title="내재가치",
        description="impv — float(6.2). Consume as returned by LS.",
    )
    timevl: float = Field(
        default=0.0,
        title="시간가치",
        description="timevl — float(6.2). Consume as returned by LS.",
    )
    jvolume: int = Field(
        default=0,
        title="잔고수량",
        description="jvolume — long(12). Consume as returned by LS.",
    )
    parpl: int = Field(
        default=0,
        title="평가손익",
        description="parpl — long(12). Consume as returned by LS.",
    )
    jngo: int = Field(
        default=0,
        title="청산가능수량",
        description="jngo — long(6). Consume as returned by LS.",
    )
    offerrem1: int = Field(
        default=0,
        title="매도잔량",
        description="offerrem1 — long(12). Consume as returned by LS.",
    )
    bidrem1: int = Field(
        default=0,
        title="매수잔량",
        description="bidrem1 — long(12). Consume as returned by LS.",
    )
    open: float = Field(
        default=0.0,
        title="시가",
        description="open — float(6.2). Consume as returned by LS.",
    )
    high: float = Field(
        default=0.0,
        title="고가",
        description="high — float(6.2). Consume as returned by LS.",
    )
    low: float = Field(
        default=0.0,
        title="저가",
        description="low — float(6.2). Consume as returned by LS.",
    )
    atmgubun: str = Field(
        default="",
        title="ATM구분",
        description="atmgubun — char(1). Consume as returned by LS.",
    )
    jisuconv: float = Field(
        default=0.0,
        title="지수환산",
        description="jisuconv — float(6.2). Consume as returned by LS.",
    )
    value: float = Field(
        default=0.0,
        title="거래대금",
        description="value — float(12). Consume as returned by LS.",
    )

class T2301Request(BaseModel):
    """Request envelope for t2301."""

    header: T2301RequestHeader = T2301RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t2301",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t2301",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T2301Response(BaseModel):
    """Response envelope for t2301."""

    header: Optional[T2301ResponseHeader] = None
    block: Optional[T2301OutBlock] = None
    block1: List[T2301OutBlock1] = []
    block2: List[T2301OutBlock2] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T2301RequestHeader",
    "T2301ResponseHeader",
    "T2301InBlock",
    "T2301OutBlock",
    "T2301OutBlock1",
    "T2301OutBlock2",
    "T2301Request",
    "T2301Response",
]