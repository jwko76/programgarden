"""빗썸 주문 가능 정보 조회 (GET /v1/orders/chance) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class OrdersChanceInBlock(BaseModel):
    """주문 가능 정보 조회 쿼리 파라미터입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])


class OrdersChanceRequest(BaseModel):
    """주문 가능 정보 조회 요청입니다."""

    params: OrdersChanceInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class OrdersChanceMarketSide(BaseModel):
    """마켓의 매도/매수 측 주문 제약 정보입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["KRW"])
    price_unit: Optional[str] = Field(default=None, title="주문 가격 단위")
    min_total: Optional[str] = Field(default=None, title="최소 주문 금액", examples=["5000"])


class OrdersChanceMarketInfo(BaseModel):
    """마켓 정보입니다."""

    id: str = Field(..., title="마켓의 유일 키", examples=["KRW-BTC"])
    name: str = Field(..., title="마켓 이름", examples=["BTC/KRW"])
    order_types: Optional[List[str]] = Field(default=None, title="지원하는 주문 방식 목록 (deprecated)")
    order_sides: Optional[List[str]] = Field(default=None, title="지원하는 주문 종류 목록")
    bid_types: Optional[List[str]] = Field(default=None, title="매수 주문 방식 목록")
    ask_types: Optional[List[str]] = Field(default=None, title="매도 주문 방식 목록")
    bid: OrdersChanceMarketSide = Field(..., title="매수 시 제약사항")
    ask: OrdersChanceMarketSide = Field(..., title="매도 시 제약사항")
    max_total: Optional[str] = Field(default=None, title="최대 주문 금액", examples=["1000000000"])
    state: str = Field(..., title="마켓 운영 상태", examples=["active"])


class OrdersChanceAccount(BaseModel):
    """주문 가능 정보 조회 시 함께 반환되는 계좌 정보입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["KRW"])
    balance: str = Field(..., title="주문 가능 금액/수량", examples=["1000000"])
    locked: str = Field(..., title="주문 중 묶여있는 금액/수량", examples=["0"])
    avg_buy_price: str = Field(..., title="매수평균가", examples=["0"])
    avg_buy_price_modified: bool = Field(..., title="매수평균가 수정 여부", examples=[False])
    unit_currency: str = Field(..., title="평단가 기준 화폐", examples=["KRW"])


class OrdersChanceOutBlock(BaseModel):
    """주문 가능 정보 조회 응답입니다."""

    bid_fee: str = Field(..., title="매수 수수료 비율", examples=["0.0004"])
    ask_fee: str = Field(..., title="매도 수수료 비율", examples=["0.0004"])
    maker_bid_fee: Optional[str] = Field(default=None, title="메이커 매수 수수료 비율", examples=["0.0004"])
    maker_ask_fee: Optional[str] = Field(default=None, title="메이커 매도 수수료 비율", examples=["0.0004"])
    market: OrdersChanceMarketInfo = Field(..., title="마켓 정보")
    bid_account: OrdersChanceAccount = Field(..., title="매수 시 사용할 화폐의 계좌 정보")
    ask_account: OrdersChanceAccount = Field(..., title="매도 시 사용할 화폐의 계좌 정보")


class OrdersChanceResponse(BithumbResponseBase):
    """주문 가능 정보 조회 응답입니다."""

    block: Optional[OrdersChanceOutBlock] = Field(default=None, description="주문 가능 정보")
