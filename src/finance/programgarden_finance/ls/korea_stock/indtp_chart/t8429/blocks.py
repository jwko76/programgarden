"""Pydantic models for LS Securities OpenAPI t8429 (API용 업종차트 일/주/월).

t8429 returns daily/weekly/monthly chart data for a domestic sector/industry index.
Replaces t8419 from 2026-06-29 (field precision expanded: 7.2 → 10.2).

Response structure:
    - ``OutBlock`` (``block``) — chart metadata: previous-day / today's OHLCV,
      continuation key, session timing, today's trade value.
    - ``OutBlock1`` (``block1``) — list of period bar rows (date, OHLCV, value).
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8429RequestHeader(BlockRequestHeader):
    pass


class T8429ResponseHeader(BlockResponseHeader):
    pass


class T8429InBlock(BaseModel):
    """t8429InBlock — input for sector daily/weekly/monthly chart query."""

    shcode: str = Field(
        ...,
        title="단축코드 (Sector short code)",
        description="3-char sector/industry code. e.g. '001'=KOSPI, '101'=KOSPI200, '501'=KOSDAQ.",
        examples=["001", "101", "501"],
    )
    gubun: Literal["2", "3", "4"] = Field(
        default="2",
        title="주기구분 (Period type)",
        description="'2'=daily, '3'=weekly, '4'=monthly.",
        examples=["2", "3", "4"],
    )
    qrycnt: int = Field(
        default=500,
        title="요청건수 (Row count)",
        description="Number of rows requested. Max 2000 (compressed) / 500 (uncompressed).",
        examples=[500],
    )
    sdate: str = Field(default="", title="시작일자 (Start date YYYYMMDD)", examples=["20250101"])
    edate: str = Field(default="", title="종료일자 (End date YYYYMMDD)", examples=["20261231"])
    cts_date: str = Field(default="", title="연속일자 (Continuation date)", examples=[""])
    comp_yn: Literal["Y", "N"] = Field(
        default="Y",
        title="압축여부 (Compression flag)",
        description="'Y' = compressed (up to 2000 rows); 'N' = uncompressed (up to 500 rows).",
        examples=["Y"],
    )


class T8429OutBlock(BaseModel):
    """t8429OutBlock — chart metadata and session summary."""

    shcode: str = Field(default="", title="단축코드 (Sector code)")
    jisiga: float = Field(default=0.0, title="전일시가 (Previous-day open index)", examples=[2750.50])
    jihigh: float = Field(default=0.0, title="전일고가 (Previous-day high index)", examples=[2780.30])
    jilow: float = Field(default=0.0, title="전일저가 (Previous-day low index)", examples=[2740.10])
    jiclose: float = Field(default=0.0, title="전일종가 (Previous-day close index)", examples=[2760.00])
    jivolume: int = Field(default=0, title="전일거래량 (Previous-day volume)", examples=[500000000])
    disiga: float = Field(default=0.0, title="당일시가 (Today's open index)", examples=[2762.00])
    dihigh: float = Field(default=0.0, title="당일고가 (Today's high index)", examples=[2790.00])
    dilow: float = Field(default=0.0, title="당일저가 (Today's low index)", examples=[2755.00])
    diclose: float = Field(default=0.0, title="당일종가 (Today's last index)", examples=[2775.00])
    disvalue: int = Field(default=0, title="당일거래대금 (Today's trade value, KRW)", examples=[8500000000000])
    cts_date: str = Field(default="", title="연속일자 (Continuation date key)")
    s_time: str = Field(default="", title="업종시작시간 (Session start time HHMMSS)", examples=["090000"])
    e_time: str = Field(default="", title="업종종료시간 (Session end time HHMMSS)", examples=["153000"])
    dshmin: str = Field(default="", title="동시호가처리시간 MM분 (Auction window minutes)", examples=["10"])
    rec_count: int = Field(default=0, title="레코드카운트 (Record count)")


class T8429OutBlock1(BaseModel):
    """t8429OutBlock1 — one daily/weekly/monthly bar row."""

    date: str = Field(default="", title="날짜 (Date YYYYMMDD)", examples=["20260620"])
    open: float = Field(default=0.0, title="시가 (Open index)", examples=[2762.00])
    high: float = Field(default=0.0, title="고가 (High index)", examples=[2790.00])
    low: float = Field(default=0.0, title="저가 (Low index)", examples=[2755.00])
    close: float = Field(default=0.0, title="종가 (Close index)", examples=[2775.00])
    jdiff_vol: int = Field(default=0, title="거래량 (Volume)", examples=[500000000])
    value: int = Field(default=0, title="거래대금 (Trade value, KRW)", examples=[8500000000000])


class T8429Request(BaseModel):
    """t8429 request envelope."""

    header: T8429RequestHeader = T8429RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8429",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8429",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)


class T8429Response(BaseModel):
    """t8429 response envelope."""

    header: Optional[T8429ResponseHeader] = None
    block: Optional[T8429OutBlock] = None
    block1: List[T8429OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None


__all__ = [
    "T8429RequestHeader",
    "T8429ResponseHeader",
    "T8429InBlock",
    "T8429OutBlock",
    "T8429OutBlock1",
    "T8429Request",
    "T8429Response",
]
