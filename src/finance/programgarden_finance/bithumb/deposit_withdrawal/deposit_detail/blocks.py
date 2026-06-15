"""빗썸 개별 입금 조회 (GET /v1/deposit) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class DepositDetailInBlock(BaseModel):
    """개별 입금 조회 쿼리 파라미터입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    uuid: Optional[str] = Field(default=None, title="입금의 고유 아이디")
    txid: Optional[str] = Field(default=None, title="입금 트랜잭션 ID")


class DepositDetailRequest(BaseModel):
    """개별 입금 조회 요청입니다."""

    params: DepositDetailInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositDetailOutBlock(BaseModel):
    """개별 입금 조회 응답입니다."""

    type: str = Field(..., title="입출금 종류", examples=["deposit"])
    uuid: str = Field(..., title="입금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: Optional[str] = Field(default=None, title="입금 네트워크", examples=["BTC"])
    txid: Optional[str] = Field(default=None, title="입금 트랜잭션 ID")
    state: str = Field(..., title="입금 상태", examples=["done"])
    created_at: str = Field(..., title="입금 생성 시간")
    done_at: Optional[str] = Field(default=None, title="입금 완료 시간")
    amount: str = Field(..., title="입금 금액/수량", examples=["1.0"])
    fee: str = Field(..., title="입금 수수료", examples=["0.0"])
    transaction_type: Optional[str] = Field(default=None, title="입금 유형", description="default(일반입금)/internal(바로입금)")


class DepositDetailResponse(BithumbResponseBase):
    """개별 입금 조회 응답입니다."""

    block: Optional[DepositDetailOutBlock] = Field(default=None, description="입금 상세 정보")
