"""Pydantic models for LS Securities OpenAPI t1906 (ETFLP호가(t1906)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1906RequestHeader(BlockRequestHeader):
    pass


class T1906ResponseHeader(BlockResponseHeader):
    pass

class T1906InBlock(BaseModel):
    """t1906InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1906OutBlock(BaseModel):
    """t1906OutBlock — output block. 출력"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(20). Consume as returned by LS.",
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
        title="누적거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    lp_offerrem1: int = Field(
        default=0,
        title="LP매도호가수량1",
        description="lp_offerrem1 — long(12). Consume as returned by LS.",
    )
    lp_bidrem1: int = Field(
        default=0,
        title="LP매수호가수량1",
        description="lp_bidrem1 — long(12). Consume as returned by LS.",
    )
    lp_offerrem2: int = Field(
        default=0,
        title="LP매도호가수량2",
        description="lp_offerrem2 — long(12). Consume as returned by LS.",
    )
    lp_bidrem2: int = Field(
        default=0,
        title="LP매수호가수량2",
        description="lp_bidrem2 — long(12). Consume as returned by LS.",
    )
    lp_offerrem3: int = Field(
        default=0,
        title="LP매도호가수량3",
        description="lp_offerrem3 — long(12). Consume as returned by LS.",
    )
    lp_bidrem3: int = Field(
        default=0,
        title="LP매수호가수량3",
        description="lp_bidrem3 — long(12). Consume as returned by LS.",
    )
    lp_offerrem4: int = Field(
        default=0,
        title="LP매도호가수량4",
        description="lp_offerrem4 — long(12). Consume as returned by LS.",
    )
    lp_bidrem4: int = Field(
        default=0,
        title="LP매수호가수량4",
        description="lp_bidrem4 — long(12). Consume as returned by LS.",
    )
    lp_offerrem5: int = Field(
        default=0,
        title="LP매도호가수량5",
        description="lp_offerrem5 — long(12). Consume as returned by LS.",
    )
    lp_bidrem5: int = Field(
        default=0,
        title="LP매수호가수량5",
        description="lp_bidrem5 — long(12). Consume as returned by LS.",
    )
    lp_offerrem6: int = Field(
        default=0,
        title="LP매도호가수량6",
        description="lp_offerrem6 — long(12). Consume as returned by LS.",
    )
    lp_bidrem6: int = Field(
        default=0,
        title="LP매수호가수량6",
        description="lp_bidrem6 — long(12). Consume as returned by LS.",
    )
    lp_offerrem7: int = Field(
        default=0,
        title="LP매도호가수량7",
        description="lp_offerrem7 — long(12). Consume as returned by LS.",
    )
    lp_bidrem7: int = Field(
        default=0,
        title="LP매수호가수량7",
        description="lp_bidrem7 — long(12). Consume as returned by LS.",
    )
    lp_offerrem8: int = Field(
        default=0,
        title="LP매도호가수량8",
        description="lp_offerrem8 — long(12). Consume as returned by LS.",
    )
    lp_bidrem8: int = Field(
        default=0,
        title="LP매수호가수량8",
        description="lp_bidrem8 — long(12). Consume as returned by LS.",
    )
    lp_offerrem9: int = Field(
        default=0,
        title="LP매도호가수량9",
        description="lp_offerrem9 — long(12). Consume as returned by LS.",
    )
    lp_bidrem9: int = Field(
        default=0,
        title="LP매수호가수량9",
        description="lp_bidrem9 — long(12). Consume as returned by LS.",
    )
    lp_offerrem10: int = Field(
        default=0,
        title="LP매도호가수량10",
        description="lp_offerrem10 — long(12). Consume as returned by LS.",
    )
    lp_bidrem10: int = Field(
        default=0,
        title="LP매수호가수량10",
        description="lp_bidrem10 — long(12). Consume as returned by LS.",
    )
    jnilclose: int = Field(
        default=0,
        title="전일종가",
        description="jnilclose — long(8). Consume as returned by LS.",
    )
    offerho1: int = Field(
        default=0,
        title="매도호가1",
        description="offerho1 — long(8). Consume as returned by LS.",
    )
    bidho1: int = Field(
        default=0,
        title="매수호가1",
        description="bidho1 — long(8). Consume as returned by LS.",
    )
    offerrem1: int = Field(
        default=0,
        title="매도호가수량1",
        description="offerrem1 — long(12). Consume as returned by LS.",
    )
    bidrem1: int = Field(
        default=0,
        title="매수호가수량1",
        description="bidrem1 — long(12). Consume as returned by LS.",
    )
    preoffercha1: int = Field(
        default=0,
        title="직전매도대비수량1",
        description="preoffercha1 — long(12). Consume as returned by LS.",
    )
    prebidcha1: int = Field(
        default=0,
        title="직전매수대비수량1",
        description="prebidcha1 — long(12). Consume as returned by LS.",
    )
    offerho2: int = Field(
        default=0,
        title="매도호가2",
        description="offerho2 — long(8). Consume as returned by LS.",
    )
    bidho2: int = Field(
        default=0,
        title="매수호가2",
        description="bidho2 — long(8). Consume as returned by LS.",
    )
    offerrem2: int = Field(
        default=0,
        title="매도호가수량2",
        description="offerrem2 — long(12). Consume as returned by LS.",
    )
    bidrem2: int = Field(
        default=0,
        title="매수호가수량2",
        description="bidrem2 — long(12). Consume as returned by LS.",
    )
    preoffercha2: int = Field(
        default=0,
        title="직전매도대비수량2",
        description="preoffercha2 — long(12). Consume as returned by LS.",
    )
    prebidcha2: int = Field(
        default=0,
        title="직전매수대비수량2",
        description="prebidcha2 — long(12). Consume as returned by LS.",
    )
    offerho3: int = Field(
        default=0,
        title="매도호가3",
        description="offerho3 — long(8). Consume as returned by LS.",
    )
    bidho3: int = Field(
        default=0,
        title="매수호가3",
        description="bidho3 — long(8). Consume as returned by LS.",
    )
    offerrem3: int = Field(
        default=0,
        title="매도호가수량3",
        description="offerrem3 — long(12). Consume as returned by LS.",
    )
    bidrem3: int = Field(
        default=0,
        title="매수호가수량3",
        description="bidrem3 — long(12). Consume as returned by LS.",
    )
    preoffercha3: int = Field(
        default=0,
        title="직전매도대비수량3",
        description="preoffercha3 — long(12). Consume as returned by LS.",
    )
    prebidcha3: int = Field(
        default=0,
        title="직전매수대비수량3",
        description="prebidcha3 — long(12). Consume as returned by LS.",
    )
    offerho4: int = Field(
        default=0,
        title="매도호가4",
        description="offerho4 — long(8). Consume as returned by LS.",
    )
    bidho4: int = Field(
        default=0,
        title="매수호가4",
        description="bidho4 — long(8). Consume as returned by LS.",
    )
    offerrem4: int = Field(
        default=0,
        title="매도호가수량4",
        description="offerrem4 — long(12). Consume as returned by LS.",
    )
    bidrem4: int = Field(
        default=0,
        title="매수호가수량4",
        description="bidrem4 — long(12). Consume as returned by LS.",
    )
    preoffercha4: int = Field(
        default=0,
        title="직전매도대비수량4",
        description="preoffercha4 — long(12). Consume as returned by LS.",
    )
    prebidcha4: int = Field(
        default=0,
        title="직전매수대비수량4",
        description="prebidcha4 — long(12). Consume as returned by LS.",
    )
    offerho5: int = Field(
        default=0,
        title="매도호가5",
        description="offerho5 — long(8). Consume as returned by LS.",
    )
    bidho5: int = Field(
        default=0,
        title="매수호가5",
        description="bidho5 — long(8). Consume as returned by LS.",
    )
    offerrem5: int = Field(
        default=0,
        title="매도호가수량5",
        description="offerrem5 — long(12). Consume as returned by LS.",
    )
    bidrem5: int = Field(
        default=0,
        title="매수호가수량5",
        description="bidrem5 — long(12). Consume as returned by LS.",
    )
    preoffercha5: int = Field(
        default=0,
        title="직전매도대비수량5",
        description="preoffercha5 — long(12). Consume as returned by LS.",
    )
    prebidcha5: int = Field(
        default=0,
        title="직전매수대비수량5",
        description="prebidcha5 — long(12). Consume as returned by LS.",
    )
    offerho6: int = Field(
        default=0,
        title="매도호가6",
        description="offerho6 — long(8). Consume as returned by LS.",
    )
    bidho6: int = Field(
        default=0,
        title="매수호가6",
        description="bidho6 — long(8). Consume as returned by LS.",
    )
    offerrem6: int = Field(
        default=0,
        title="매도호가수량6",
        description="offerrem6 — long(12). Consume as returned by LS.",
    )
    bidrem6: int = Field(
        default=0,
        title="매수호가수량6",
        description="bidrem6 — long(12). Consume as returned by LS.",
    )
    preoffercha6: int = Field(
        default=0,
        title="직전매도대비수량6",
        description="preoffercha6 — long(12). Consume as returned by LS.",
    )
    prebidcha6: int = Field(
        default=0,
        title="직전매수대비수량6",
        description="prebidcha6 — long(12). Consume as returned by LS.",
    )
    offerho7: int = Field(
        default=0,
        title="매도호가7",
        description="offerho7 — long(8). Consume as returned by LS.",
    )
    bidho7: int = Field(
        default=0,
        title="매수호가7",
        description="bidho7 — long(8). Consume as returned by LS.",
    )
    offerrem7: int = Field(
        default=0,
        title="매도호가수량7",
        description="offerrem7 — long(12). Consume as returned by LS.",
    )
    bidrem7: int = Field(
        default=0,
        title="매수호가수량7",
        description="bidrem7 — long(12). Consume as returned by LS.",
    )
    preoffercha7: int = Field(
        default=0,
        title="직전매도대비수량7",
        description="preoffercha7 — long(12). Consume as returned by LS.",
    )
    prebidcha7: int = Field(
        default=0,
        title="직전매수대비수량7",
        description="prebidcha7 — long(12). Consume as returned by LS.",
    )
    offerho8: int = Field(
        default=0,
        title="매도호가8",
        description="offerho8 — long(8). Consume as returned by LS.",
    )
    bidho8: int = Field(
        default=0,
        title="매수호가8",
        description="bidho8 — long(8). Consume as returned by LS.",
    )
    offerrem8: int = Field(
        default=0,
        title="매도호가수량8",
        description="offerrem8 — long(12). Consume as returned by LS.",
    )
    bidrem8: int = Field(
        default=0,
        title="매수호가수량8",
        description="bidrem8 — long(12). Consume as returned by LS.",
    )
    preoffercha8: int = Field(
        default=0,
        title="직전매도대비수량8",
        description="preoffercha8 — long(12). Consume as returned by LS.",
    )
    prebidcha8: int = Field(
        default=0,
        title="직전매수대비수량8",
        description="prebidcha8 — long(12). Consume as returned by LS.",
    )
    offerho9: int = Field(
        default=0,
        title="매도호가9",
        description="offerho9 — long(8). Consume as returned by LS.",
    )
    bidho9: int = Field(
        default=0,
        title="매수호가9",
        description="bidho9 — long(8). Consume as returned by LS.",
    )
    offerrem9: int = Field(
        default=0,
        title="매도호가수량9",
        description="offerrem9 — long(12). Consume as returned by LS.",
    )
    bidrem9: int = Field(
        default=0,
        title="매수호가수량9",
        description="bidrem9 — long(12). Consume as returned by LS.",
    )
    preoffercha9: int = Field(
        default=0,
        title="직전매도대비수량9",
        description="preoffercha9 — long(12). Consume as returned by LS.",
    )
    prebidcha9: int = Field(
        default=0,
        title="직전매수대비수량9",
        description="prebidcha9 — long(12). Consume as returned by LS.",
    )
    offerho10: int = Field(
        default=0,
        title="매도호가10",
        description="offerho10 — long(8). Consume as returned by LS.",
    )
    bidho10: int = Field(
        default=0,
        title="매수호가10",
        description="bidho10 — long(8). Consume as returned by LS.",
    )
    offerrem10: int = Field(
        default=0,
        title="매도호가수량10",
        description="offerrem10 — long(12). Consume as returned by LS.",
    )
    bidrem10: int = Field(
        default=0,
        title="매수호가수량10",
        description="bidrem10 — long(12). Consume as returned by LS.",
    )
    preoffercha10: int = Field(
        default=0,
        title="직전매도대비수량10",
        description="preoffercha10 — long(12). Consume as returned by LS.",
    )
    prebidcha10: int = Field(
        default=0,
        title="직전매수대비수량10",
        description="prebidcha10 — long(12). Consume as returned by LS.",
    )
    offer: int = Field(
        default=0,
        title="매도호가수량합",
        description="offer — long(12). Consume as returned by LS.",
    )
    bid: int = Field(
        default=0,
        title="매수호가수량합",
        description="bid — long(12). Consume as returned by LS.",
    )
    preoffercha: int = Field(
        default=0,
        title="직전매도대비수량합",
        description="preoffercha — long(12). Consume as returned by LS.",
    )
    prebidcha: int = Field(
        default=0,
        title="직전매수대비수량합",
        description="prebidcha — long(12). Consume as returned by LS.",
    )
    hotime: str = Field(
        default="",
        title="수신시간",
        description="hotime — char(8). Consume as returned by LS.",
    )
    yeprice: int = Field(
        default=0,
        title="예상체결가격",
        description="yeprice — long(8). Consume as returned by LS.",
    )
    yevolume: int = Field(
        default=0,
        title="예상체결수량",
        description="yevolume — long(12). Consume as returned by LS.",
    )
    yesign: str = Field(
        default="",
        title="예상체결전일구분",
        description="yesign — char(1). Consume as returned by LS.",
    )
    yechange: int = Field(
        default=0,
        title="예상체결전일대비",
        description="yechange — long(8). Consume as returned by LS.",
    )
    yediff: float = Field(
        default=0.0,
        title="예상체결등락율",
        description="yediff — float(6.2). Consume as returned by LS.",
    )
    tmoffer: int = Field(
        default=0,
        title="시간외매도잔량",
        description="tmoffer — long(12). Consume as returned by LS.",
    )
    tmbid: int = Field(
        default=0,
        title="시간외매수잔량",
        description="tmbid — long(12). Consume as returned by LS.",
    )
    ho_status: str = Field(
        default="",
        title="동시구분",
        description="ho_status — char(1). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    uplmtprice: int = Field(
        default=0,
        title="상한가",
        description="uplmtprice — long(8). Consume as returned by LS.",
    )
    dnlmtprice: int = Field(
        default=0,
        title="하한가",
        description="dnlmtprice — long(8). Consume as returned by LS.",
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
    midprice: int = Field(
        default=0,
        title="중간가격",
        description="midprice — long(8). Consume as returned by LS.",
    )
    offermidsumrem: int = Field(
        default=0,
        title="매도중간가잔량합계수량",
        description="offermidsumrem — long(9). Consume as returned by LS.",
    )
    bidmidsumrem: int = Field(
        default=0,
        title="매수중간가잔량합계수량",
        description="bidmidsumrem — long(9). Consume as returned by LS.",
    )

class T1906Request(BaseModel):
    """Request envelope for t1906."""

    header: T1906RequestHeader = T1906RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1906",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1906",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1906Response(BaseModel):
    """Response envelope for t1906."""

    header: Optional[T1906ResponseHeader] = None
    block: Optional[T1906OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1906RequestHeader",
    "T1906ResponseHeader",
    "T1906InBlock",
    "T1906OutBlock",
    "T1906Request",
    "T1906Response",
]