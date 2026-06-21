"""Pydantic models for LS Securities OpenAPI t8408 (API용 업종차트 틱/n틱).

t8408 returns tick/n-tick chart data for a domestic sector/industry index.
Replaces t8417 from 2026-06-29 (field precision expanded: 7.2 → 10.2).

Response structure:
    - ``OutBlock`` (``block``) — chart metadata: previous-day / today's OHLCV
      for the index, continuation keys, session timing.
    - ``OutBlock1`` (``block1``) — list of tick rows (date, time, OHLCV).

InBlock key field:
    - ``shcode``: 3-char sector code (e.g. "001" = KOSPI composite,
      "101" = KOSPI200, "501" = KOSDAQ composite).
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8408RequestHeader(BlockRequestHeader):
    pass


class T8408ResponseHeader(BlockResponseHeader):
    pass


class T8408InBlock(BaseModel):
    """t8408InBlock — input for sector tick/n-tick chart query."""

    shcode: str = Field(
        ...,
        title="단축코드 (Sector short code)",
        description="3-char sector/industry code. e.g. '001' = KOSPI, '101' = KOSPI200, '501' = KOSDAQ.",
        examples=["001", "101", "501"],
    )
    ncnt: int = Field(
        default=1,
        title="단위(n틱) (Tick unit)",
        description="Aggregation unit in ticks. 1 = raw tick, N = N-tick bars.",
        examples=[1, 3, 5],
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
        examples=["0", "1"],
    )
    sdate: str = Field(
        default="",
        title="시작일자 (Start date)",
        description="Start date in YYYYMMDD format.",
        examples=["20260101"],
    )
    stime: str = Field(
        default="",
        title="시작시간 (Start time, currently unused)",
        description="Start time HHMMSS. Currently unused by LS.",
        examples=["090000"],
    )
    edate: str = Field(
        default="",
        title="종료일자 (End date)",
        description="End date in YYYYMMDD format.",
        examples=["20261231"],
    )
    etime: str = Field(
        default="",
        title="종료시간 (End time, currently unused)",
        description="End time HHMMSS. Currently unused by LS.",
        examples=["153000"],
    )
    cts_date: str = Field(
        default="",
        title="연속일자 (Continuation date)",
        description="Continuation cursor date. Pass back verbatim from the previous response for paging.",
        examples=[""],
    )
    cts_time: str = Field(
        default="",
        title="연속시간 (Continuation time)",
        description="Continuation cursor time. Pass back verbatim from the previous response for paging.",
        examples=[""],
    )
    comp_yn: Literal["Y", "N"] = Field(
        default="Y",
        title="압축여부 (Compression flag)",
        description="'Y' = compressed response (up to 2000 rows); 'N' = uncompressed (up to 500 rows).",
        examples=["Y"],
    )


class T8408OutBlock(BaseModel):
    """t8408OutBlock — chart metadata and session summary."""

    shcode: str = Field(default="", title="단축코드 (Sector code)", description="Echoed sector short code.")
    jisiga: float = Field(default=0.0, title="전일시가 (Previous-day open index)", description="Previous session's opening index value.", examples=[2750.50])
    jihigh: float = Field(default=0.0, title="전일고가 (Previous-day high index)", examples=[2780.30])
    jilow: float = Field(default=0.0, title="전일저가 (Previous-day low index)", examples=[2740.10])
    jiclose: float = Field(default=0.0, title="전일종가 (Previous-day close index)", examples=[2760.00])
    jivolume: int = Field(default=0, title="전일거래량 (Previous-day volume)", examples=[500000000])
    disiga: float = Field(default=0.0, title="당일시가 (Today's open index)", examples=[2762.00])
    dihigh: float = Field(default=0.0, title="당일고가 (Today's high index)", examples=[2790.00])
    dilow: float = Field(default=0.0, title="당일저가 (Today's low index)", examples=[2755.00])
    diclose: float = Field(default=0.0, title="당일종가 (Today's last index)", examples=[2775.00])
    cts_date: str = Field(default="", title="연속일자 (Continuation date key)", examples=[""])
    cts_time: str = Field(default="", title="연속시간 (Continuation time key)", examples=[""])
    s_time: str = Field(default="", title="장시작시간 HHMMSS (Session start time)", examples=["090000"])
    e_time: str = Field(default="", title="장종료시간 HHMMSS (Session end time)", examples=["153000"])
    dshmin: str = Field(default="", title="동시호가처리시간 MM분 (Auction window minutes)", examples=["10"])
    rec_count: int = Field(default=0, title="레코드카운트 (Record count)", examples=[200])


class T8408OutBlock1(BaseModel):
    """t8408OutBlock1 — one tick/n-tick bar row."""

    date: str = Field(default="", title="날짜 (Date)", description="Bar date YYYYMMDD.", examples=["20260620"])
    time: str = Field(default="", title="시간 (Time)", description="Bar time HHMMSS.", examples=["091530"])
    open: float = Field(default=0.0, title="시가 (Open index)", examples=[2762.00])
    high: float = Field(default=0.0, title="고가 (High index)", examples=[2765.00])
    low: float = Field(default=0.0, title="저가 (Low index)", examples=[2760.00])
    close: float = Field(default=0.0, title="종가 (Close index)", examples=[2763.50])
    jdiff_vol: int = Field(default=0, title="거래량 (Volume)", examples=[1500000])


class T8408Request(BaseModel):
    """t8408 request envelope."""

    header: T8408RequestHeader = T8408RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8408",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8408",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)


class T8408Response(BaseModel):
    """t8408 response envelope."""

    header: Optional[T8408ResponseHeader] = None
    block: Optional[T8408OutBlock] = None
    block1: List[T8408OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None


__all__ = [
    "T8408RequestHeader",
    "T8408ResponseHeader",
    "T8408InBlock",
    "T8408OutBlock",
    "T8408OutBlock1",
    "T8408Request",
    "T8408Response",
]
