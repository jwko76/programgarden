"""Pydantic models for LS Securities OpenAPI t2545 (상품선물투자자매매동향(챠트용)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T2545RequestHeader(BlockRequestHeader):
    pass


class T2545ResponseHeader(BlockResponseHeader):
    pass

class T2545InBlock(BaseModel):
    """t2545InBlock — input block. 기본입력"""

    eitem: str = Field(
        ...,
        title="상품ID",
        description="eitem — char(2). Consume as returned by LS.",
    )
    sgubun: str = Field(
        ...,
        title="시장구분",
        description="sgubun — char(1). Consume as returned by LS.",
    )
    upcode: str = Field(
        ...,
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )
    nmin: int = Field(
        ...,
        title="N분",
        description="nmin — int(2). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="조회건수",
        description="cnt — int(3). Consume as returned by LS.",
    )
    bgubun: str = Field(
        ...,
        title="전일분",
        description="bgubun — char(1). Consume as returned by LS.",
    )

class T2545OutBlock(BaseModel):
    """t2545OutBlock — output block. 기본출력"""

    eitem: str = Field(
        default="",
        title="상품ID",
        description="eitem — char(2). Consume as returned by LS.",
    )
    sgubun: str = Field(
        default="",
        title="시장구분",
        description="sgubun — char(1). Consume as returned by LS.",
    )
    indcode: str = Field(
        default="",
        title="개인투자자코드",
        description="indcode — char(4). Consume as returned by LS.",
    )
    forcode: str = Field(
        default="",
        title="외국인투자자코드",
        description="forcode — char(4). Consume as returned by LS.",
    )
    syscode: str = Field(
        default="",
        title="기관계투자자코드",
        description="syscode — char(4). Consume as returned by LS.",
    )
    stocode: str = Field(
        default="",
        title="증권투자자코드",
        description="stocode — char(4). Consume as returned by LS.",
    )
    invcode: str = Field(
        default="",
        title="투신투자자코드",
        description="invcode — char(4). Consume as returned by LS.",
    )
    bancode: str = Field(
        default="",
        title="은행투자자코드",
        description="bancode — char(4). Consume as returned by LS.",
    )
    inscode: str = Field(
        default="",
        title="보험투자자코드",
        description="inscode — char(4). Consume as returned by LS.",
    )
    fincode: str = Field(
        default="",
        title="종금투자자코드",
        description="fincode — char(4). Consume as returned by LS.",
    )
    moncode: str = Field(
        default="",
        title="기금투자자코드",
        description="moncode — char(4). Consume as returned by LS.",
    )
    etccode: str = Field(
        default="",
        title="기타투자자코드",
        description="etccode — char(4). Consume as returned by LS.",
    )
    natcode: str = Field(
        default="",
        title="국가투자자코드",
        description="natcode — char(4). Consume as returned by LS.",
    )
    pefcode: str = Field(
        default="",
        title="사모펀드투자자코드",
        description="pefcode — char(4). Consume as returned by LS.",
    )
    jisucd: str = Field(
        default="",
        title="기준지수코드",
        description="jisucd — char(8). Consume as returned by LS.",
    )
    jisunm: str = Field(
        default="",
        title="기준지수명",
        description="jisunm — char(20). Consume as returned by LS.",
    )

class T2545OutBlock1(BaseModel):
    """t2545OutBlock1 — output block (occurs — list of rows). 출력1"""

    date: str = Field(
        default="",
        title="일자",
        description="date — char(8). Consume as returned by LS.",
    )
    time: str = Field(
        default="",
        title="시간",
        description="time — char(6). Consume as returned by LS.",
    )
    datetime: str = Field(
        default="",
        title="일자시간",
        description="datetime — char(14). Consume as returned by LS.",
    )
    indmsvol: int = Field(
        default=0,
        title="개인순매수거래량",
        description="indmsvol — long(8). Consume as returned by LS.",
    )
    indmsamt: float = Field(
        default=0.0,
        title="개인순매수거래대금",
        description="indmsamt — double(12.0). Consume as returned by LS.",
    )
    formsvol: int = Field(
        default=0,
        title="외국인순매수거래량",
        description="formsvol — long(8). Consume as returned by LS.",
    )
    formsamt: float = Field(
        default=0.0,
        title="외국인순매수거래대금",
        description="formsamt — double(12.0). Consume as returned by LS.",
    )
    sysmsvol: int = Field(
        default=0,
        title="기관계순매수거래량",
        description="sysmsvol — long(8). Consume as returned by LS.",
    )
    sysmsamt: float = Field(
        default=0.0,
        title="기관계순매수거래대금",
        description="sysmsamt — double(12.0). Consume as returned by LS.",
    )
    stomsvol: int = Field(
        default=0,
        title="증권순매수거래량",
        description="stomsvol — long(8). Consume as returned by LS.",
    )
    stomsamt: float = Field(
        default=0.0,
        title="증권순매수거래대금",
        description="stomsamt — double(12.0). Consume as returned by LS.",
    )
    invmsvol: int = Field(
        default=0,
        title="투신순매수거래량",
        description="invmsvol — long(8). Consume as returned by LS.",
    )
    invmsamt: float = Field(
        default=0.0,
        title="투신순매수거래대금",
        description="invmsamt — double(12.0). Consume as returned by LS.",
    )
    banmsvol: int = Field(
        default=0,
        title="은행순매수거래량",
        description="banmsvol — long(8). Consume as returned by LS.",
    )
    banmsamt: float = Field(
        default=0.0,
        title="은행순매수거래대금",
        description="banmsamt — double(12.0). Consume as returned by LS.",
    )
    insmsvol: int = Field(
        default=0,
        title="보험순매수거래량",
        description="insmsvol — long(8). Consume as returned by LS.",
    )
    insmsamt: float = Field(
        default=0.0,
        title="보험순매수거래대금",
        description="insmsamt — double(12.0). Consume as returned by LS.",
    )
    finmsvol: int = Field(
        default=0,
        title="종금순매수거래량",
        description="finmsvol — long(8). Consume as returned by LS.",
    )
    finmsamt: float = Field(
        default=0.0,
        title="종금순매수거래대금",
        description="finmsamt — double(12.0). Consume as returned by LS.",
    )
    monmsvol: int = Field(
        default=0,
        title="기금순매수거래량",
        description="monmsvol — long(8). Consume as returned by LS.",
    )
    monmsamt: float = Field(
        default=0.0,
        title="기금순매수거래대금",
        description="monmsamt — double(12.0). Consume as returned by LS.",
    )
    etcmsvol: int = Field(
        default=0,
        title="기타순매수거래량",
        description="etcmsvol — long(8). Consume as returned by LS.",
    )
    etcmsamt: float = Field(
        default=0.0,
        title="기타순매수거래대금",
        description="etcmsamt — double(12.0). Consume as returned by LS.",
    )
    natmsvol: int = Field(
        default=0,
        title="국가순매수거래량",
        description="natmsvol — long(8). Consume as returned by LS.",
    )
    natmsamt: float = Field(
        default=0.0,
        title="국가순매수거래대금",
        description="natmsamt — double(12.0). Consume as returned by LS.",
    )
    pefmsvol: int = Field(
        default=0,
        title="사모펀드순매수거래량",
        description="pefmsvol — long(8). Consume as returned by LS.",
    )
    pefmsamt: float = Field(
        default=0.0,
        title="사모펀드순매수거래대금",
        description="pefmsamt — double(12.0). Consume as returned by LS.",
    )
    upclose: float = Field(
        default=0.0,
        title="기준지수",
        description="upclose — float(6.2). Consume as returned by LS.",
    )
    upcvolume: int = Field(
        default=0,
        title="기준체결거래량",
        description="upcvolume — long(8). Consume as returned by LS.",
    )
    upvolume: float = Field(
        default=0.0,
        title="기준누적거래량",
        description="upvolume — double(12.0). Consume as returned by LS.",
    )
    upvalue: float = Field(
        default=0.0,
        title="기준거래대금",
        description="upvalue — double(12.0). Consume as returned by LS.",
    )

class T2545Request(BaseModel):
    """Request envelope for t2545."""

    header: T2545RequestHeader = T2545RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t2545",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t2545",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T2545Response(BaseModel):
    """Response envelope for t2545."""

    header: Optional[T2545ResponseHeader] = None
    block: Optional[T2545OutBlock] = None
    block1: List[T2545OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T2545RequestHeader",
    "T2545ResponseHeader",
    "T2545InBlock",
    "T2545OutBlock",
    "T2545OutBlock1",
    "T2545Request",
    "T2545Response",
]