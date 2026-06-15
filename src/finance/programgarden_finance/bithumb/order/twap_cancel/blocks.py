"""빗썸 TWAP 주문 취소 (DELETE /v1/twap) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class TwapCancelInBlock(BaseModel):
    """TWAP 주문 취소 쿼리 파라미터입니다."""

    algo_order_id: str = Field(..., title="취소할 TWAP 주문의 고유 ID", examples=["TWAP-A01B02C03D04E05F06"])


class TwapCancelRequest(BaseModel):
    """TWAP 주문 취소 요청입니다."""

    params: TwapCancelInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class TwapCancelOutBlock(BaseModel):
    """TWAP 주문 취소 응답입니다 (DELETE /v1/twap, 200)."""

    algo_order_id: str = Field(..., title="취소된 TWAP 주문의 고유 ID", examples=["C0101000000001799625"])


class TwapCancelResponse(BithumbResponseBase):
    """TWAP 주문 취소 응답입니다."""

    block: Optional[TwapCancelOutBlock] = Field(default=None, description="취소된 TWAP 주문 정보")
