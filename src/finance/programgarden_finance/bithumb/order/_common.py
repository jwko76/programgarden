"""주문 조회/생성/취소 모듈에서 공통으로 사용하는 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field


class OrderTrade(BaseModel):
    """주문에 대한 체결 내역입니다."""

    market: str = Field(..., title="마켓의 유일 키", examples=["KRW-BTC"])
    uuid: str = Field(..., title="체결의 고유 아이디", examples=["9e8f8eba-7050-4837-82c3-768e2e63b58a"])
    price: str = Field(..., title="체결 가격", examples=["95500000"])
    volume: str = Field(..., title="체결량", examples=["0.01"])
    funds: str = Field(..., title="체결된 총 가격", examples=["955000"])
    side: str = Field(..., title="체결 종류", description="bid(매수)/ask(매도)", examples=["bid"])
    created_at: str = Field(..., title="체결 시각", examples=["2026-06-14T12:00:00+09:00"])


class OrderOutBlock(BaseModel):
    """주문 정보 응답의 공통 필드입니다."""

    uuid: str = Field(..., title="주문의 고유 아이디", examples=["9e8f8eba-7050-4837-82c3-768e2e63b58a"])
    side: str = Field(..., title="주문 종류", description="bid(매수)/ask(매도)", examples=["bid"])
    ord_type: str = Field(..., title="주문 방식", description="limit/price/market/best", examples=["limit"])
    price: Optional[str] = Field(default=None, title="주문 당시 화폐 가격", examples=["95500000"])
    state: str = Field(
        ...,
        title="주문 상태",
        description="wait(체결 대기)/watch(예약주문 대기)/done(전체 체결 완료)/cancel(주문 취소)",
        examples=["wait"],
    )
    market: str = Field(..., title="마켓의 유일 키", examples=["KRW-BTC"])
    created_at: str = Field(..., title="주문 생성 시간", examples=["2026-06-14T12:00:00+09:00"])
    volume: Optional[str] = Field(default=None, title="사용자가 입력한 주문 양", examples=["0.01"])
    remaining_volume: Optional[str] = Field(default=None, title="체결 후 남은 주문 양", examples=["0.0"])
    reserved_fee: str = Field(..., title="수수료로 예약된 비용", examples=["0.0"])
    remaining_fee: str = Field(..., title="남은 수수료", examples=["0.0"])
    paid_fee: str = Field(..., title="지불된 수수료", examples=["0.0"])
    locked: str = Field(..., title="거래에 사용중인 비용", examples=["955000"])
    executed_volume: str = Field(..., title="체결된 양", examples=["0.0"])
    executed_funds: Optional[str] = Field(default=None, title="체결된 총 금액", examples=["0"])
    trades_count: int = Field(..., title="해당 주문에 걸린 체결 수", examples=[0])
    time_in_force: Optional[str] = Field(default=None, title="IOC, FOK 설정", description="ioc/fok", examples=["ioc"])
    client_order_id: Optional[str] = Field(default=None, title="클라이언트가 지정한 주문 식별자")
