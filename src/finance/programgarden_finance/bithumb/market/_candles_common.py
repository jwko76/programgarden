"""캔들(분/일/주/월) 조회 모듈에서 공통으로 사용하는 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field


class CandlesQueryInBlock(BaseModel):
    """캔들 조회 공통 쿼리 파라미터입니다."""

    market: str = Field(..., title="마켓 코드", description="ex. KRW-BTC", examples=["KRW-BTC"])
    to: Optional[str] = Field(
        default=None,
        title="마지막 캔들 시각(exclusive)",
        description="ISO8601 형식 또는 'yyyy-MM-dd HH:mm:ss'. 비워서 요청 시 가장 최근 캔들 기준",
        examples=["2026-06-14 00:00:00"],
    )
    count: Optional[int] = Field(
        default=None, title="캔들 개수", description="최대 200개", examples=[200]
    )


class CandleBaseOutBlock(BaseModel):
    """캔들 조회 응답의 공통 필드입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    candle_date_time_utc: str = Field(..., title="캔들 기준 시각(UTC)", examples=["2026-06-14T00:00:00"])
    candle_date_time_kst: str = Field(..., title="캔들 기준 시각(KST)", examples=["2026-06-14T09:00:00"])
    opening_price: float = Field(..., title="시가", examples=[95000000.0])
    high_price: float = Field(..., title="고가", examples=[96000000.0])
    low_price: float = Field(..., title="저가", examples=[94000000.0])
    trade_price: float = Field(..., title="종가", examples=[95500000.0])
    timestamp: int = Field(..., title="해당 캔들에서 마지막 틱이 저장된 시각(ms)", examples=[1749868800000])
    candle_acc_trade_price: float = Field(..., title="누적 거래 금액", examples=[1234567890.0])
    candle_acc_trade_volume: float = Field(..., title="누적 거래량", examples=[12.345])
