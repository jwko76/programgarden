"""빗썸 원화 출금 요청 (POST /v1/withdraws/krw) 요청/응답 모델입니다.

[!] 고위험 엔드포인트: 실제 빗썸 KRW 잔고에서 차감하여 등록된 은행 계좌로 출금
처리합니다. 2차 인증(카카오)이 필요하여 자동화 테스트로는 검증할 수 없으므로,
mock 테스트로만 요청/응답 직렬화를 검증합니다.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WithdrawKrwInBlock(BaseModel):
    """원화 출금 요청 본문(JSON body)입니다."""

    amount: str = Field(..., title="출금 금액(원화)", examples=["6000"])
    two_factor_type: Literal["kakao"] = Field(
        ...,
        title="2차 인증 수단",
        description="카카오 인증(kakao)만 지원합니다.",
        examples=["kakao"],
    )


class WithdrawKrwRequest(BaseModel):
    """원화 출금 요청입니다."""

    body: WithdrawKrwInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawKrwOutBlock(BaseModel):
    """원화 출금 요청 응답입니다 (POST /v1/withdraws/krw, 201)."""

    type: str = Field(..., title="입출금 종류", examples=["withdraw"])
    uuid: str = Field(..., title="출금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["KRW"])
    net_type: Optional[str] = Field(default=None, title="출금 네트워크", description="원화 출금은 null입니다.")
    txid: Optional[str] = Field(default=None, title="출금 트랜잭션 ID")
    state: str = Field(..., title="출금 상태", description="PROCESSING/DONE/CANCELLED", examples=["PROCESSING"])
    created_at: str = Field(..., title="출금 생성 시각")
    done_at: Optional[str] = Field(default=None, title="출금 완료 시각")
    amount: str = Field(..., title="출금 금액", examples=["6000"])
    fee: str = Field(..., title="출금 수수료", examples=["1000"])
    transaction_type: str = Field(..., title="출금 유형", description="default(일반출금)")


class WithdrawKrwResponse(BithumbResponseBase):
    """원화 출금 요청 응답입니다."""

    block: Optional[WithdrawKrwOutBlock] = Field(default=None, description="원화 출금 처리 결과")
