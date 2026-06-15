"""빗썸 주문하기 (POST /v2/orders) 요청/응답 모델입니다."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class OrderNewInBlock(BaseModel):
    """주문 생성 요청 본문(JSON body)입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    side: Literal["bid", "ask"] = Field(..., title="주문 종류", description="bid(매수)/ask(매도)", examples=["bid"])
    order_type: Literal["limit", "price", "market"] = Field(
        ...,
        title="주문 방식",
        description="limit(지정가)/price(시장가 매수)/market(시장가 매도)",
        examples=["limit"],
    )
    volume: Optional[str] = Field(
        default=None,
        title="주문 수량",
        description="매수/매도하려는 화폐의 양. order_type이 price(시장가 매수)인 경우 비워둡니다.",
        examples=["0.001"],
    )
    price: Optional[str] = Field(
        default=None,
        title="주문 가격",
        description="order_type이 limit(지정가) 또는 price(시장가 매수)인 경우 필수입니다.",
        examples=["50000000"],
    )
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정하는 주문 식별자")


class OrderNewRequest(BaseModel):
    """주문 생성 요청입니다."""

    body: OrderNewInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class OrderNewOutBlock(BaseModel):
    """주문 생성 응답입니다 (POST /v2/orders, 201)."""

    order_id: str = Field(..., title="주문의 고유 ID", examples=["C0101000000001799653"])
    market: str = Field(..., title="마켓의 유일 키", examples=["KRW-BTC"])
    side: str = Field(..., title="주문 종류", description="bid(매수)/ask(매도)", examples=["bid"])
    order_type: str = Field(..., title="주문 방식", description="limit/price/market", examples=["limit"])
    created_at: str = Field(..., title="주문 생성 시각", examples=["2024-07-14T13:35:41+09:00"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")
    stp_type: Optional[str] = Field(default=None, title="자전거래 방지 처리 유형", examples=["cancel_taker"])


class OrderNewResponse(BithumbResponseBase):
    """주문 생성 응답입니다."""

    block: Optional[OrderNewOutBlock] = Field(default=None, description="생성된 주문 정보")
