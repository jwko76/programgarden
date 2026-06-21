"""Pydantic models for LS Securities OpenAPI t8402 (주식선물현재가조회(API용)(t8402)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8402RequestHeader(BlockRequestHeader):
    pass


class T8402ResponseHeader(BlockResponseHeader):
    pass

class T8402InBlock(BaseModel):
    """t8402InBlock — input block. 기본입력"""

    focode: str = Field(
        ...,
        title="단축코드",
        description="focode — char(8). Consume as returned by LS.",
    )

class T8402OutBlock(BaseModel):
    """t8402OutBlock — output block. 출력"""

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
    jnilclose: int = Field(
        default=0,
        title="전일종가",
        description="jnilclose — long(8). Consume as returned by LS.",
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
    stimeqrt: float = Field(
        default=0.0,
        title="거래량전일동시간비율",
        description="stimeqrt — double(6.2). Consume as returned by LS.",
    )
    value: int = Field(
        default=0,
        title="거래대금",
        description="value — long(12). Consume as returned by LS.",
    )
    mgjv: int = Field(
        default=0,
        title="미결제량",
        description="mgjv — long(8). Consume as returned by LS.",
    )
    mgjvdiff: int = Field(
        default=0,
        title="미결제증감",
        description="mgjvdiff — long(8). Consume as returned by LS.",
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
    high52w: int = Field(
        default=0,
        title="52최고가",
        description="high52w — long(8). Consume as returned by LS.",
    )
    low52w: int = Field(
        default=0,
        title="52최저가",
        description="low52w — long(8). Consume as returned by LS.",
    )
    basis: float = Field(
        default=0.0,
        title="베이시스",
        description="basis — float(6.2). Consume as returned by LS.",
    )
    recprice: int = Field(
        default=0,
        title="기준가",
        description="recprice — long(8). Consume as returned by LS.",
    )
    theoryprice: int = Field(
        default=0,
        title="이론가",
        description="theoryprice — long(8). Consume as returned by LS.",
    )
    glyl: float = Field(
        default=0.0,
        title="괴리율",
        description="glyl — float(6.3). Consume as returned by LS.",
    )
    lastmonth: str = Field(
        default="",
        title="만기일",
        description="lastmonth — char(8). Consume as returned by LS.",
    )
    jandatecnt: int = Field(
        default=0,
        title="잔여일",
        description="jandatecnt — long(8). Consume as returned by LS.",
    )
    pricejisu: float = Field(
        default=0.0,
        title="종합지수",
        description="pricejisu — float(10.2). Consume as returned by LS.",
    )
    jisusign: str = Field(
        default="",
        title="종합지수전일대비구분",
        description="jisusign — char(1). Consume as returned by LS.",
    )
    jisuchange: float = Field(
        default=0.0,
        title="종합지수전일대비",
        description="jisuchange — float(10.2). Consume as returned by LS.",
    )
    jisudiff: float = Field(
        default=0.0,
        title="종합지수등락율",
        description="jisudiff — float(6.2). Consume as returned by LS.",
    )
    kospijisu: float = Field(
        default=0.0,
        title="KOSPI200지수",
        description="kospijisu — float(10.2). Consume as returned by LS.",
    )
    kospisign: str = Field(
        default="",
        title="KOSPI200전일대비구분",
        description="kospisign — char(1). Consume as returned by LS.",
    )
    kospichange: float = Field(
        default=0.0,
        title="KOSPI200전일대비",
        description="kospichange — float(10.2). Consume as returned by LS.",
    )
    kospidiff: float = Field(
        default=0.0,
        title="KOSPI200등락율",
        description="kospidiff — float(6.2). Consume as returned by LS.",
    )
    listhprice: int = Field(
        default=0,
        title="상장최고가",
        description="listhprice — long(8). Consume as returned by LS.",
    )
    listlprice: int = Field(
        default=0,
        title="상장최저가",
        description="listlprice — long(8). Consume as returned by LS.",
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
    ceta: float = Field(
        default=0.0,
        title="세타",
        description="ceta — float(6.4). Consume as returned by LS.",
    )
    vega: float = Field(
        default=0.0,
        title="베가",
        description="vega — float(6.4). Consume as returned by LS.",
    )
    rhox: float = Field(
        default=0.0,
        title="로우",
        description="rhox — float(6.4). Consume as returned by LS.",
    )
    gmprice: int = Field(
        default=0,
        title="근월물현재가",
        description="gmprice — long(8). Consume as returned by LS.",
    )
    gmsign: str = Field(
        default="",
        title="근월물전일대비구분",
        description="gmsign — char(1). Consume as returned by LS.",
    )
    gmchange: int = Field(
        default=0,
        title="근월물전일대비",
        description="gmchange — long(8). Consume as returned by LS.",
    )
    gmdiff: float = Field(
        default=0.0,
        title="근월물등락율",
        description="gmdiff — float(6.2). Consume as returned by LS.",
    )
    theorypriceg: int = Field(
        default=0,
        title="이론가",
        description="theorypriceg — long(8). Consume as returned by LS.",
    )
    histimpv: float = Field(
        default=0.0,
        title="역사적변동성",
        description="histimpv — float(6.2). Consume as returned by LS.",
    )
    impv: float = Field(
        default=0.0,
        title="내재변동성",
        description="impv — float(6.2). Consume as returned by LS.",
    )
    sbasis: int = Field(
        default=0,
        title="시장BASIS",
        description="sbasis — long(8). Consume as returned by LS.",
    )
    ibasis: int = Field(
        default=0,
        title="이론BASIS",
        description="ibasis — long(8). Consume as returned by LS.",
    )
    gmfutcode: str = Field(
        default="",
        title="근월물종목코드",
        description="gmfutcode — char(8). Consume as returned by LS.",
    )
    actprice: int = Field(
        default=0,
        title="행사가",
        description="actprice — long(8). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="기초자산단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    basehname: str = Field(
        default="",
        title="기초자산한글명",
        description="basehname — char(20). Consume as returned by LS.",
    )
    baseprice: int = Field(
        default=0,
        title="기초자산현재가",
        description="baseprice — long(8). Consume as returned by LS.",
    )
    basesign: str = Field(
        default="",
        title="기초자산현재가대비구분",
        description="basesign — char(1). Consume as returned by LS.",
    )
    basechange: int = Field(
        default=0,
        title="기초자산현재가전일대비",
        description="basechange — long(8). Consume as returned by LS.",
    )
    basediff: float = Field(
        default=0.0,
        title="기초자산등락률",
        description="basediff — float(6.2). Consume as returned by LS.",
    )
    basevol: int = Field(
        default=0,
        title="기초자산거래량",
        description="basevol — long(12). Consume as returned by LS.",
    )
    baseprevol: int = Field(
        default=0,
        title="기초자산전일거래량",
        description="baseprevol — long(12). Consume as returned by LS.",
    )
    basebidprc: int = Field(
        default=0,
        title="기초자산매수호가",
        description="basebidprc — long(9). Consume as returned by LS.",
    )
    baseaskprc: int = Field(
        default=0,
        title="기초자산매도호가",
        description="baseaskprc — long(9). Consume as returned by LS.",
    )
    basefornetbid: int = Field(
        default=0,
        title="기초자산외국계회원사순매수",
        description="basefornetbid — long(12). Consume as returned by LS.",
    )
    prodgrp: str = Field(
        default="",
        title="상품군",
        description="prodgrp — char(20). Consume as returned by LS.",
    )
    mulcnt: float = Field(
        default=0.0,
        title="승수",
        description="mulcnt — float(12.8). Consume as returned by LS.",
    )
    danhochk: str = Field(
        default="",
        title="단일가호가여부",
        description="danhochk — char(1). Consume as returned by LS.",
    )
    yeprice: int = Field(
        default=0,
        title="예상체결가",
        description="yeprice — long(8). Consume as returned by LS.",
    )
    jnilysign: str = Field(
        default="",
        title="예상체결가전일종가대비구분",
        description="jnilysign — char(1). Consume as returned by LS.",
    )
    jnilychange: int = Field(
        default=0,
        title="예상체결가전일종가대비",
        description="jnilychange — long(8). Consume as returned by LS.",
    )
    jnilydrate: float = Field(
        default=0.0,
        title="예상체결가전일종가등락율",
        description="jnilydrate — float(6.2). Consume as returned by LS.",
    )

class T8402Request(BaseModel):
    """Request envelope for t8402."""

    header: T8402RequestHeader = T8402RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8402",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8402",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8402Response(BaseModel):
    """Response envelope for t8402."""

    header: Optional[T8402ResponseHeader] = None
    block: Optional[T8402OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8402RequestHeader",
    "T8402ResponseHeader",
    "T8402InBlock",
    "T8402OutBlock",
    "T8402Request",
    "T8402Response",
]