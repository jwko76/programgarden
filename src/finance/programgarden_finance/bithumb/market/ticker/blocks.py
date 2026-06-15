"""빗썸 현재가 조회 (GET /v1/ticker) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class TickerInBlock(BaseModel):
    """현재가 조회 쿼리 파라미터입니다."""

    markets: str = Field(
        ...,
        title="마켓 코드 목록",
        description="콤마(,)로 구분되는 마켓 코드 (ex. KRW-BTC,KRW-ETH)",
        examples=["KRW-BTC,KRW-ETH"],
    )


class TickerRequest(BaseModel):
    """현재가 조회 요청입니다."""

    params: TickerInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class TickerOutBlock(BaseModel):
    """현재가 조회 응답 항목입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    trade_date: str = Field(..., title="최근 거래 일자(UTC)", description="yyyyMMdd", examples=["20260614"])
    trade_time: str = Field(..., title="최근 거래 시각(UTC)", description="HHmmss", examples=["123456"])
    trade_date_kst: str = Field(..., title="최근 거래 일자(KST)", description="yyyyMMdd", examples=["20260614"])
    trade_time_kst: str = Field(..., title="최근 거래 시각(KST)", description="HHmmss", examples=["213456"])
    trade_timestamp: int = Field(..., title="최근 거래 일시(KST, ms)", examples=[1749900896000])
    opening_price: float = Field(..., title="시가", examples=[95000000.0])
    high_price: float = Field(..., title="고가", examples=[96000000.0])
    low_price: float = Field(..., title="저가", examples=[94000000.0])
    trade_price: float = Field(..., title="현재가(종가)", examples=[95500000.0])
    prev_closing_price: float = Field(..., title="전일 종가", examples=[94800000.0])
    change: str = Field(..., title="변화 방향", description="RISE(상승)/EVEN(보합)/FALL(하락)", examples=["RISE"])
    change_price: float = Field(..., title="변화액의 절대값", examples=[700000.0])
    change_rate: float = Field(..., title="변화율의 절대값", examples=[0.00738])
    signed_change_price: float = Field(..., title="부호가 있는 변화액", examples=[700000.0])
    signed_change_rate: float = Field(..., title="부호가 있는 변화율", examples=[0.00738])
    trade_volume: float = Field(..., title="최근 거래량", examples=[0.0123])
    acc_trade_price: float = Field(..., title="누적 거래금액(UTC 0시 기준)", examples=[12345678900.0])
    acc_trade_price_24h: float = Field(..., title="24시간 누적 거래금액", examples=[23456789000.0])
    acc_trade_volume: float = Field(..., title="누적 거래량(UTC 0시 기준)", examples=[123.456])
    acc_trade_volume_24h: float = Field(..., title="24시간 누적 거래량", examples=[234.567])
    highest_52_week_price: float = Field(..., title="52주 최고가", examples=[100000000.0])
    highest_52_week_date: str = Field(..., title="52주 최고가 달성일", description="yyyy-MM-dd", examples=["2025-12-01"])
    lowest_52_week_price: float = Field(..., title="52주 최저가", examples=[40000000.0])
    lowest_52_week_date: str = Field(..., title="52주 최저가 달성일", description="yyyy-MM-dd", examples=["2025-01-15"])
    timestamp: int = Field(..., title="타임스탬프(ms)", examples=[1749900896123])


class TickerResponse(BithumbResponseBase):
    """현재가 조회 응답입니다."""

    blocks: Optional[List[TickerOutBlock]] = Field(default=None, description="마켓별 현재가 정보 목록")
