"""Pydantic models for LS Securities OpenAPI t1972 (ELW현재가(거래원)조회(t1972)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1972RequestHeader(BlockRequestHeader):
    pass


class T1972ResponseHeader(BlockResponseHeader):
    pass

class T1972InBlock(BaseModel):
    """t1972InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="단축코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1972OutBlock(BaseModel):
    """t1972OutBlock — output block. 출력"""

    hname: str = Field(
        default="",
        title="한글명",
        description="hname — char(40). Consume as returned by LS.",
    )
    expcode: str = Field(
        default="",
        title="표준코드",
        description="expcode — char(12). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="단축코드",
        description="shcode — char(9). Consume as returned by LS.",
    )
    offerno1: str = Field(
        default="",
        title="매도증권사코드1",
        description="offerno1 — char(6). Consume as returned by LS.",
    )
    bidno1: str = Field(
        default="",
        title="매수증권사코드1",
        description="bidno1 — char(6). Consume as returned by LS.",
    )
    dvol1: int = Field(
        default=0,
        title="총매도수량1",
        description="dvol1 — long(12). Consume as returned by LS.",
    )
    svol1: int = Field(
        default=0,
        title="총매수수량1",
        description="svol1 — long(12). Consume as returned by LS.",
    )
    dcha1: int = Field(
        default=0,
        title="매도증감1",
        description="dcha1 — long(12). Consume as returned by LS.",
    )
    scha1: int = Field(
        default=0,
        title="매수증감1",
        description="scha1 — long(12). Consume as returned by LS.",
    )
    ddiff1: float = Field(
        default=0.0,
        title="매도비율1",
        description="ddiff1 — float(6.2). Consume as returned by LS.",
    )
    sdiff1: float = Field(
        default=0.0,
        title="매수비율1",
        description="sdiff1 — float(6.2). Consume as returned by LS.",
    )
    offerno2: str = Field(
        default="",
        title="매도증권사코드2",
        description="offerno2 — char(6). Consume as returned by LS.",
    )
    bidno2: str = Field(
        default="",
        title="매수증권사코드2",
        description="bidno2 — char(6). Consume as returned by LS.",
    )
    dvol2: int = Field(
        default=0,
        title="총매도수량2",
        description="dvol2 — long(12). Consume as returned by LS.",
    )
    svol2: int = Field(
        default=0,
        title="총매수수량2",
        description="svol2 — long(12). Consume as returned by LS.",
    )
    dcha2: int = Field(
        default=0,
        title="매도증감2",
        description="dcha2 — long(12). Consume as returned by LS.",
    )
    scha2: int = Field(
        default=0,
        title="매수증감2",
        description="scha2 — long(12). Consume as returned by LS.",
    )
    ddiff2: float = Field(
        default=0.0,
        title="매도비율2",
        description="ddiff2 — float(6.2). Consume as returned by LS.",
    )
    sdiff2: float = Field(
        default=0.0,
        title="매수비율2",
        description="sdiff2 — float(6.2). Consume as returned by LS.",
    )
    offerno3: str = Field(
        default="",
        title="매도증권사코드3",
        description="offerno3 — char(6). Consume as returned by LS.",
    )
    bidno3: str = Field(
        default="",
        title="매수증권사코드3",
        description="bidno3 — char(6). Consume as returned by LS.",
    )
    dvol3: int = Field(
        default=0,
        title="총매도수량3",
        description="dvol3 — long(12). Consume as returned by LS.",
    )
    svol3: int = Field(
        default=0,
        title="총매수수량3",
        description="svol3 — long(12). Consume as returned by LS.",
    )
    dcha3: int = Field(
        default=0,
        title="매도증감3",
        description="dcha3 — long(12). Consume as returned by LS.",
    )
    scha3: int = Field(
        default=0,
        title="매수증감3",
        description="scha3 — long(12). Consume as returned by LS.",
    )
    ddiff3: float = Field(
        default=0.0,
        title="매도비율3",
        description="ddiff3 — float(6.2). Consume as returned by LS.",
    )
    sdiff3: float = Field(
        default=0.0,
        title="매수비율3",
        description="sdiff3 — float(6.2). Consume as returned by LS.",
    )
    offerno4: str = Field(
        default="",
        title="매도증권사코드4",
        description="offerno4 — char(6). Consume as returned by LS.",
    )
    bidno4: str = Field(
        default="",
        title="매수증권사코드4",
        description="bidno4 — char(6). Consume as returned by LS.",
    )
    dvol4: int = Field(
        default=0,
        title="총매도수량4",
        description="dvol4 — long(12). Consume as returned by LS.",
    )
    svol4: int = Field(
        default=0,
        title="총매수수량4",
        description="svol4 — long(12). Consume as returned by LS.",
    )
    dcha4: int = Field(
        default=0,
        title="매도증감4",
        description="dcha4 — long(12). Consume as returned by LS.",
    )
    scha4: int = Field(
        default=0,
        title="매수증감4",
        description="scha4 — long(12). Consume as returned by LS.",
    )
    ddiff4: float = Field(
        default=0.0,
        title="매도비율4",
        description="ddiff4 — float(6.2). Consume as returned by LS.",
    )
    sdiff4: float = Field(
        default=0.0,
        title="매수비율4",
        description="sdiff4 — float(6.2). Consume as returned by LS.",
    )
    offerno5: str = Field(
        default="",
        title="매도증권사코드5",
        description="offerno5 — char(6). Consume as returned by LS.",
    )
    bidno5: str = Field(
        default="",
        title="매수증권사코드5",
        description="bidno5 — char(6). Consume as returned by LS.",
    )
    dvol5: int = Field(
        default=0,
        title="총매도수량5",
        description="dvol5 — long(12). Consume as returned by LS.",
    )
    svol5: int = Field(
        default=0,
        title="총매수수량5",
        description="svol5 — long(12). Consume as returned by LS.",
    )
    dcha5: int = Field(
        default=0,
        title="매도증감5",
        description="dcha5 — long(12). Consume as returned by LS.",
    )
    scha5: int = Field(
        default=0,
        title="매수증감5",
        description="scha5 — long(12). Consume as returned by LS.",
    )
    ddiff5: float = Field(
        default=0.0,
        title="매도비율5",
        description="ddiff5 — float(6.2). Consume as returned by LS.",
    )
    sdiff5: float = Field(
        default=0.0,
        title="매수비율5",
        description="sdiff5 — float(6.2). Consume as returned by LS.",
    )
    fwdvl: int = Field(
        default=0,
        title="외국계매도합계수량",
        description="fwdvl — long(12). Consume as returned by LS.",
    )
    fwsvl: int = Field(
        default=0,
        title="외국계매수합계수량",
        description="fwsvl — long(12). Consume as returned by LS.",
    )
    ftradmdcha: int = Field(
        default=0,
        title="외국계매도직전대비",
        description="ftradmdcha — long(12). Consume as returned by LS.",
    )
    ftradmscha: int = Field(
        default=0,
        title="외국계매수직전대비",
        description="ftradmscha — long(12). Consume as returned by LS.",
    )
    fwddiff: float = Field(
        default=0.0,
        title="외국계매도합계비율",
        description="fwddiff — float(6.2). Consume as returned by LS.",
    )
    fwsdiff: float = Field(
        default=0.0,
        title="외국계매수합계비율",
        description="fwsdiff — float(6.2). Consume as returned by LS.",
    )

class T1972Request(BaseModel):
    """Request envelope for t1972."""

    header: T1972RequestHeader = T1972RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1972",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1972",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1972Response(BaseModel):
    """Response envelope for t1972."""

    header: Optional[T1972ResponseHeader] = None
    block: Optional[T1972OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1972RequestHeader",
    "T1972ResponseHeader",
    "T1972InBlock",
    "T1972OutBlock",
    "T1972Request",
    "T1972Response",
]