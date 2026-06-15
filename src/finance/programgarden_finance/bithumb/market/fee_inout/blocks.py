"""빗썸 입출금 수수료 조회 (GET /v2/fee/inout/{currency}) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class FeeInoutInBlock(BaseModel):
    """입출금 수수료 조회 쿼리 파라미터입니다."""

    currency: str = Field(
        ...,
        title="화폐 코드",
        description="화폐를 의미하는 영문 대문자 코드입니다. 전체 화폐를 조회하려면 'ALL'을 사용합니다 (URL 경로에 포함되며 쿼리 파라미터로는 전송되지 않습니다).",
        examples=["BTC"],
    )


class FeeInoutRequest(BaseModel):
    """입출금 수수료 조회 요청입니다."""

    params: FeeInoutInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class FeeInoutNetwork(BaseModel):
    """화폐별 네트워크 입출금 수수료 정보입니다."""

    net_name: str = Field(..., title="네트워크 이름", examples=["Bitcoin"])
    deposit_fee_quantity: Optional[str] = Field(default=None, title="입금 수수료", examples=["0"])
    deposit_minimum_quantity: Optional[str] = Field(default=None, title="최소 입금 수량", examples=["0.001"])
    withdraw_fee_quantity: Optional[str] = Field(
        default=None,
        title="출금 수수료(고정값)",
        description="고정 수수료 모델인 경우의 출금 수수료입니다. 비율 모델인 경우 null입니다.",
        examples=["0.0005"],
    )
    withdraw_rate: Optional[str] = Field(
        default=None,
        title="출금 수수료율(비율값)",
        description="비율 수수료 모델인 경우의 출금 수수료율입니다. 고정 수수료 모델인 경우 null입니다.",
        examples=["0.001"],
    )
    withdraw_fee_min: Optional[str] = Field(default=None, title="출금 수수료 최소값(비율 모델)")
    withdraw_fee_max: Optional[str] = Field(default=None, title="출금 수수료 최대값(비율 모델)")
    withdraw_minimum_quantity: Optional[str] = Field(default=None, title="최소 출금 수량", examples=["0.001"])


class FeeInoutOutBlock(BaseModel):
    """화폐별 입출금 수수료 응답 항목입니다."""

    name: str = Field(..., title="화폐 한글명", examples=["비트코인"])
    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    networks: List[FeeInoutNetwork] = Field(default_factory=list, title="네트워크별 수수료 정보")


class FeeInoutResponse(BithumbResponseBase):
    """입출금 수수료 조회 응답입니다.

    모든 수수료 값은 출금 화폐(currency) 단위로 표시됩니다.
    """

    blocks: Optional[List[FeeInoutOutBlock]] = Field(default=None, description="화폐별 입출금 수수료 목록")
