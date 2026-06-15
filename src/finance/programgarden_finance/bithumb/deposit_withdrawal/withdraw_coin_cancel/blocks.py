"""빗썸 가상자산 출금 취소 (DELETE /v1/withdraws/coin) 요청/응답 모델입니다.

[!] 고위험 엔드포인트: 진행 중인 가상자산 출금 요청을 취소합니다. mock 테스트로만
요청/응답 직렬화를 검증하며, 실거래 라이브 테스트는 진행하지 않습니다.
"""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WithdrawCoinCancelInBlock(BaseModel):
    """가상자산 출금 취소 쿼리 파라미터입니다."""

    withdrawal_id: str = Field(..., title="취소할 출금의 고유 ID")


class WithdrawCoinCancelRequest(BaseModel):
    """가상자산 출금 취소 요청입니다."""

    params: WithdrawCoinCancelInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawCoinCancelOutBlock(BaseModel):
    """가상자산 출금 취소 응답입니다 (DELETE /v1/withdraws/coin, 200)."""

    type: str = Field(..., title="입출금 종류", examples=["withdraw"])
    withdrawal_id: str = Field(..., title="취소된 출금의 고유 ID")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: str = Field(..., title="출금 네트워크", examples=["BTC"])
    state: str = Field(..., title="출금 상태", examples=["CANCELLED"])
    created_at: str = Field(..., title="출금 생성 시각")
    amount: str = Field(..., title="출금 금액/수량")
    fee: str = Field(..., title="출금 수수료")
    krw_amount: str = Field(..., title="원화 환산 가격")


class WithdrawCoinCancelResponse(BithumbResponseBase):
    """가상자산 출금 취소 응답입니다."""

    block: Optional[WithdrawCoinCancelOutBlock] = Field(default=None, description="출금 취소 처리 결과")
