"""빗썸 개별 주문 조회 (GET /v1/order) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions
from .._common import OrderOutBlock, OrderTrade


class OrderDetailInBlock(BaseModel):
    """개별 주문 조회 쿼리 파라미터입니다. uuid 또는 client_order_id 중 하나는 필수입니다."""

    uuid: Optional[str] = Field(default=None, title="주문 UUID", examples=["9e8f8eba-7050-4837-82c3-768e2e63b58a"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")


class OrderDetailRequest(BaseModel):
    """개별 주문 조회 요청입니다."""

    params: OrderDetailInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class OrderDetailOutBlock(OrderOutBlock):
    """개별 주문 조회 응답입니다."""

    trades: List[OrderTrade] = Field(default_factory=list, title="체결 내역 목록")


class OrderDetailResponse(BithumbResponseBase):
    """개별 주문 조회 응답입니다."""

    block: Optional[OrderDetailOutBlock] = Field(default=None, description="주문 상세 정보")
