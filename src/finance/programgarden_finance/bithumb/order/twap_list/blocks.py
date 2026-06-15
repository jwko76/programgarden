"""빗썸 TWAP 주문내역 조회 (GET /v1/twap) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class TwapListInBlock(BaseModel):
    """TWAP 주문내역 조회 쿼리 파라미터입니다."""

    market: Optional[str] = Field(default=None, title="마켓 코드", examples=["KRW-BTC"])
    uuids: Optional[List[str]] = Field(default=None, title="TWAP 주문 ID 목록")
    state: Optional[Literal["progress", "done", "cancel"]] = Field(
        default=None, title="주문 상태", description="기본값 progress"
    )
    next_key: Optional[str] = Field(default=None, title="다음 페이지 조회를 위한 커서 값")
    limit: Optional[int] = Field(default=None, title="개수 제한", description="최대 100, 기본값 100")
    order_by: Optional[Literal["asc", "desc"]] = Field(default=None, title="정렬 방식", description="기본값 desc")


class TwapListRequest(BaseModel):
    """TWAP 주문내역 조회 요청입니다."""

    params: TwapListInBlock = Field(default_factory=TwapListInBlock, description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class TwapOrderItem(BaseModel):
    """TWAP 주문 항목입니다."""

    uuid: str = Field(..., title="TWAP 주문의 고유 ID")
    side: str = Field(..., title="주문 종류", description="bid/ask")
    price: Optional[str] = Field(default=None, title="주문 당시 가격")
    state: str = Field(..., title="주문 상태", description="progress/done/cancel")
    market: str = Field(..., title="거래 페어 심볼", examples=["KRW-BTC"])
    created_at: str = Field(..., title="주문 생성 시각")
    volume: Optional[str] = Field(default=None, title="사용자 입력 주문량")
    finished_at: Optional[str] = Field(default=None, title="주문 종료 시각", description="state가 done일 때만 존재")
    total_order_count: Optional[int] = Field(default=None, title="주문 전체 건수")
    total_trades_count: Optional[int] = Field(default=None, title="주문 전체 체결 수")
    progress_count: Optional[int] = Field(default=None, title="주문 진행 건수")
    total_executed_amount: Optional[str] = Field(default=None, title="주문 총 체결 금액")
    total_executed_volume: Optional[str] = Field(default=None, title="주문 총 체결 수량")
    avg_trade_price: Optional[str] = Field(default=None, title="주문 평균 체결 단가")
    wallet_id: Optional[str] = Field(default=None, title="지갑의 고유 ID")
    canceled_at: Optional[str] = Field(default=None, title="주문 취소 시각", description="state가 cancel일 때만 존재")
    cancel_type: Optional[str] = Field(default=None, title="취소 타입", description="user/asset/admin/system")


class TwapListOutBlock(BaseModel):
    """TWAP 주문내역 조회 응답입니다 (GET /v1/twap, 200)."""

    has_next: bool = Field(..., title="다음 페이지 존재 여부")
    next_key: Optional[str] = Field(default=None, title="다음 페이지 조회를 위한 커서 값(Base64)")
    orders: List[TwapOrderItem] = Field(default_factory=list, title="TWAP 주문 목록")


class TwapListResponse(BithumbResponseBase):
    """TWAP 주문내역 조회 응답입니다."""

    block: Optional[TwapListOutBlock] = Field(default=None, description="TWAP 주문 조회 결과")
