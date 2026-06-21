"""Pydantic models for LS Securities OpenAPI t1717 (외인기관종목별동향(t1717)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1717RequestHeader(BlockRequestHeader):
    pass


class T1717ResponseHeader(BlockResponseHeader):
    pass

class T1717InBlock(BaseModel):
    """t1717InBlock — input block. 기본입력"""

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
        title="시작일자(일간조회일경우는space)",
        description="fromdt — char(8). Consume as returned by LS.",
    )
    todt: str = Field(
        ...,
        title="종료일자",
        description="todt — char(8). Consume as returned by LS.",
    )
    dan_gb: str = Field(
        ...,
        title="단가구분(0:전체1:매수혹은매도단가)",
        description="dan_gb — char(1). Consume as returned by LS.",
    )
    exchgubun: str = Field(
        ...,
        title="거래소구분코드",
        description="exchgubun — char(1). Consume as returned by LS.",
    )

class T1717OutBlock(BaseModel):
    """t1717OutBlock — output block (occurs — list of rows). 출력"""

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
        description="diff — float(6.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="누적거래량",
        description="volume — long(12). Consume as returned by LS.",
    )
    tjj0000_vol: int = Field(
        default=0,
        title="사모펀드(순매수량)",
        description="tjj0000_vol — long(12). Consume as returned by LS.",
    )
    tjj0001_vol: int = Field(
        default=0,
        title="증권(순매수량)",
        description="tjj0001_vol — long(12). Consume as returned by LS.",
    )
    tjj0002_vol: int = Field(
        default=0,
        title="보험(순매수량)",
        description="tjj0002_vol — long(12). Consume as returned by LS.",
    )
    tjj0003_vol: int = Field(
        default=0,
        title="투신(순매수량)",
        description="tjj0003_vol — long(12). Consume as returned by LS.",
    )
    tjj0004_vol: int = Field(
        default=0,
        title="은행(순매수량)",
        description="tjj0004_vol — long(12). Consume as returned by LS.",
    )
    tjj0005_vol: int = Field(
        default=0,
        title="종금(순매수량)",
        description="tjj0005_vol — long(12). Consume as returned by LS.",
    )
    tjj0006_vol: int = Field(
        default=0,
        title="기금(순매수량)",
        description="tjj0006_vol — long(12). Consume as returned by LS.",
    )
    tjj0007_vol: int = Field(
        default=0,
        title="기타법인(순매수량)",
        description="tjj0007_vol — long(12). Consume as returned by LS.",
    )
    tjj0008_vol: int = Field(
        default=0,
        title="개인(순매수량)",
        description="tjj0008_vol — long(12). Consume as returned by LS.",
    )
    tjj0009_vol: int = Field(
        default=0,
        title="등록외국인(순매수량)",
        description="tjj0009_vol — long(12). Consume as returned by LS.",
    )
    tjj0010_vol: int = Field(
        default=0,
        title="미등록외국인(순매수량)",
        description="tjj0010_vol — long(12). Consume as returned by LS.",
    )
    tjj0011_vol: int = Field(
        default=0,
        title="국가외(순매수량)",
        description="tjj0011_vol — long(12). Consume as returned by LS.",
    )
    tjj0018_vol: int = Field(
        default=0,
        title="기관(순매수량)",
        description="tjj0018_vol — long(12). Consume as returned by LS.",
    )
    tjj0016_vol: int = Field(
        default=0,
        title="외인계(순매수량)(등록+미등록)",
        description="tjj0016_vol — long(12). Consume as returned by LS.",
    )
    tjj0017_vol: int = Field(
        default=0,
        title="기타계(순매수량)(기타+국가)",
        description="tjj0017_vol — long(12). Consume as returned by LS.",
    )
    tjj0000_dan: int = Field(
        default=0,
        title="사모펀드(단가)",
        description="tjj0000_dan — long(12). Consume as returned by LS.",
    )
    tjj0001_dan: int = Field(
        default=0,
        title="증권(단가)",
        description="tjj0001_dan — long(12). Consume as returned by LS.",
    )
    tjj0002_dan: int = Field(
        default=0,
        title="보험(단가)",
        description="tjj0002_dan — long(12). Consume as returned by LS.",
    )
    tjj0003_dan: int = Field(
        default=0,
        title="투신(단가)",
        description="tjj0003_dan — long(12). Consume as returned by LS.",
    )
    tjj0004_dan: int = Field(
        default=0,
        title="은행(단가)",
        description="tjj0004_dan — long(12). Consume as returned by LS.",
    )
    tjj0005_dan: int = Field(
        default=0,
        title="종금(단가)",
        description="tjj0005_dan — long(12). Consume as returned by LS.",
    )
    tjj0006_dan: int = Field(
        default=0,
        title="기금(단가)",
        description="tjj0006_dan — long(12). Consume as returned by LS.",
    )
    tjj0007_dan: int = Field(
        default=0,
        title="기타법인(단가)",
        description="tjj0007_dan — long(12). Consume as returned by LS.",
    )
    tjj0008_dan: int = Field(
        default=0,
        title="개인(단가)",
        description="tjj0008_dan — long(12). Consume as returned by LS.",
    )
    tjj0009_dan: int = Field(
        default=0,
        title="등록외국인(단가)",
        description="tjj0009_dan — long(12). Consume as returned by LS.",
    )
    tjj0010_dan: int = Field(
        default=0,
        title="미등록외국인(단가)",
        description="tjj0010_dan — long(12). Consume as returned by LS.",
    )
    tjj0011_dan: int = Field(
        default=0,
        title="국가외(단가)",
        description="tjj0011_dan — long(12). Consume as returned by LS.",
    )
    tjj0018_dan: int = Field(
        default=0,
        title="기관(단가)",
        description="tjj0018_dan — long(12). Consume as returned by LS.",
    )
    tjj0016_dan: int = Field(
        default=0,
        title="외인계(단가)(등록+미등록)",
        description="tjj0016_dan — long(12). Consume as returned by LS.",
    )
    tjj0017_dan: int = Field(
        default=0,
        title="기타계(단가)(기타+국가)",
        description="tjj0017_dan — long(12). Consume as returned by LS.",
    )

class T1717Request(BaseModel):
    """Request envelope for t1717."""

    header: T1717RequestHeader = T1717RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1717",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1717",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1717Response(BaseModel):
    """Response envelope for t1717."""

    header: Optional[T1717ResponseHeader] = None
    block: List[T1717OutBlock] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1717RequestHeader",
    "T1717ResponseHeader",
    "T1717InBlock",
    "T1717OutBlock",
    "T1717Request",
    "T1717Response",
]