"""Pydantic models for LS Securities OpenAPI t8409 (API용 업종차트 분).

t8409 returns minute/n-minute chart data for a domestic sector/industry index.
Replaces t8418 from 2026-06-29 (field precision expanded: 7.2 → 10.2).

Response structure:
    - ``OutBlock`` (``block``) — chart metadata: previous-day / today's OHLCV,
      continuation keys, session timing, today's trade value.
    - ``OutBlock1`` (``block1``) — list of minute bar rows (date, time, OHLCV, value).
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8409RequestHeader(BlockRequestHeader):
    pass


class T8409ResponseHeader(BlockResponseHeader):
    pass


class T8409InBlock(BaseModel):
    """t8409InBlock — input for sector minute/n-minute chart query."""

    shcode: str = Field(
        ...,
        title="단축코드 (Sector short code)",
        description="3-char sector/industry code. e.g. '001'=KOSPI, '101'=KOSPI200, '501'=KOSDAQ.",
        examples=["001", "101"],
    )
    ncnt: int = Field(
        default=1,
        title="단위(n분) (Minute unit)",
        description="Aggregation unit in minutes. 1 = 1-minute bars, 5 = 5-minute bars, etc.",
        examples=[1, 3, 5, 10, 30, 60],
    )
    qrycnt: int = Field(
        default=500,
        title="요청건수 (Row count)",
        description="Number of rows requested. Max 2000 (compressed) / 500 (uncompressed).",
        examples=[500],
    )
    nday: str = Field(
        default="0",
        title="조회영업일수 (Trading-day lookback)",
        description="'0' = not used; '1' or greater = include data from that many prior sessions.",
        examples=["0"],
    )
    sdate: str = Field(default="", title="시작일자 (Start date YYYYMMDD)", examples=["20260101"])
    stime: str = Field(default="", title="시작시간 (Start time, currently unused)", examples=["090000"])
    edate: str = Field(default="", title="종료일자 (End date YYYYMMDD)", examples=["20261231"])
    etime: str = Field(default="", title="종료시간 (End time, currently unused)", examples=["153000"])
    cts_date: str = Field(default="", title="연속일자 (Continuation date)", examples=[""])
    cts_time: str = Field(default="", title="연속시간 (Continuation time)", examples=[""])
    comp_yn: Literal["Y", "N"] = Field(
        default="Y",
        title="압축여부 (Compression flag)",
        description="'Y' = compressed (up to 2000 rows); 'N' = uncompressed (up to 500 rows).",
        examples=["Y"],
    )


class T8409OutBlock(BaseModel):
    """t8409OutBlock — chart metadata and session summary."""

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
    cts_time: str = Field(default="", title="연속시간 (Continuation time key)")
    s_time: str = Field(default="", title="업종시작시간 HHMMSS (Session start time)", examples=["090000"])
    e_time: str = Field(default="", title="업종종료시간 HHMMSS (Session end time)", examples=["153000"])
    dshmin: str = Field(default="", title="동시호가처리시간 MM분 (Auction window minutes)", examples=["10"])
    rec_count: int = Field(default=0, title="레코드카운트 (Record count)")


class T8409OutBlock1(BaseModel):
    """t8409OutBlock1 — one minute/n-minute bar row."""

    date: str = Field(default="", title="날짜 (Date YYYYMMDD)", examples=["20260620"])
    time: str = Field(default="", title="시간 (Time HHMMSS)", examples=["091500"])
    open: float = Field(default=0.0, title="시가 (Open index)", examples=[2762.00])
    high: float = Field(default=0.0, title="고가 (High index)", examples=[2765.00])
    low: float = Field(default=0.0, title="저가 (Low index)", examples=[2760.00])
    close: float = Field(default=0.0, title="종가 (Close index)", examples=[2763.50])
    jdiff_vol: int = Field(default=0, title="거래량 (Volume)", examples=[1500000])
    value: int = Field(default=0, title="거래대금 (Trade value, KRW)", examples=[3200000000])


class T8409Request(BaseModel):
    """t8409 request envelope."""

    header: T8409RequestHeader = T8409RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8409",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8409",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)


class T8409Response(BaseModel):
    """t8409 response envelope."""

    header: Optional[T8409ResponseHeader] = None
    block: Optional[T8409OutBlock] = None
    block1: List[T8409OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None


__all__ = [
    "T8409RequestHeader",
    "T8409ResponseHeader",
    "T8409InBlock",
    "T8409OutBlock",
    "T8409OutBlock1",
    "T8409Request",
    "T8409Response",
]
