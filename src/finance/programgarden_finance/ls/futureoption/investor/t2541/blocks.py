"""Pydantic models for LS Securities OpenAPI t2541 (상품선물투자자매매동향(실시간)(t2541)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T2541RequestHeader(BlockRequestHeader):
    pass


class T2541ResponseHeader(BlockResponseHeader):
    pass

class T2541InBlock(BaseModel):
    """t2541InBlock — input block. 기본입력"""

    eitem: str = Field(
        ...,
        title="상품ID",
        description="eitem — char(2). Consume as returned by LS.",
    )
    market: str = Field(
        ...,
        title="시장구분",
        description="market — char(1). Consume as returned by LS.",
    )
    upcode: str = Field(
        ...,
        title="업종코드",
        description="upcode — char(3). Consume as returned by LS.",
    )
    gubun1: str = Field(
        ...,
        title="수량구분",
        description="gubun1 — char(1). Consume as returned by LS.",
    )
    gubun2: str = Field(
        ...,
        title="전일분구분",
        description="gubun2 — char(1). Consume as returned by LS.",
    )
    cts_time: str = Field(
        ...,
        title="CTSTIME",
        description="cts_time — char(8). Consume as returned by LS.",
    )
    cts_idx: int = Field(
        ...,
        title="CTSIDX",
        description="cts_idx — long(4). Consume as returned by LS.",
    )
    cnt: int = Field(
        ...,
        title="조회건수",
        description="cnt — int(4). Consume as returned by LS.",
    )

class T2541OutBlock(BaseModel):
    """t2541OutBlock — output block. 기본출력"""

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
    cts_time: str = Field(
        default="",
        title="CTSTIME",
        description="cts_time — char(8). Consume as returned by LS.",
    )
    tjjcode_08: str = Field(
        default="",
        title="개인투자자코드",
        description="tjjcode_08 — char(4). Consume as returned by LS.",
    )
    ms_08: int = Field(
        default=0,
        title="개인매수",
        description="ms_08 — long(12). Consume as returned by LS.",
    )
    md_08: int = Field(
        default=0,
        title="개인매도",
        description="md_08 — long(12). Consume as returned by LS.",
    )
    rate_08: int = Field(
        default=0,
        title="개인증감",
        description="rate_08 — long(12). Consume as returned by LS.",
    )
    svolume_08: int = Field(
        default=0,
        title="개인순매수",
        description="svolume_08 — long(12). Consume as returned by LS.",
    )
    jjcode_17: str = Field(
        default="",
        title="외국인투자자코드",
        description="jjcode_17 — char(4). Consume as returned by LS.",
    )
    ms_17: int = Field(
        default=0,
        title="외국인매수",
        description="ms_17 — long(12). Consume as returned by LS.",
    )
    md_17: int = Field(
        default=0,
        title="외국인매도",
        description="md_17 — long(12). Consume as returned by LS.",
    )
    rate_17: int = Field(
        default=0,
        title="외국인증감",
        description="rate_17 — long(12). Consume as returned by LS.",
    )
    svolume_17: int = Field(
        default=0,
        title="외국인순매수",
        description="svolume_17 — long(12). Consume as returned by LS.",
    )
    jjcode_18: str = Field(
        default="",
        title="기관계투자자코드",
        description="jjcode_18 — char(4). Consume as returned by LS.",
    )
    ms_18: int = Field(
        default=0,
        title="기관계매수",
        description="ms_18 — long(12). Consume as returned by LS.",
    )
    md_18: int = Field(
        default=0,
        title="기관계매도",
        description="md_18 — long(12). Consume as returned by LS.",
    )
    rate_18: int = Field(
        default=0,
        title="기관계증감",
        description="rate_18 — long(12). Consume as returned by LS.",
    )
    svolume_18: int = Field(
        default=0,
        title="기관계순매수",
        description="svolume_18 — long(12). Consume as returned by LS.",
    )
    jjcode_01: str = Field(
        default="",
        title="증권투자자코드",
        description="jjcode_01 — char(4). Consume as returned by LS.",
    )
    ms_01: int = Field(
        default=0,
        title="증권매수",
        description="ms_01 — long(12). Consume as returned by LS.",
    )
    md_01: int = Field(
        default=0,
        title="증권매도",
        description="md_01 — long(12). Consume as returned by LS.",
    )
    rate_01: int = Field(
        default=0,
        title="증권증감",
        description="rate_01 — long(12). Consume as returned by LS.",
    )
    svolume_01: int = Field(
        default=0,
        title="증권순매수",
        description="svolume_01 — long(12). Consume as returned by LS.",
    )
    jjcode_03: str = Field(
        default="",
        title="투신투자자코드",
        description="jjcode_03 — char(4). Consume as returned by LS.",
    )
    ms_03: int = Field(
        default=0,
        title="투신매수",
        description="ms_03 — long(12). Consume as returned by LS.",
    )
    md_03: int = Field(
        default=0,
        title="투신매도",
        description="md_03 — long(12). Consume as returned by LS.",
    )
    rate_03: int = Field(
        default=0,
        title="투신증감",
        description="rate_03 — long(12). Consume as returned by LS.",
    )
    svolume_03: int = Field(
        default=0,
        title="투신순매수",
        description="svolume_03 — long(12). Consume as returned by LS.",
    )
    jjcode_04: str = Field(
        default="",
        title="은행투자자코드",
        description="jjcode_04 — char(4). Consume as returned by LS.",
    )
    ms_04: int = Field(
        default=0,
        title="은행매수",
        description="ms_04 — long(12). Consume as returned by LS.",
    )
    md_04: int = Field(
        default=0,
        title="은행매도",
        description="md_04 — long(12). Consume as returned by LS.",
    )
    rate_04: int = Field(
        default=0,
        title="은행증감",
        description="rate_04 — long(12). Consume as returned by LS.",
    )
    svolume_04: int = Field(
        default=0,
        title="은행순매수",
        description="svolume_04 — long(12). Consume as returned by LS.",
    )
    jjcode_02: str = Field(
        default="",
        title="보험투자자코드",
        description="jjcode_02 — char(4). Consume as returned by LS.",
    )
    ms_02: int = Field(
        default=0,
        title="보험매수",
        description="ms_02 — long(12). Consume as returned by LS.",
    )
    md_02: int = Field(
        default=0,
        title="보험매도",
        description="md_02 — long(12). Consume as returned by LS.",
    )
    rate_02: int = Field(
        default=0,
        title="보험증감",
        description="rate_02 — long(12). Consume as returned by LS.",
    )
    svolume_02: int = Field(
        default=0,
        title="보험순매수",
        description="svolume_02 — long(12). Consume as returned by LS.",
    )
    jjcode_05: str = Field(
        default="",
        title="종금투자자코드",
        description="jjcode_05 — char(4). Consume as returned by LS.",
    )
    ms_05: int = Field(
        default=0,
        title="종금매수",
        description="ms_05 — long(12). Consume as returned by LS.",
    )
    md_05: int = Field(
        default=0,
        title="종금매도",
        description="md_05 — long(12). Consume as returned by LS.",
    )
    rate_05: int = Field(
        default=0,
        title="종금증감",
        description="rate_05 — long(12). Consume as returned by LS.",
    )
    svolume_05: int = Field(
        default=0,
        title="종금순매수",
        description="svolume_05 — long(12). Consume as returned by LS.",
    )
    jjcode_06: str = Field(
        default="",
        title="기금투자자코드",
        description="jjcode_06 — char(4). Consume as returned by LS.",
    )
    ms_06: int = Field(
        default=0,
        title="기금매수",
        description="ms_06 — long(12). Consume as returned by LS.",
    )
    md_06: int = Field(
        default=0,
        title="기금매도",
        description="md_06 — long(12). Consume as returned by LS.",
    )
    rate_06: int = Field(
        default=0,
        title="기금증감",
        description="rate_06 — long(12). Consume as returned by LS.",
    )
    svolume_06: int = Field(
        default=0,
        title="기금순매수",
        description="svolume_06 — long(12). Consume as returned by LS.",
    )
    jjcode_07: str = Field(
        default="",
        title="기타투자자코드",
        description="jjcode_07 — char(4). Consume as returned by LS.",
    )
    ms_07: int = Field(
        default=0,
        title="기타매수",
        description="ms_07 — long(12). Consume as returned by LS.",
    )
    md_07: int = Field(
        default=0,
        title="기타매도",
        description="md_07 — long(12). Consume as returned by LS.",
    )
    rate_07: int = Field(
        default=0,
        title="기타증감",
        description="rate_07 — long(12). Consume as returned by LS.",
    )
    svolume_07: int = Field(
        default=0,
        title="기타순매수",
        description="svolume_07 — long(12). Consume as returned by LS.",
    )
    jjcode_11: str = Field(
        default="",
        title="국가투자자코드",
        description="jjcode_11 — char(4). Consume as returned by LS.",
    )
    ms_11: int = Field(
        default=0,
        title="국가매수",
        description="ms_11 — long(12). Consume as returned by LS.",
    )
    md_11: int = Field(
        default=0,
        title="국가매도",
        description="md_11 — long(12). Consume as returned by LS.",
    )
    rate_11: int = Field(
        default=0,
        title="국가증감",
        description="rate_11 — long(12). Consume as returned by LS.",
    )
    svolume_11: int = Field(
        default=0,
        title="국가순매수",
        description="svolume_11 — long(12). Consume as returned by LS.",
    )
    jjcode_00: str = Field(
        default="",
        title="사모펀드코드",
        description="jjcode_00 — char(4). Consume as returned by LS.",
    )
    ms_00: int = Field(
        default=0,
        title="사모펀드매수",
        description="ms_00 — long(12). Consume as returned by LS.",
    )
    md_00: int = Field(
        default=0,
        title="사모펀드매도",
        description="md_00 — long(12). Consume as returned by LS.",
    )
    rate_00: int = Field(
        default=0,
        title="사모펀드증감",
        description="rate_00 — long(12). Consume as returned by LS.",
    )
    svolume_00: int = Field(
        default=0,
        title="사모펀드순매수",
        description="svolume_00 — long(12). Consume as returned by LS.",
    )

class T2541OutBlock1(BaseModel):
    """t2541OutBlock1 — output block (occurs — list of rows). 출력1"""

    time: str = Field(
        default="",
        title="시간",
        description="time — char(8). Consume as returned by LS.",
    )
    sv_08: int = Field(
        default=0,
        title="개인순매수",
        description="sv_08 — long(12). Consume as returned by LS.",
    )
    sv_17: int = Field(
        default=0,
        title="외국인순매수",
        description="sv_17 — long(12). Consume as returned by LS.",
    )
    sv_18: int = Field(
        default=0,
        title="기관계순매수",
        description="sv_18 — long(12). Consume as returned by LS.",
    )
    sv_01: int = Field(
        default=0,
        title="증권순매수",
        description="sv_01 — long(12). Consume as returned by LS.",
    )
    sv_03: int = Field(
        default=0,
        title="투신순매수",
        description="sv_03 — long(12). Consume as returned by LS.",
    )
    sv_04: int = Field(
        default=0,
        title="은행순매수",
        description="sv_04 — long(12). Consume as returned by LS.",
    )
    sv_02: int = Field(
        default=0,
        title="보험순매수",
        description="sv_02 — long(12). Consume as returned by LS.",
    )
    sv_05: int = Field(
        default=0,
        title="종금순매수",
        description="sv_05 — long(12). Consume as returned by LS.",
    )
    sv_06: int = Field(
        default=0,
        title="기금순매수",
        description="sv_06 — long(12). Consume as returned by LS.",
    )
    sv_07: int = Field(
        default=0,
        title="기타순매수",
        description="sv_07 — long(12). Consume as returned by LS.",
    )
    sv_11: int = Field(
        default=0,
        title="국가순매수",
        description="sv_11 — long(12). Consume as returned by LS.",
    )
    sv_00: int = Field(
        default=0,
        title="사모펀드순매수",
        description="sv_00 — long(12). Consume as returned by LS.",
    )

class T2541Request(BaseModel):
    """Request envelope for t2541."""

    header: T2541RequestHeader = T2541RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t2541",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t2541",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T2541Response(BaseModel):
    """Response envelope for t2541."""

    header: Optional[T2541ResponseHeader] = None
    block: Optional[T2541OutBlock] = None
    block1: List[T2541OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T2541RequestHeader",
    "T2541ResponseHeader",
    "T2541InBlock",
    "T2541OutBlock",
    "T2541OutBlock1",
    "T2541Request",
    "T2541Response",
]