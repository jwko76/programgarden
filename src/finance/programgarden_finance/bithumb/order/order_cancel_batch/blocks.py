"""빗썸 다건 주문 취소 (POST /v2/orders/cancel) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class OrderCancelBatchInBlock(BaseModel):
    """다건 주문 취소 요청 본문(JSON body)입니다.

    ``order_ids`` 또는 ``client_order_ids`` 중 하나 이상이 필수이며, 둘 다 전달하면
    ``order_ids`` 기준으로 처리됩니다.
    """

    order_ids: Optional[List[str]] = Field(
        default=None, title="취소할 주문의 고유 ID 목록", description="최대 30개"
    )
    client_order_ids: Optional[List[str]] = Field(
        default=None, title="취소할 주문의 클라이언트 지정 ID 목록", description="최대 30개"
    )


class OrderCancelBatchRequest(BaseModel):
    """다건 주문 취소 요청입니다."""

    body: OrderCancelBatchInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class CancelSuccessItem(BaseModel):
    """다건 주문 취소 성공 항목입니다."""

    order_id: str = Field(..., title="주문의 고유 ID", examples=["C0917000000000070001"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")
    created_at: str = Field(..., title="주문 취소 요청 시각", examples=["2024-07-12T16:30:01+09:00"])


class CancelFailError(BaseModel):
    """다건 주문 취소 실패 항목의 에러 정보입니다."""

    name: Optional[str] = Field(default=None, title="에러명", examples=["order_not_found"])
    message: Optional[str] = Field(default=None, title="에러 메시지", examples=["주문을 찾지 못했습니다."])


class CancelFailItem(BaseModel):
    """다건 주문 취소 실패 항목입니다."""

    order_id: Optional[str] = Field(default=None, title="주문의 고유 ID", description="client_order_id로 조회했으나 매칭 실패 시 미반환될 수 있습니다.")
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")
    error: Optional[CancelFailError] = Field(default=None, title="에러 정보")


class OrderCancelBatchOutBlock(BaseModel):
    """다건 주문 취소 응답입니다 (POST /v2/orders/cancel, 200)."""

    success: List[CancelSuccessItem] = Field(default_factory=list, title="취소 성공 목록")
    fail: List[CancelFailItem] = Field(default_factory=list, title="취소 실패 목록")


class OrderCancelBatchResponse(BithumbResponseBase):
    """다건 주문 취소 응답입니다."""

    block: Optional[OrderCancelBatchOutBlock] = Field(default=None, description="다건 주문 취소 결과")
