"""빗썸 실시간 체결(trade) WebSocket 응답 모델입니다.

빗썸 공개 WebSocket ``wss://pubwss.bithumb.com/pub/ws`` 에서
``{"type": "trade", "codes": [...]}`` 구독 후 수신하는 push 메시지의
Pydantic 모델입니다. 개별 체결 틱마다 발생합니다.
"""

from typing import Optional

from pydantic import BaseModel, Field


class TradeRealResponse(BaseModel):
    """빗썸 WebSocket 실시간 체결(trade) push 응답입니다."""

    type: str = Field(
        ...,
        title="스트림 타입",
        description="항상 'trade'.",
        examples=["trade"],
    )
    code: str = Field(
        ...,
        title="마켓 코드",
        description="빗썸 마켓 코드 (ex. KRW-BTC).",
        examples=["KRW-BTC"],
    )
    trade_price: float = Field(
        ...,
        title="체결가",
        description="해당 체결 틱의 체결 가격.",
        examples=[95500000.0],
    )
    trade_volume: float = Field(
        ...,
        title="체결량",
        description="해당 체결 틱의 체결 수량.",
        examples=[0.0123],
    )
    ask_bid: str = Field(
        ...,
        title="매수/매도 구분",
        description="ASK(매도 체결) / BID(매수 체결).",
        examples=["BID"],
    )
    prev_closing_price: float = Field(
        ...,
        title="전일 종가",
        examples=[94800000.0],
    )
    change: str = Field(
        ...,
        title="변화 방향",
        description="RISE / EVEN / FALL.",
        examples=["RISE"],
    )
    change_price: float = Field(
        ...,
        title="변화액 절대값",
        examples=[700000.0],
    )
    trade_date: str = Field(
        ...,
        title="체결 일자(UTC)",
        description="yyyyMMdd 형식.",
        examples=["20260619"],
    )
    trade_time: str = Field(
        ...,
        title="체결 시각(UTC)",
        description="HHmmss 형식.",
        examples=["123456"],
    )
    trade_timestamp: int = Field(
        ...,
        title="체결 일시(ms, KST)",
        examples=[1750334400000],
    )
    timestamp: int = Field(
        ...,
        title="서버 타임스탬프(ms)",
        examples=[1750334400123],
    )
    sequential_id: int = Field(
        ...,
        title="체결 번호",
        description="체결의 고유 순번. 오름차순.",
        examples=[1234567890123456789],
    )
    stream_type: str = Field(
        ...,
        title="스트림 데이터 타입",
        description="REALTIME / SNAPSHOT.",
        examples=["REALTIME"],
    )
    error_msg: Optional[str] = Field(
        default=None,
        title="파싱 오류 메시지",
        description="모델 파싱 실패 시 오류 내용. 정상 수신 시 None.",
    )
