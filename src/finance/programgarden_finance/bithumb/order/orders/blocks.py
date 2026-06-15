"""빗썸 주문 리스트 조회 (GET /v1/orders) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions
from .._common import OrderOutBlock

OrderState = Literal["wait", "watch", "done", "cancel"]


class OrdersInBlock(BaseModel):
    """주문 리스트 조회 쿼리 파라미터입니다. state와 states는 동시에 사용할 수 없습니다."""

    market: Optional[str] = Field(default=None, title="마켓 코드", examples=["KRW-BTC"])
    state: Optional[OrderState] = Field(
        default=None, title="주문 상태", description="wait/watch/done/cancel 중 하나", examples=["wait"]
    )
    states: Optional[List[OrderState]] = Field(default=None, title="주문 상태 목록 (state와 동시 사용 불가)")
    uuids: Optional[List[str]] = Field(default=None, title="주문 UUID 목록")
    client_order_ids: Optional[List[str]] = Field(default=None, title="클라이언트 주문 식별자 목록")
    page: Optional[int] = Field(default=None, title="페이지 번호", description="기본 1", examples=[1])
    limit: Optional[int] = Field(default=None, title="조회 개수", description="기본 100, 최대 100", examples=[100])
    order_by: Optional[Literal["asc", "desc"]] = Field(
        default=None, title="정렬 방식", description="created_at 기준 정렬, 기본 desc", examples=["desc"]
    )


class OrdersRequest(BaseModel):
    """주문 리스트 조회 요청입니다."""

    params: OrdersInBlock = Field(default_factory=OrdersInBlock, description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class OrdersOutBlock(OrderOutBlock):
    """주문 리스트 조회 응답 항목입니다."""


class OrdersResponse(BithumbResponseBase):
    """주문 리스트 조회 응답입니다."""

    blocks: Optional[List[OrdersOutBlock]] = Field(default=None, description="주문 목록")
