"""빗썸 실시간 현재가(ticker) WebSocket 응답 모델입니다.

빗썸 공개 WebSocket ``wss://pubwss.bithumb.com/pub/ws`` 에서
``{"type": "ticker", "codes": [...]}`` 구독 후 수신하는 push 메시지의
Pydantic 모델입니다.

REST API의 ``TickerOutBlock``(``/v1/ticker``)과 필드 구성이 유사하나
실시간 push 전용 필드(``ask_bid``, ``stream_type``)가 추가됩니다.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TickerRealResponse(BaseModel):
    """빗썸 WebSocket 실시간 현재가(ticker) push 응답입니다."""

    type: str = Field(
        ...,
        title="스트림 타입",
        description="항상 'ticker'.",
        examples=["ticker"],
    )
    code: str = Field(
        ...,
        title="마켓 코드",
        description="빗썸 마켓 코드 (ex. KRW-BTC).",
        examples=["KRW-BTC"],
    )
    opening_price: float = Field(
        ...,
        title="시가",
        description="당일 시가.",
        examples=[95000000.0],
    )
    high_price: float = Field(
        ...,
        title="고가",
        description="당일 고가.",
        examples=[96000000.0],
    )
    low_price: float = Field(
        ...,
        title="저가",
        description="당일 저가.",
        examples=[94000000.0],
    )
    trade_price: float = Field(
        ...,
        title="현재가(최근 체결가)",
        description="가장 최근 체결 가격.",
        examples=[95500000.0],
    )
    prev_closing_price: float = Field(
        ...,
        title="전일 종가",
        description="전 거래일 종가.",
        examples=[94800000.0],
    )
    acc_trade_price: float = Field(
        ...,
        title="누적 거래금액(UTC 0시 기준)",
        examples=[12345678900.0],
    )
    change: str = Field(
        ...,
        title="변화 방향",
        description="RISE(상승) / EVEN(보합) / FALL(하락).",
        examples=["RISE"],
    )
    change_price: float = Field(
        ...,
        title="변화액 절대값",
        examples=[700000.0],
    )
    signed_change_price: float = Field(
        ...,
        title="부호가 있는 변화액",
        examples=[700000.0],
    )
    change_rate: float = Field(
        ...,
        title="변화율 절대값",
        examples=[0.00738],
    )
    signed_change_rate: float = Field(
        ...,
        title="부호가 있는 변화율",
        examples=[0.00738],
    )
    ask_bid: str = Field(
        ...,
        title="매수/매도 구분",
        description="ASK(매도) / BID(매수). 직전 체결 방향.",
        examples=["BID"],
    )
    trade_volume: float = Field(
        ...,
        title="최근 거래량",
        description="직전 체결의 거래량.",
        examples=[0.0123],
    )
    acc_trade_volume: float = Field(
        ...,
        title="누적 거래량(UTC 0시 기준)",
        examples=[123.456],
    )
    trade_date: str = Field(
        ...,
        title="최근 거래 일자(UTC)",
        description="yyyyMMdd 형식.",
        examples=["20260619"],
    )
    trade_time: str = Field(
        ...,
        title="최근 거래 시각(UTC)",
        description="HHmmss 형식.",
        examples=["123456"],
    )
    trade_timestamp: int = Field(
        ...,
        title="최근 거래 일시(ms, KST)",
        examples=[1750334400000],
    )
    acc_ask_volume: float = Field(
        ...,
        title="누적 매도 거래량",
        examples=[60.0],
    )
    acc_bid_volume: float = Field(
        ...,
        title="누적 매수 거래량",
        examples=[63.456],
    )
    highest_52_week_price: float = Field(
        ...,
        title="52주 최고가",
        examples=[120000000.0],
    )
    highest_52_week_date: str = Field(
        ...,
        title="52주 최고가 달성일",
        description="yyyy-MM-dd 형식.",
        examples=["2025-12-01"],
    )
    lowest_52_week_price: float = Field(
        ...,
        title="52주 최저가",
        examples=[60000000.0],
    )
    lowest_52_week_date: str = Field(
        ...,
        title="52주 최저가 달성일",
        description="yyyy-MM-dd 형식.",
        examples=["2025-08-15"],
    )
    market_state: str = Field(
        ...,
        title="마켓 거래 상태",
        description="ACTIVE / PREVIEW / DELISTED 등.",
        examples=["ACTIVE"],
    )
    is_trading_suspended: bool = Field(
        ...,
        title="거래 정지 여부",
        examples=[False],
    )
    delisting_date: Optional[str] = Field(
        default=None,
        title="상장 폐지일",
        description="상장 폐지 예정일. 없으면 null.",
        examples=[None],
    )
    market_warning: str = Field(
        ...,
        title="투자유의 구분",
        description="NONE / CAUTION.",
        examples=["NONE"],
    )
    timestamp: int = Field(
        ...,
        title="타임스탬프(ms)",
        description="서버 기준 현재 시각(ms).",
        examples=[1750334400123],
    )
    acc_trade_price_24h: float = Field(
        ...,
        title="24시간 누적 거래금액",
        examples=[23456789000.0],
    )
    acc_trade_volume_24h: float = Field(
        ...,
        title="24시간 누적 거래량",
        examples=[234.567],
    )
    stream_type: str = Field(
        ...,
        title="스트림 데이터 타입",
        description="REALTIME(실시간) / SNAPSHOT(초기 스냅샷).",
        examples=["REALTIME"],
    )
    error_msg: Optional[str] = Field(
        default=None,
        title="파싱 오류 메시지",
        description="모델 파싱 실패 시 오류 내용. 정상 수신 시 None.",
    )
