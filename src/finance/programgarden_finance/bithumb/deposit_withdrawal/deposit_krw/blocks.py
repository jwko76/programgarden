"""빗썸 원화 입금 (POST /v1/deposits/krw) 요청/응답 모델입니다.

[!] 고위험 엔드포인트: 실제 원화를 계좌에서 차감하여 빗썸 KRW 잔고로 입금 처리합니다.
2차 인증(카카오)이 필요하여 자동화 테스트로는 검증할 수 없으므로, mock 테스트로만
요청/응답 직렬화를 검증합니다.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class DepositKrwInBlock(BaseModel):
    """원화 입금 요청 본문(JSON body)입니다."""

    amount: str = Field(..., title="입금 금액(원화)", examples=["60000"])
    two_factor_type: Literal["kakao"] = Field(
        ...,
        title="2차 인증 수단",
        description="카카오 인증(kakao)만 지원합니다.",
        examples=["kakao"],
    )


class DepositKrwRequest(BaseModel):
    """원화 입금 요청입니다."""

    body: DepositKrwInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositKrwOutBlock(BaseModel):
    """원화 입금 응답입니다 (POST /v1/deposits/krw, 201)."""

    type: str = Field(..., title="입출금 종류", examples=["deposit"])
    uuid: str = Field(..., title="입금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["KRW"])
    net_type: Optional[str] = Field(default=None, title="입금 네트워크", description="원화 입금은 null입니다.")
    txid: Optional[str] = Field(default=None, title="입금 트랜잭션 ID")
    state: str = Field(..., title="입금 상태", examples=["processing"])
    created_at: str = Field(..., title="입금 생성 시간")
    done_at: Optional[str] = Field(default=None, title="입금 완료 시간")
    amount: str = Field(..., title="입금 금액", examples=["60000"])
    fee: str = Field(..., title="입금 수수료", examples=["0"])
    transaction_type: str = Field(..., title="입금 유형", description="default(일반입금)/internal(바로입금)")


class DepositKrwResponse(BithumbResponseBase):
    """원화 입금 응답입니다."""

    block: Optional[DepositKrwOutBlock] = Field(default=None, description="원화 입금 처리 결과")
