"""빗썸 출금 허용 주소 리스트 조회 (GET /v1/withdraws/coin_addresses) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WithdrawCoinAddressesInBlock(BaseModel):
    """출금 허용 주소 리스트 조회는 쿼리 파라미터가 없습니다."""


class WithdrawCoinAddressesRequest(BaseModel):
    """출금 허용 주소 리스트 조회 요청입니다."""

    params: WithdrawCoinAddressesInBlock = Field(default_factory=WithdrawCoinAddressesInBlock, description="요청 파라미터 (없음)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawCoinAddressesOutBlock(BaseModel):
    """출금 허용 주소 리스트 조회 응답 항목입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: str = Field(..., title="출금 네트워크 타입", examples=["BTC"])
    network_name: str = Field(..., title="출금 네트워크 이름", examples=["Bitcoin"])
    withdraw_address: str = Field(..., title="출금 주소")
    secondary_address: Optional[str] = Field(default=None, title="2차 출금 주소", description="일부 화폐(XRP 등)는 데스티네이션 태그/메모가 필요합니다.")
    exchange_name: str = Field(..., title="출금 거래소명")
    owner_type: Literal["personal", "corporation"] = Field(..., title="주소 소유주 구분", description="personal(개인)/corporation(법인)")
    owner_ko_name: Optional[str] = Field(default=None, title="주소 소유주 국문명")
    owner_en_name: Optional[str] = Field(default=None, title="주소 소유주 영문명")
    owner_corp_ko_name: Optional[str] = Field(default=None, title="주소 소유 법인 국문명")
    owner_corp_en_name: Optional[str] = Field(default=None, title="주소 소유 법인 영문명")


class WithdrawCoinAddressesResponse(BithumbResponseBase):
    """출금 허용 주소 리스트 조회 응답입니다."""

    blocks: Optional[List[WithdrawCoinAddressesOutBlock]] = Field(default=None, description="출금 허용 주소 목록")
