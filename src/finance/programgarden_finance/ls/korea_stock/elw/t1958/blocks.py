"""Pydantic models for LS Securities OpenAPI t1958 (ELW종목비교(t1958)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1958RequestHeader(BlockRequestHeader):
    pass


class T1958ResponseHeader(BlockResponseHeader):
    pass

class T1958InBlock(BaseModel):
    """t1958InBlock — input block. 입력"""

    shcode1: str = Field(
        ...,
        title="종목코드1",
        description="shcode1 — char(6). Consume as returned by LS.",
    )
    shcode2: str = Field(
        ...,
        title="종목코드2",
        description="shcode2 — char(6). Consume as returned by LS.",
    )

class T1958OutBlock(BaseModel):
    """t1958OutBlock — output block. 출력"""

    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(40). Consume as returned by LS.",
    )
    item1: str = Field(
        default="",
        title="기초자산",
        description="item1 — char(12). Consume as returned by LS.",
    )
    issuernmk: str = Field(
        default="",
        title="발행사",
        description="issuernmk — char(40). Consume as returned by LS.",
    )
    elwopt: str = Field(
        default="",
        title="콜풋구분",
        description="elwopt — char(2). Consume as returned by LS.",
    )
    elwtype: str = Field(
        default="",
        title="행사방식",
        description="elwtype — char(2). Consume as returned by LS.",
    )
    settletype: str = Field(
        default="",
        title="결제방법",
        description="settletype — char(2). Consume as returned by LS.",
    )
    elwexec: float = Field(
        default=0.0,
        title="행사가",
        description="elwexec — float(8.2). Consume as returned by LS.",
    )
    convrate: float = Field(
        default=0.0,
        title="전환비율",
        description="convrate — float(12.4). Consume as returned by LS.",
    )
    listing: float = Field(
        default=0.0,
        title="발행수량",
        description="listing — float(12). Consume as returned by LS.",
    )
    mmsdate: str = Field(
        default="",
        title="행사개시일",
        description="mmsdate — char(8). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="최종거래일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    nofdays: int = Field(
        default=0,
        title="거래잔존일수",
        description="nofdays — long(4). Consume as returned by LS.",
    )
    payday: str = Field(
        default="",
        title="지급일",
        description="payday — char(8). Consume as returned by LS.",
    )
    parity: float = Field(
        default=0.0,
        title="패리티",
        description="parity — float(6.2). Consume as returned by LS.",
    )
    premium: float = Field(
        default=0.0,
        title="프리미엄",
        description="premium — float(6.2). Consume as returned by LS.",
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
    gearing: float = Field(
        default=0.0,
        title="기어링",
        description="gearing — float(6.2). Consume as returned by LS.",
    )
    egearing: float = Field(
        default=0.0,
        title="e.기어링",
        description="egearing — float(6.2). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="가격",
        description="price — long(8). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — float(12). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )

class T1958OutBlock1(BaseModel):
    """t1958OutBlock1 — output block. 출력1"""

    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(40). Consume as returned by LS.",
    )
    item1: str = Field(
        default="",
        title="기초자산",
        description="item1 — char(12). Consume as returned by LS.",
    )
    issuernmk: str = Field(
        default="",
        title="발행사",
        description="issuernmk — char(40). Consume as returned by LS.",
    )
    elwopt: str = Field(
        default="",
        title="콜풋구분",
        description="elwopt — char(2). Consume as returned by LS.",
    )
    elwtype: str = Field(
        default="",
        title="행사방식",
        description="elwtype — char(2). Consume as returned by LS.",
    )
    settletype: str = Field(
        default="",
        title="결제방법",
        description="settletype — char(2). Consume as returned by LS.",
    )
    elwexec: float = Field(
        default=0.0,
        title="행사가",
        description="elwexec — float(8.2). Consume as returned by LS.",
    )
    convrate: float = Field(
        default=0.0,
        title="전환비율",
        description="convrate — float(12.4). Consume as returned by LS.",
    )
    listing: float = Field(
        default=0.0,
        title="발행수량",
        description="listing — float(12). Consume as returned by LS.",
    )
    mmsdate: str = Field(
        default="",
        title="행사개시일",
        description="mmsdate — char(8). Consume as returned by LS.",
    )
    lastdate: str = Field(
        default="",
        title="최종거래일",
        description="lastdate — char(8). Consume as returned by LS.",
    )
    nofdays: int = Field(
        default=0,
        title="거래잔존일수",
        description="nofdays — long(4). Consume as returned by LS.",
    )
    payday: str = Field(
        default="",
        title="지급일",
        description="payday — char(8). Consume as returned by LS.",
    )
    parity: float = Field(
        default=0.0,
        title="패리티",
        description="parity — float(6.2). Consume as returned by LS.",
    )
    premium: float = Field(
        default=0.0,
        title="프리미엄",
        description="premium — float(6.2). Consume as returned by LS.",
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
    gearing: float = Field(
        default=0.0,
        title="기어링",
        description="gearing — float(6.2). Consume as returned by LS.",
    )
    egearing: float = Field(
        default=0.0,
        title="e.기어링",
        description="egearing — float(6.2). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="가격",
        description="price — long(8). Consume as returned by LS.",
    )
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — float(12). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )

class T1958OutBlock2(BaseModel):
    """t1958OutBlock2 — output block. 출력2"""

    hnamecmp: str = Field(
        default="",
        title="종목명비교",
        description="hnamecmp — char(6). Consume as returned by LS.",
    )
    item1cmp: str = Field(
        default="",
        title="기초자산비교",
        description="item1cmp — char(6). Consume as returned by LS.",
    )
    issuernmkcmp: str = Field(
        default="",
        title="발행사비교",
        description="issuernmkcmp — char(6). Consume as returned by LS.",
    )
    elwoptcmp: str = Field(
        default="",
        title="콜풋구분비교",
        description="elwoptcmp — char(6). Consume as returned by LS.",
    )
    elwtypecmp: str = Field(
        default="",
        title="행사방식비교",
        description="elwtypecmp — char(6). Consume as returned by LS.",
    )
    settlecmp: str = Field(
        default="",
        title="결제방법비교",
        description="settlecmp — char(6). Consume as returned by LS.",
    )
    elwexeccmp: float = Field(
        default=0.0,
        title="행사가비교",
        description="elwexeccmp — float(8.2). Consume as returned by LS.",
    )
    convcmp: float = Field(
        default=0.0,
        title="전환비율비교",
        description="convcmp — float(12.4). Consume as returned by LS.",
    )
    listingcmp: float = Field(
        default=0.0,
        title="발행수량비교",
        description="listingcmp — float(12). Consume as returned by LS.",
    )
    mmsdatecmp: str = Field(
        default="",
        title="행사개시일비교",
        description="mmsdatecmp — char(6). Consume as returned by LS.",
    )
    lastdatecmp: str = Field(
        default="",
        title="최종거래일비교",
        description="lastdatecmp — char(6). Consume as returned by LS.",
    )
    nofdayscmp: str = Field(
        default="",
        title="거래잔존일수비교",
        description="nofdayscmp — char(6). Consume as returned by LS.",
    )
    paydaycmp: str = Field(
        default="",
        title="지급일비교",
        description="paydaycmp — char(6). Consume as returned by LS.",
    )
    paritycmp: float = Field(
        default=0.0,
        title="패리티비교",
        description="paritycmp — float(6.2). Consume as returned by LS.",
    )
    premiumcmp: float = Field(
        default=0.0,
        title="프리미엄비교",
        description="premiumcmp — float(6.2). Consume as returned by LS.",
    )
    beratecmp: float = Field(
        default=0.0,
        title="손익분기비교",
        description="beratecmp — float(6.2). Consume as returned by LS.",
    )
    captcmp: float = Field(
        default=0.0,
        title="자본지지비교",
        description="captcmp — float(6.2). Consume as returned by LS.",
    )
    gearingcmp: float = Field(
        default=0.0,
        title="기어링비교",
        description="gearingcmp — float(6.2). Consume as returned by LS.",
    )
    egearingcmp: float = Field(
        default=0.0,
        title="e.기어링비교",
        description="egearingcmp — float(6.2). Consume as returned by LS.",
    )
    pricecmp: int = Field(
        default=0,
        title="가격비교",
        description="pricecmp — long(8). Consume as returned by LS.",
    )
    volumecmp: float = Field(
        default=0.0,
        title="거래량비교",
        description="volumecmp — float(12). Consume as returned by LS.",
    )
    diffcmp: float = Field(
        default=0.0,
        title="등락율비교",
        description="diffcmp — float(6.2). Consume as returned by LS.",
    )

class T1958Request(BaseModel):
    """Request envelope for t1958."""

    header: T1958RequestHeader = T1958RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1958",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1958",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1958Response(BaseModel):
    """Response envelope for t1958."""

    header: Optional[T1958ResponseHeader] = None
    block: Optional[T1958OutBlock] = None
    block1: Optional[T1958OutBlock1] = None
    block2: Optional[T1958OutBlock2] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1958RequestHeader",
    "T1958ResponseHeader",
    "T1958InBlock",
    "T1958OutBlock",
    "T1958OutBlock1",
    "T1958OutBlock2",
    "T1958Request",
    "T1958Response",
]