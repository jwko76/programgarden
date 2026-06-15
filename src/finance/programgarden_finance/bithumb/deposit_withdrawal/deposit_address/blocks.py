"""빗썸 개별 입금 주소 조회 (GET /v1/deposits/coin_address) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class DepositAddressInBlock(BaseModel):
    """개별 입금 주소 조회 쿼리 파라미터입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    net_type: str = Field(..., title="입금 네트워크", examples=["BTC"])


class DepositAddressRequest(BaseModel):
    """개별 입금 주소 조회 요청입니다."""

    params: DepositAddressInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositAddressOutBlock(BaseModel):
    """개별 입금 주소 조회 응답입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: str = Field(..., title="입금 네트워크", examples=["BTC"])
    deposit_address: str = Field(..., title="입금 주소", examples=["3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"])
    secondary_address: Optional[str] = Field(default=None, title="보조 입금 주소", description="일부 화폐(XRP 등)는 secondary_address(데스티네이션 태그/메모)가 필요합니다.")


class DepositAddressResponse(BithumbResponseBase):
    """개별 입금 주소 조회 응답입니다."""

    block: Optional[DepositAddressOutBlock] = Field(default=None, description="입금 주소 정보")
