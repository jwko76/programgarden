"""Pydantic models for LS Securities OpenAPI t1950 (ELW현재가(시세)조회(t1950)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1950RequestHeader(BlockRequestHeader):
    pass


class T1950ResponseHeader(BlockResponseHeader):
    pass

class T1950InBlock(BaseModel):
    """t1950InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="ELW단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1950OutBlock(BaseModel):
    """t1950OutBlock — output block. 출력"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(40). Consume as returned by LS.",
    )
    chetime: str = Field(
        default="",
        title="체결시간",
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
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    cvolume: int = Field(
        default=0,
        title="체결량",
        description="cvolume — long(10). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="누적거래량",
        description="volume — float(12). Consume as returned by LS.",
    )
    recprice: int = Field(
        default=0,
        title="기준가",
        description="recprice — long(8). Consume as returned by LS.",
    )
    avg: int = Field(
        default=0,
        title="가중평균",
        description="avg — long(8). Consume as returned by LS.",
    )
    jnilvolume: float = Field(
        default=0.0,
        title="전일거래량",
        description="jnilvolume — float(12). Consume as returned by LS.",
    )
    jvolume: float = Field(
        default=0.0,
        title="전일동시간거래량",
        description="jvolume — float(12). Consume as returned by LS.",
    )
    jnilclose: int = Field(
        default=0,
        title="전일종가",
        description="jnilclose — long(8). Consume as returned by LS.",
    )
    volumechg: float = Field(
        default=0.0,
        title="거래량차",
        description="volumechg — float(12). Consume as returned by LS.",
    )
    volumediff: float = Field(
        default=0.0,
        title="거래량차등락율",
        description="volumediff — float(6.2). Consume as returned by LS.",
    )
    open: int = Field(
        default=0,
        title="시가",
        description="open — long(8). Consume as returned by LS.",
    )
    odiff: float = Field(
        default=0.0,
        title="시가등락율",
        description="odiff — float(6.2). Consume as returned by LS.",
    )
    opentime: str = Field(
        default="",
        title="시가시간",
        description="opentime — char(6). Consume as returned by LS.",
    )
    high: int = Field(
        default=0,
        title="고가",
        description="high — long(8). Consume as returned by LS.",
    )
    hdiff: float = Field(
        default=0.0,
        title="고가등락율",
        description="hdiff — float(6.2). Consume as returned by LS.",
    )
    hightime: str = Field(
        default="",
        title="고가시간",
        description="hightime — char(6). Consume as returned by LS.",
    )
    low: int = Field(
        default=0,
        title="저가",
        description="low — long(8). Consume as returned by LS.",
    )
    ldiff: float = Field(
        default=0.0,
        title="저가등락율",
        description="ldiff — float(6.2). Consume as returned by LS.",
    )
    lowtime: str = Field(
        default="",
        title="저가시간",
        description="lowtime — char(6). Consume as returned by LS.",
    )
    high52w: int = Field(
        default=0,
        title="52최고가",
        description="high52w — long(8). Consume as returned by LS.",
    )
    high52wdiff: float = Field(
        default=0.0,
        title="52최고가등락율",
        description="high52wdiff — float(6.2). Consume as returned by LS.",
    )
    high52wdate: str = Field(
        default="",
        title="52최고가일",
        description="high52wdate — char(8). Consume as returned by LS.",
    )
    low52w: int = Field(
        default=0,
        title="52최저가",
        description="low52w — long(8). Consume as returned by LS.",
    )
    low52wdiff: float = Field(
        default=0.0,
        title="52최저가등락율",
        description="low52wdiff — float(6.2). Consume as returned by LS.",
    )
    low52wdate: str = Field(
        default="",
        title="52최저가일",
        description="low52wdate — char(8). Consume as returned by LS.",
    )
    exhratio: float = Field(
        default=0.0,
        title="소진율",
        description="exhratio — float(6.2). Consume as returned by LS.",
    )
    listing: float = Field(
        default=0.0,
        title="상장주식수(천)",
        description="listing — float(12). Consume as returned by LS.",
    )
    memedan: str = Field(
        default="",
        title="수량단위",
        description="memedan — char(5). Consume as returned by LS.",
    )
    vol: float = Field(
        default=0.0,
        title="회전율",
        description="vol — float(6.2). Consume as returned by LS.",
    )
    parity: float = Field(
        default=0.0,
        title="패리티",
        description="parity — float(8.2). Consume as returned by LS.",
    )
    berate: float = Field(
        default=0.0,
        title="손익분기",
        description="berate — float(8.2). Consume as returned by LS.",
    )
    gearing: float = Field(
        default=0.0,
        title="기어링",
        description="gearing — float(8.2). Consume as returned by LS.",
    )
    elwexec: float = Field(
        default=0.0,
        title="행사가",
        description="elwexec — float(8.2). Consume as returned by LS.",
    )
    issueprice: int = Field(
        default=0,
        title="발행가",
        description="issueprice — long(8). Consume as returned by LS.",
    )
    convrate: float = Field(
        default=0.0,
        title="전환비율",
        description="convrate — float(12.4). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="최종거래일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    capt: float = Field(
        default=0.0,
        title="자본지지",
        description="capt — float(8.2). Consume as returned by LS.",
    )
    egearing: float = Field(
        default=0.0,
        title="e.기어링",
        description="egearing — float(8.2). Consume as returned by LS.",
    )
    premium: float = Field(
        default=0.0,
        title="프리미엄",
        description="premium — float(8.2). Consume as returned by LS.",
    )
    spread: float = Field(
        default=0.0,
        title="스프레드",
        description="spread — float(6.2). Consume as returned by LS.",
    )
    espread: float = Field(
        default=0.0,
        title="최대스프레드",
        description="espread — float(6.2). Consume as returned by LS.",
    )
    theoryprice: float = Field(
        default=0.0,
        title="이론가",
        description="theoryprice — float(10.2). Consume as returned by LS.",
    )
    impv: float = Field(
        default=0.0,
        title="내재변동성",
        description="impv — float(6.2). Consume as returned by LS.",
    )
    moneyness: str = Field(
        default="",
        title="상태",
        description="moneyness — char(1). Consume as returned by LS.",
    )
    delt: float = Field(
        default=0.0,
        title="델타",
        description="delt — float(8.6). Consume as returned by LS.",
    )
    gama: float = Field(
        default=0.0,
        title="감마",
        description="gama — float(8.6). Consume as returned by LS.",
    )
    vega: float = Field(
        default=0.0,
        title="베가",
        description="vega — float(13.6). Consume as returned by LS.",
    )
    ceta: float = Field(
        default=0.0,
        title="쎄타",
        description="ceta — float(13.6). Consume as returned by LS.",
    )
    rhox: float = Field(
        default=0.0,
        title="로",
        description="rhox — float(13.6). Consume as returned by LS.",
    )
    bjandatecnt: int = Field(
        default=0,
        title="잔존일수",
        description="bjandatecnt — long(4). Consume as returned by LS.",
    )
    mmsdate: str = Field(
        default="",
        title="행사개시일",
        description="mmsdate — char(8). Consume as returned by LS.",
    )
    mmedate: str = Field(
        default="",
        title="행사종료일",
        description="mmedate — char(8). Consume as returned by LS.",
    )
    payday: str = Field(
        default="",
        title="지급일",
        description="payday — char(8). Consume as returned by LS.",
    )
    listdate: str = Field(
        default="",
        title="발행일",
        description="listdate — char(8). Consume as returned by LS.",
    )
    lpmem: str = Field(
        default="",
        title="LP회원사",
        description="lpmem — char(20). Consume as returned by LS.",
    )
    lp_holdvol: float = Field(
        default=0.0,
        title="LP보유수량",
        description="lp_holdvol — float(12). Consume as returned by LS.",
    )
    bcode: str = Field(
        default="",
        title="기초자산코드",
        description="bcode — char(6). Consume as returned by LS.",
    )
    bgubun: str = Field(
        default="",
        title="기초자산구분",
        description="bgubun — char(1). Consume as returned by LS.",
    )
    bprice: int = Field(
        default=0,
        title="기초자산현재가",
        description="bprice — long(8). Consume as returned by LS.",
    )
    bsign: str = Field(
        default="",
        title="기초자산전일비구분",
        description="bsign — char(1). Consume as returned by LS.",
    )
    bchange: int = Field(
        default=0,
        title="기초자산전일비",
        description="bchange — long(8). Consume as returned by LS.",
    )
    bdiff: float = Field(
        default=0.0,
        title="기초자산등락율",
        description="bdiff — float(6.2). Consume as returned by LS.",
    )
    bvolume: float = Field(
        default=0.0,
        title="기초자산거래량",
        description="bvolume — float(12). Consume as returned by LS.",
    )
    info1: str = Field(
        default="",
        title="락구분",
        description="info1 — char(10). Consume as returned by LS.",
    )
    info2: str = Field(
        default="",
        title="관리/급등구분",
        description="info2 — char(10). Consume as returned by LS.",
    )
    info3: str = Field(
        default="",
        title="정지/연장구분",
        description="info3 — char(10). Consume as returned by LS.",
    )
    info4: str = Field(
        default="",
        title="투자/불성실구분",
        description="info4 — char(12). Consume as returned by LS.",
    )
    janginfo: str = Field(
        default="",
        title="장구분",
        description="janginfo — char(10). Consume as returned by LS.",
    )
    basketgb: str = Field(
        default="",
        title="바스켓구분",
        description="basketgb — char(1). Consume as returned by LS.",
    )
    basketcnt: int = Field(
        default=0,
        title="바스켓갯수",
        description="basketcnt — long(3). Consume as returned by LS.",
    )
    elwtype: str = Field(
        default="",
        title="ELW권리행사방식",
        description="elwtype — char(2). Consume as returned by LS.",
    )
    settletype: str = Field(
        default="",
        title="ELW결제방법",
        description="settletype — char(2). Consume as returned by LS.",
    )
    lpord: str = Field(
        default="",
        title="LP사주문가능여부",
        description="lpord — char(2). Consume as returned by LS.",
    )
    elwdetail: str = Field(
        default="",
        title="권리내용",
        description="elwdetail — char(100). Consume as returned by LS.",
    )
    valuation: str = Field(
        default="",
        title="만기평가가격방식",
        description="valuation — char(100). Consume as returned by LS.",
    )
    value: float = Field(
        default=0.0,
        title="누적거래대금",
        description="value — double(12.0). Consume as returned by LS.",
    )

class T1950OutBlock1(BaseModel):
    """t1950OutBlock1 — output block (occurs — list of rows). 출력1"""

    bskcode: str = Field(
        default="",
        title="기초자산코드",
        description="bskcode — char(6). Consume as returned by LS.",
    )
    bskbno: int = Field(
        default=0,
        title="기초자산비율",
        description="bskbno — long(3). Consume as returned by LS.",
    )
    bskprice: int = Field(
        default=0,
        title="기초자산현재가",
        description="bskprice — long(8). Consume as returned by LS.",
    )
    bsksign: str = Field(
        default="",
        title="기초자산전일비구분",
        description="bsksign — char(1). Consume as returned by LS.",
    )
    bskchange: int = Field(
        default=0,
        title="기초자산전일비",
        description="bskchange — long(8). Consume as returned by LS.",
    )
    bskdiff: float = Field(
        default=0.0,
        title="기초자산등락율",
        description="bskdiff — float(6.2). Consume as returned by LS.",
    )
    bskvolume: float = Field(
        default=0.0,
        title="기초자산거래량",
        description="bskvolume — float(12). Consume as returned by LS.",
    )
    bskjnilclose: int = Field(
        default=0,
        title="기초자산전일종가",
        description="bskjnilclose — long(8). Consume as returned by LS.",
    )

class T1950Request(BaseModel):
    """Request envelope for t1950."""

    header: T1950RequestHeader = T1950RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1950",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1950",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1950Response(BaseModel):
    """Response envelope for t1950."""

    header: Optional[T1950ResponseHeader] = None
    block: Optional[T1950OutBlock] = None
    block1: List[T1950OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1950RequestHeader",
    "T1950ResponseHeader",
    "T1950InBlock",
    "T1950OutBlock",
    "T1950OutBlock1",
    "T1950Request",
    "T1950Response",
]