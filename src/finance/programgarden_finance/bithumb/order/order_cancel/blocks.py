"""빗썸 주문 취소 (DELETE /v2/order) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class OrderCancelInBlock(BaseModel):
    """주문 취소 쿼리 파라미터입니다. order_id 또는 client_order_id 중 하나는 필수입니다."""

    order_id: Optional[str] = Field(default=None, title="취소할 주문의 고유 ID", examples=["C0101000000001799625"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")


class OrderCancelRequest(BaseModel):
    """주문 취소 요청입니다."""

    params: OrderCancelInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class OrderCancelOutBlock(BaseModel):
    """주문 취소 응답입니다 (DELETE /v2/order, 200)."""

    order_id: str = Field(..., title="주문의 고유 ID", examples=["C0101000000001799625"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")
    created_at: str = Field(..., title="주문 생성 시각", examples=["2024-07-12T16:30:01+09:00"])


class OrderCancelResponse(BithumbResponseBase):
    """주문 취소 응답입니다."""

    block: Optional[OrderCancelOutBlock] = Field(default=None, description="취소된 주문 정보")
