"""빗썸 전체 계좌 조회 (GET /v1/accounts) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class AccountsInBlock(BaseModel):
    """전체 계좌 조회는 쿼리 파라미터가 없습니다."""


class AccountsRequest(BaseModel):
    """전체 계좌 조회 요청입니다."""

    params: AccountsInBlock = Field(default_factory=AccountsInBlock, description="요청 파라미터 (없음)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class AccountsOutBlock(BaseModel):
    """전체 계좌 조회 응답 항목 (자산별 보유 현황)입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    balance: str = Field(..., title="주문 가능 금액/수량", examples=["2.0"])
    locked: str = Field(..., title="주문 중 묶여있는 금액/수량", examples=["0.0"])
    avg_buy_price: str = Field(..., title="매수평균가", examples=["95000000"])
    avg_buy_price_modified: bool = Field(..., title="매수평균가 수정 여부", examples=[False])
    unit_currency: str = Field(..., title="평단가 기준 화폐", examples=["KRW"])


class AccountsResponse(BithumbResponseBase):
    """전체 계좌 조회 응답입니다."""

    blocks: Optional[List[AccountsOutBlock]] = Field(default=None, description="자산별 보유 현황 목록")
