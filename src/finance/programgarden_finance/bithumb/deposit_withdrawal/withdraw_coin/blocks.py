"""빗썸 가상자산 출금 요청 (POST /v1/withdraws/coin) 요청/응답 모델입니다.

[!] 고위험 엔드포인트: 실제 가상자산이 외부 주소로 이동합니다. mock 테스트로만
요청/응답 직렬화를 검증하며, 실거래 라이브 테스트는 진행하지 않습니다.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WithdrawCoinInBlock(BaseModel):
    """가상자산 출금 요청 본문(JSON body)입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    net_type: str = Field(..., title="출금 네트워크", examples=["BTC"])
    amount: str = Field(..., title="출금 수량", examples=["0.01"])
    address: str = Field(..., title="등록된 출금 주소", examples=["3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"])
    secondary_address: Optional[str] = Field(default=None, title="보조 주소", description="일부 화폐(XRP 등)는 secondary_address(데스티네이션 태그/메모)가 필요합니다.")
    exchange_name: Optional[str] = Field(default=None, title="출금 거래소명(영문)")
    receiver_type: Optional[Literal["personal", "corporation"]] = Field(
        default=None, title="수취인 구분", description="personal(개인)/corporation(법인)"
    )
    receiver_ko_name: Optional[str] = Field(default=None, title="수취인 한글명")
    receiver_en_name: Optional[str] = Field(default=None, title="수취인 영문명")
    receiver_corp_ko_name: Optional[str] = Field(default=None, title="수취 법인 한글명", description="수취인이 법인인 경우 필수입니다.")
    receiver_corp_en_name: Optional[str] = Field(default=None, title="수취 법인 영문명", description="수취인이 법인인 경우 필수입니다.")


class WithdrawCoinRequest(BaseModel):
    """가상자산 출금 요청입니다."""

    body: WithdrawCoinInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawCoinOutBlock(BaseModel):
    """가상자산 출금 요청 응답입니다 (POST /v1/withdraws/coin, 201)."""

    type: str = Field(..., title="입출금 종류", examples=["withdraw"])
    uuid: str = Field(..., title="출금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: str = Field(..., title="출금 네트워크", examples=["BTC"])
    state: str = Field(..., title="출금 상태", description="PROCESSING/DONE/CANCELLED", examples=["PROCESSING"])
    created_at: str = Field(..., title="출금 생성 시각")
    done_at: Optional[str] = Field(default=None, title="출금 완료 시각")
    amount: str = Field(..., title="출금 금액/수량", examples=["0.01"])
    fee: str = Field(..., title="출금 수수료", examples=["0.0005"])
    krw_amount: str = Field(..., title="원화 환산 가격", examples=["1000000"])
    transaction_type: Optional[str] = Field(default=None, title="출금 유형", description="default(일반출금)")
    txid: Optional[str] = Field(default=None, title="출금 트랜잭션 ID")


class WithdrawCoinResponse(BithumbResponseBase):
    """가상자산 출금 요청 응답입니다."""

    block: Optional[WithdrawCoinOutBlock] = Field(default=None, description="출금 요청 처리 결과")
