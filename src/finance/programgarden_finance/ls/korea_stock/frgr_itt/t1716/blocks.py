"""Pydantic models for LS Securities OpenAPI t1716 (외인기관종목별동향(t1716)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1716RequestHeader(BlockRequestHeader):
    pass


class T1716ResponseHeader(BlockResponseHeader):
    pass

class T1716InBlock(BaseModel):
    """t1716InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    gubun: str = Field(
        ...,
        title="구분(0:일간순매수1:기간누적순매수)",
        description="gubun — char(1). Consume as returned by LS.",
    )
    fromdt: str = Field(
        ...,
        title="시작일자",
        description="fromdt — char(8). Consume as returned by LS.",
    )
    todt: str = Field(
        ...,
        title="종료일자",
        description="todt — char(8). Consume as returned by LS.",
    )
    prapp: int = Field(
        ...,
        title="PR감산적용율",
        description="prapp — long(3). Consume as returned by LS.",
    )
    prgubun: str = Field(
        ...,
        title="PR적용구분(0:적용안함1:적용)",
        description="prgubun — char(1). Consume as returned by LS.",
    )
    orggubun: str = Field(
        ...,
        title="기관적용",
        description="orggubun — char(1). Consume as returned by LS.",
    )
    frggubun: str = Field(
        ...,
        title="외인적용",
        description="frggubun — char(1). Consume as returned by LS.",
    )
    exchgubun: str = Field(
        ...,
        title="거래소구분코드",
        description="exchgubun — char(1). Consume as returned by LS.",
    )

class T1716OutBlock(BaseModel):
    """t1716OutBlock — output block (occurs — list of rows). 출력"""

    date: str = Field(
        default="",
        title="일자",
        description="date — char(8). Consume as returned by LS.",
    )
    close: int = Field(
        default=0,
        title="종가",
        description="close — long(8). Consume as returned by LS.",
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
        description="diff — double(6.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="누적거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    krx_0008: int = Field(
        default=0,
        title="거래소_개인",
        description="krx_0008 — long(12). Consume as returned by LS.",
    )
    krx_0018: int = Field(
        default=0,
        title="거래소_기관",
        description="krx_0018 — long(12). Consume as returned by LS.",
    )
    krx_0009: int = Field(
        default=0,
        title="거래소_외국인",
        description="krx_0009 — long(12). Consume as returned by LS.",
    )
    pgmvol: int = Field(
        default=0,
        title="프로그램",
        description="pgmvol — long(12). Consume as returned by LS.",
    )
    fsc_listing: int = Field(
        default=0,
        title="금감원_외인보유주식수",
        description="fsc_listing — long(12). Consume as returned by LS.",
    )
    fsc_sjrate: float = Field(
        default=0.0,
        title="금감원_소진율",
        description="fsc_sjrate — double(6.2). Consume as returned by LS.",
    )
    fsc_0009: int = Field(
        default=0,
        title="금감원_외국인",
        description="fsc_0009 — long(12). Consume as returned by LS.",
    )
    gm_volume: int = Field(
        default=0,
        title="공매도수량",
        description="gm_volume — long(12). Consume as returned by LS.",
    )
    gm_value: int = Field(
        default=0,
        title="공매도대금",
        description="gm_value — long(12). Consume as returned by LS.",
    )

class T1716Request(BaseModel):
    """Request envelope for t1716."""

    header: T1716RequestHeader = T1716RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1716",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1716",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1716Response(BaseModel):
    """Response envelope for t1716."""

    header: Optional[T1716ResponseHeader] = None
    block: List[T1716OutBlock] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1716RequestHeader",
    "T1716ResponseHeader",
    "T1716InBlock",
    "T1716OutBlock",
    "T1716Request",
    "T1716Response",
]