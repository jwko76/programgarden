"""빗썸 입금 주소 생성 요청 (POST /v1/deposits/generate_coin_address) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class DepositAddressGenerateInBlock(BaseModel):
    """입금 주소 생성 요청 본문(JSON body)입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    net_type: str = Field(..., title="입금 네트워크", examples=["BTC"])


class DepositAddressGenerateRequest(BaseModel):
    """입금 주소 생성 요청입니다."""

    body: DepositAddressGenerateInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositAddressGenerateOutBlock(BaseModel):
    """입금 주소 생성 응답입니다 (POST /v1/deposits/generate_coin_address, 201)."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: str = Field(..., title="입금 네트워크", examples=["BTC"])
    deposit_address: Optional[str] = Field(default=None, title="입금 주소", description="생성이 완료되지 않은 경우 null일 수 있습니다.")
    secondary_address: Optional[str] = Field(default=None, title="보조 입금 주소", description="일부 화폐(XRP 등)는 secondary_address(데스티네이션 태그/메모)가 필요합니다.")


class DepositAddressGenerateResponse(BithumbResponseBase):
    """입금 주소 생성 응답입니다."""

    block: Optional[DepositAddressGenerateOutBlock] = Field(default=None, description="생성된 입금 주소 정보")
