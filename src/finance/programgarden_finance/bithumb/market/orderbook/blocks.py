"""빗썸 호가 정보 조회 (GET /v1/orderbook) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class OrderbookInBlock(BaseModel):
    """호가 정보 조회 쿼리 파라미터입니다."""

    markets: str = Field(
        ...,
        title="마켓 코드 목록",
        description="콤마(,)로 구분되는 마켓 코드 (ex. KRW-BTC,KRW-ETH)",
        examples=["KRW-BTC"],
    )


class OrderbookRequest(BaseModel):
    """호가 정보 조회 요청입니다."""

    params: OrderbookInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class OrderbookUnit(BaseModel):
    """호가 단위(매도/매수 1단계) 정보입니다."""

    ask_price: float = Field(..., title="매도 호가", examples=[95600000.0])
    bid_price: float = Field(..., title="매수 호가", examples=[95500000.0])
    ask_size: float = Field(..., title="매도 잔량", examples=[0.1234])
    bid_size: float = Field(..., title="매수 잔량", examples=[0.5678])


class OrderbookOutBlock(BaseModel):
    """호가 정보 조회 응답 항목입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    timestamp: int = Field(..., title="호가 생성 시각(ms)", examples=[1749900896123])
    total_ask_size: float = Field(..., title="호가 매도 총 잔량", examples=[12.345])
    total_bid_size: float = Field(..., title="호가 매수 총 잔량", examples=[23.456])
    orderbook_units: List[OrderbookUnit] = Field(..., title="호가 목록", description="매도/매수 호가 단위 목록")
    level: Optional[int] = Field(default=None, title="호가 모아보기 단위", examples=[0])


class OrderbookResponse(BithumbResponseBase):
    """호가 정보 조회 응답입니다."""

    blocks: Optional[List[OrderbookOutBlock]] = Field(default=None, description="마켓별 호가 정보 목록")
