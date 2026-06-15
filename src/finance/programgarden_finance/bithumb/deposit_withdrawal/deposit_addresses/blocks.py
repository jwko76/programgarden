"""빗썸 전체 입금 주소 조회 (GET /v1/deposits/coin_addresses) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class DepositAddressesInBlock(BaseModel):
    """전체 입금 주소 조회는 쿼리 파라미터가 없습니다."""


class DepositAddressesRequest(BaseModel):
    """전체 입금 주소 조회 요청입니다."""

    params: DepositAddressesInBlock = Field(default_factory=DepositAddressesInBlock, description="요청 파라미터 (없음)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositAddressesOutBlock(BaseModel):
    """전체 입금 주소 조회 응답 항목입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: str = Field(..., title="입금 네트워크", examples=["BTC"])
    deposit_address: Optional[str] = Field(default=None, title="입금 주소", description="생성되지 않은 경우 null일 수 있습니다.")
    secondary_address: Optional[str] = Field(default=None, title="보조 입금 주소", description="일부 화폐(XRP 등)는 secondary_address(데스티네이션 태그/메모)가 필요합니다.")


class DepositAddressesResponse(BithumbResponseBase):
    """전체 입금 주소 조회 응답입니다."""

    blocks: Optional[List[DepositAddressesOutBlock]] = Field(default=None, description="화폐/네트워크별 입금 주소 목록")
