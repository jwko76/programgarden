"""빗썸 실시간 호가(orderbook) WebSocket 응답 모델입니다.

빗썸 공개 WebSocket ``wss://pubwss.bithumb.com/pub/ws`` 에서
``{"type": "orderbook", "codes": [...]}`` 구독 후 수신하는 push 메시지의
Pydantic 모델입니다. 호가창 변경마다 전체 스냅샷을 전송합니다.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class OrderbookRealUnit(BaseModel):
    """호가 단위(매도/매수 1단계) 정보입니다."""

    ask_price: float = Field(
        ...,
        title="매도 호가",
        examples=[95600000.0],
    )
    bid_price: float = Field(
        ...,
        title="매수 호가",
        examples=[95500000.0],
    )
    ask_size: float = Field(
        ...,
        title="매도 잔량",
        examples=[0.1234],
    )
    bid_size: float = Field(
        ...,
        title="매수 잔량",
        examples=[0.5678],
    )


class OrderbookRealResponse(BaseModel):
    """빗썸 WebSocket 실시간 호가(orderbook) push 응답입니다."""

    type: str = Field(
        ...,
        title="스트림 타입",
        description="항상 'orderbook'.",
        examples=["orderbook"],
    )
    code: str = Field(
        ...,
        title="마켓 코드",
        description="빗썸 마켓 코드 (ex. KRW-BTC).",
        examples=["KRW-BTC"],
    )
    timestamp: int = Field(
        ...,
        title="호가 생성 시각(ms)",
        examples=[1750334400123],
    )
    total_ask_size: float = Field(
        ...,
        title="호가 매도 총 잔량",
        examples=[10.5],
    )
    total_bid_size: float = Field(
        ...,
        title="호가 매수 총 잔량",
        examples=[15.2],
    )
    orderbook_units: List[OrderbookRealUnit] = Field(
        ...,
        title="호가 목록",
        description="매도/매수 호가 단위 목록 (매도 낮은 가격 순).",
    )
    stream_type: str = Field(
        ...,
        title="스트림 데이터 타입",
        description="REALTIME / SNAPSHOT.",
        examples=["REALTIME"],
    )
    level: Optional[float] = Field(
        default=None,
        title="호가 모아보기 단위",
        description="0이면 기본 단위. 빗썸이 설정한 호가 단위.",
        examples=[0.0],
    )
    error_msg: Optional[str] = Field(
        default=None,
        title="파싱 오류 메시지",
        description="모델 파싱 실패 시 오류 내용. 정상 수신 시 None.",
    )
