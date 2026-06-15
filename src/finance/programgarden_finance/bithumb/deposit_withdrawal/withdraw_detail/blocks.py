"""빗썸 개별 출금 조회 (GET /v1/withdraw) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WithdrawDetailInBlock(BaseModel):
    """개별 출금 조회 쿼리 파라미터입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    uuid: Optional[str] = Field(default=None, title="출금의 고유 아이디")
    txid: Optional[str] = Field(default=None, title="출금 트랜잭션 ID")


class WithdrawDetailRequest(BaseModel):
    """개별 출금 조회 요청입니다."""

    params: WithdrawDetailInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawDetailOutBlock(BaseModel):
    """개별 출금 조회 응답입니다."""

    type: str = Field(..., title="입출금 종류", examples=["withdraw"])
    uuid: str = Field(..., title="출금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: Optional[str] = Field(default=None, title="출금 네트워크", examples=["BTC"])
    txid: Optional[str] = Field(default=None, title="출금 트랜잭션 ID")
    state: str = Field(..., title="출금 상태", description="PROCESSING/DONE/CANCELLED", examples=["DONE"])
    created_at: str = Field(..., title="출금 생성 시각")
    done_at: Optional[str] = Field(default=None, title="출금 완료 시각")
    amount: str = Field(..., title="출금 금액/수량")
    fee: str = Field(..., title="출금 수수료")
    transaction_type: Optional[str] = Field(default=None, title="출금 유형", description="default(일반출금)")


class WithdrawDetailResponse(BithumbResponseBase):
    """개별 출금 조회 응답입니다."""

    block: Optional[WithdrawDetailOutBlock] = Field(default=None, description="출금 상세 정보")
