"""Pydantic models for LS Securities OpenAPI t1969 (ELW지표검색(t1969)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1969RequestHeader(BlockRequestHeader):
    pass


class T1969ResponseHeader(BlockResponseHeader):
    pass

class T1969InBlock(BaseModel):
    """t1969InBlock — input block. 입력"""

    chkitem: str = Field(
        ...,
        title="기초자산chk구분",
        description="chkitem — char(1). Consume as returned by LS.",
    )
    cbitem: str = Field(
        ...,
        title="기초자산코드",
        description="cbitem — char(12). Consume as returned by LS.",
    )
    chkissuer: str = Field(
        ...,
        title="발행사chk구분",
        description="chkissuer — char(1). Consume as returned by LS.",
    )
    cbissuer: str = Field(
        ...,
        title="발행사",
        description="cbissuer — char(12). Consume as returned by LS.",
    )
    chkcallput: str = Field(
        ...,
        title="권리chk구분",
        description="chkcallput — char(1). Consume as returned by LS.",
    )
    cbcallput: str = Field(
        ...,
        title="권리(call:01.put:02)",
        description="cbcallput — char(2). Consume as returned by LS.",
    )
    chkexec: str = Field(
        ...,
        title="행사가chk구분",
        description="chkexec — char(1). Consume as returned by LS.",
    )
    cbexec: str = Field(
        ...,
        title="행사가(>=:1.<=:2)",
        description="cbexec — char(1). Consume as returned by LS.",
    )
    chktype: str = Field(
        ...,
        title="행사방식chk구분",
        description="chktype — char(1). Consume as returned by LS.",
    )
    cbtype: str = Field(
        ...,
        title="행사방식",
        description="cbtype — char(2). Consume as returned by LS.",
    )
    chksettle: str = Field(
        ...,
        title="결제방법chk구분",
        description="chksettle — char(1). Consume as returned by LS.",
    )
    cbsettle: str = Field(
        ...,
        title="결제방법",
        description="cbsettle — char(2). Consume as returned by LS.",
    )
    chklast: str = Field(
        ...,
        title="만기chk구분",
        description="chklast — char(1). Consume as returned by LS.",
    )
    cblast: str = Field(
        ...,
        title="만기월별",
        description="cblast — char(6). Consume as returned by LS.",
    )
    chkelwexec: str = Field(
        ...,
        title="행사가격chk구분",
        description="chkelwexec — char(1). Consume as returned by LS.",
    )
    elwexecs: float = Field(
        ...,
        title="행사가이상",
        description="elwexecs — float(10.2). Consume as returned by LS.",
    )
    elwexece: float = Field(
        ...,
        title="행사가이하",
        description="elwexece — float(10.2). Consume as returned by LS.",
    )
    chkvolume: str = Field(
        ...,
        title="거래량chk구분",
        description="chkvolume — char(1). Consume as returned by LS.",
    )
    volumes: float = Field(
        ...,
        title="거래량이상",
        description="volumes — float(12). Consume as returned by LS.",
    )
    volumee: float = Field(
        ...,
        title="거래량이하",
        description="volumee — float(12). Consume as returned by LS.",
    )
    chkrate: str = Field(
        ...,
        title="등락율chk구분",
        description="chkrate — char(1). Consume as returned by LS.",
    )
    rates: float = Field(
        ...,
        title="등락율이상",
        description="rates — float(6.2). Consume as returned by LS.",
    )
    ratee: float = Field(
        ...,
        title="등락율이하",
        description="ratee — float(6.2). Consume as returned by LS.",
    )
    chkpremium: str = Field(
        ...,
        title="프리미엄chk구분",
        description="chkpremium — char(1). Consume as returned by LS.",
    )
    premiums: float = Field(
        ...,
        title="프리미엄이상",
        description="premiums — float(6.2). Consume as returned by LS.",
    )
    premiume: float = Field(
        ...,
        title="프리미엄이하",
        description="premiume — float(6.2). Consume as returned by LS.",
    )
    chkparity: str = Field(
        ...,
        title="패리티chk구분",
        description="chkparity — char(1). Consume as returned by LS.",
    )
    paritys: float = Field(
        ...,
        title="패리티이상",
        description="paritys — float(6.2). Consume as returned by LS.",
    )
    paritye: float = Field(
        ...,
        title="패리티이하",
        description="paritye — float(6.2). Consume as returned by LS.",
    )
    chkberate: str = Field(
        ...,
        title="손익분기chk구분",
        description="chkberate — char(1). Consume as returned by LS.",
    )
    berates: float = Field(
        ...,
        title="손익분기이상",
        description="berates — float(6.2). Consume as returned by LS.",
    )
    beratee: float = Field(
        ...,
        title="손익분기이하",
        description="beratee — float(6.2). Consume as returned by LS.",
    )
    chkcapt: str = Field(
        ...,
        title="자본지지chk구분",
        description="chkcapt — char(1). Consume as returned by LS.",
    )
    capts: float = Field(
        ...,
        title="자본지지이상",
        description="capts — float(6.2). Consume as returned by LS.",
    )
    capte: float = Field(
        ...,
        title="자본지지이하",
        description="capte — float(6.2). Consume as returned by LS.",
    )
    chkegearing: str = Field(
        ...,
        title="e.기어링chk구분",
        description="chkegearing — char(1). Consume as returned by LS.",
    )
    egearings: float = Field(
        ...,
        title="e.기어링이상",
        description="egearings — float(6.2). Consume as returned by LS.",
    )
    egearinge: float = Field(
        ...,
        title="e.기어링이하",
        description="egearinge — float(6.2). Consume as returned by LS.",
    )
    chkgearing: str = Field(
        ...,
        title="기어링chk구분",
        description="chkgearing — char(1). Consume as returned by LS.",
    )
    gearings: float = Field(
        ...,
        title="기어링이상",
        description="gearings — float(6.2). Consume as returned by LS.",
    )
    gearinge: float = Field(
        ...,
        title="기어링이하",
        description="gearinge — float(6.2). Consume as returned by LS.",
    )
    chkdelta: str = Field(
        ...,
        title="델타chk구분",
        description="chkdelta — char(1). Consume as returned by LS.",
    )
    deltas: float = Field(
        ...,
        title="델타이상",
        description="deltas — float(10.6). Consume as returned by LS.",
    )
    deltae: float = Field(
        ...,
        title="델타이하",
        description="deltae — float(10.6). Consume as returned by LS.",
    )
    chktheta: str = Field(
        ...,
        title="쎄타chk구분",
        description="chktheta — char(1). Consume as returned by LS.",
    )
    thetas: float = Field(
        ...,
        title="쎄타이상",
        description="thetas — float(10.6). Consume as returned by LS.",
    )
    thetae: float = Field(
        ...,
        title="쎄타이하",
        description="thetae — float(10.6). Consume as returned by LS.",
    )
    chkduedate: str = Field(
        ...,
        title="최종거래일chk구분",
        description="chkduedate — char(1). Consume as returned by LS.",
    )
    duedates: str = Field(
        ...,
        title="최종거래일이상",
        description="duedates — char(8). Consume as returned by LS.",
    )
    duedatee: str = Field(
        ...,
        title="최종거래일이하",
        description="duedatee — char(8). Consume as returned by LS.",
    )
    onetickgubun: str = Field(
        ...,
        title="LP갭1틱",
        description="onetickgubun — char(1). Consume as returned by LS.",
    )
    lp_liquidity: str = Field(
        ...,
        title="LP유동성공급",
        description="lp_liquidity — char(1). Consume as returned by LS.",
    )
    chklp_code: str = Field(
        ...,
        title="LPchk구분",
        description="chklp_code — char(1). Consume as returned by LS.",
    )
    lp_code: str = Field(
        ...,
        title="LP회원사코드",
        description="lp_code — char(3). Consume as returned by LS.",
    )
    chkkoba: str = Field(
        ...,
        title="조기종료chk구분",
        description="chkkoba — char(1). Consume as returned by LS.",
    )
    cbkoba: str = Field(
        ...,
        title="조기종료(0:전체1:KOBA2:KOBA제외)",
        description="cbkoba — char(1). Consume as returned by LS.",
    )

class T1969OutBlock(BaseModel):
    """t1969OutBlock — output block. 출력"""

    cnt: int = Field(
        default=0,
        title="종목갯수",
        description="cnt — long(4). Consume as returned by LS.",
    )

class T1969OutBlock1(BaseModel):
    """t1969OutBlock1 — output block (occurs — list of rows). 출력1"""

    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(40). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    issuernmk: str = Field(
        default="",
        title="발행사",
        description="issuernmk — char(40). Consume as returned by LS.",
    )
    itemcode: str = Field(
        default="",
        title="기초자산코드",
        description="itemcode — char(12). Consume as returned by LS.",
    )
    cpgubun: str = Field(
        default="",
        title="콜/풋구분",
        description="cpgubun — char(2). Consume as returned by LS.",
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
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — float(12). Consume as returned by LS.",
    )
    jnilvolume: float = Field(
        default=0.0,
        title="전일거래량",
        description="jnilvolume — float(12). Consume as returned by LS.",
    )
    elwexec: float = Field(
        default=0.0,
        title="행사가",
        description="elwexec — float(10.2). Consume as returned by LS.",
    )
    item: str = Field(
        default="",
        title="기초자산명",
        description="item — char(20). Consume as returned by LS.",
    )
    bprice: float = Field(
        default=0.0,
        title="기초자산가",
        description="bprice — float(10.2). Consume as returned by LS.",
    )
    bsign: str = Field(
        default="",
        title="기초전일대비구분",
        description="bsign — char(1). Consume as returned by LS.",
    )
    bchange: float = Field(
        default=0.0,
        title="기초전일대비",
        description="bchange — float(10.2). Consume as returned by LS.",
    )
    bdiff: float = Field(
        default=0.0,
        title="기초등락율",
        description="bdiff — float(6.2). Consume as returned by LS.",
    )
    premium: float = Field(
        default=0.0,
        title="프리미엄",
        description="premium — float(6.2). Consume as returned by LS.",
    )
    parity: float = Field(
        default=0.0,
        title="패리티",
        description="parity — float(6.2). Consume as returned by LS.",
    )
    berate: float = Field(
        default=0.0,
        title="손익분기",
        description="berate — float(6.2). Consume as returned by LS.",
    )
    capt: float = Field(
        default=0.0,
        title="자본지지",
        description="capt — float(6.2). Consume as returned by LS.",
    )
    egearing: float = Field(
        default=0.0,
        title="e.기어링",
        description="egearing — float(6.2). Consume as returned by LS.",
    )
    gearing: float = Field(
        default=0.0,
        title="기어링",
        description="gearing — float(6.2). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="최종거래일",
        description="lastdate — char(8). Consume as returned by LS.",
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
    lpname: str = Field(
        default="",
        title="LP회원사",
        description="lpname — char(40). Consume as returned by LS.",
    )
    lphold: float = Field(
        default=0.0,
        title="LP보유율",
        description="lphold — float(6.2). Consume as returned by LS.",
    )
    bjandatecnt: int = Field(
        default=0,
        title="잔존일수",
        description="bjandatecnt — long(4). Consume as returned by LS.",
    )
    convrate: float = Field(
        default=0.0,
        title="전환비율",
        description="convrate — float(8.4). Consume as returned by LS.",
    )
    tickvalue: float = Field(
        default=0.0,
        title="1틱환산",
        description="tickvalue — float(10.2). Consume as returned by LS.",
    )
    kasis: float = Field(
        default=0.0,
        title="괴리율",
        description="kasis — float(6.2). Consume as returned by LS.",
    )

class T1969Request(BaseModel):
    """Request envelope for t1969."""

    header: T1969RequestHeader = T1969RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1969",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1969",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1969Response(BaseModel):
    """Response envelope for t1969."""

    header: Optional[T1969ResponseHeader] = None
    block: Optional[T1969OutBlock] = None
    block1: List[T1969OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1969RequestHeader",
    "T1969ResponseHeader",
    "T1969InBlock",
    "T1969OutBlock",
    "T1969OutBlock1",
    "T1969Request",
    "T1969Response",
]