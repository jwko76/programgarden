"""빗썸 다건 주문 (POST /v2/orders/batch) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class BatchOrderItem(BaseModel):
    """다건 주문 요청에 포함되는 개별 주문입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    side: Literal["bid", "ask"] = Field(..., title="주문 종류", description="bid(매수)/ask(매도)", examples=["bid"])
    order_type: Literal["limit", "price", "market"] = Field(
        ...,
        title="주문 방식",
        description="limit(지정가)/price(시장가 매수)/market(시장가 매도)",
        examples=["limit"],
    )
    price: Optional[str] = Field(
        default=None,
        title="주문 가격",
        description="order_type이 limit(지정가) 또는 price(시장가 매수)인 경우 필수입니다.",
        examples=["50000000"],
    )
    volume: Optional[str] = Field(
        default=None,
        title="주문 수량",
        description="order_type이 limit(지정가) 또는 market(시장가 매도)인 경우 필수입니다.",
        examples=["0.001"],
    )
    client_order_id: Optional[str] = Field(
        default=None,
        title="클라이언트가 지정하는 주문 식별자",
        description="1~36자의 영문/숫자/-/_",
    )


class OrderNewBatchInBlock(BaseModel):
    """다건 주문 요청 본문(JSON body)입니다."""

    batch_orders: List[BatchOrderItem] = Field(
        ..., title="주문 목록", description="최소 1건, 최대 20건"
    )


class OrderNewBatchRequest(BaseModel):
    """다건 주문 요청입니다."""

    body: OrderNewBatchInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class BatchOrderResultItem(BaseModel):
    """다건 주문 처리 결과 항목입니다 (성공 시 order_id, 실패 시 name/message가 채워집니다)."""

    order_id: Optional[str] = Field(default=None, title="서버가 부여한 주문의 고유 ID", examples=["C0101000007410713262"])
    market: Optional[str] = Field(default=None, title="마켓 코드", examples=["KRW-BTC"])
    side: Optional[str] = Field(default=None, title="주문 종류", description="bid/ask")
    order_type: Optional[str] = Field(default=None, title="주문 방식", description="limit/price/market")
    created_at: Optional[str] = Field(default=None, title="주문 생성 시각", examples=["2026-01-06T12:08:11+09:00"])
    stp_type: Optional[str] = Field(default=None, title="자전거래 방지 처리 유형", examples=["cancel_taker"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")
    name: Optional[str] = Field(default=None, title="에러명(실패 시)", examples=["cross_trading"])
    message: Optional[str] = Field(default=None, title="에러 메시지(실패 시)")


class OrderNewBatchOutBlock(BaseModel):
    """다건 주문 응답입니다 (POST /v2/orders/batch, 200)."""

    batch_orders_response: List[BatchOrderResultItem] = Field(
        default_factory=list, title="각 주문의 처리 결과 목록"
    )


class OrderNewBatchResponse(BithumbResponseBase):
    """다건 주문 응답입니다."""

    block: Optional[OrderNewBatchOutBlock] = Field(default=None, description="다건 주문 처리 결과")
