"""빗썸 출금 가능 정보 조회 (GET /v1/withdraws/chance) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WithdrawsChanceInBlock(BaseModel):
    """출금 가능 정보 조회 쿼리 파라미터입니다."""

    currency: str = Field(..., title="화폐 코드", examples=["BTC"])
    net_type: str = Field(..., title="출금 네트워크", examples=["BTC"])


class WithdrawsChanceRequest(BaseModel):
    """출금 가능 정보 조회 요청입니다."""

    params: WithdrawsChanceInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawsChanceMemberLevel(BaseModel):
    """회원 등급/보안 설정 정보입니다."""

    security_level: Optional[int] = Field(default=None, title="회원 보안 등급")
    fee_level: Optional[int] = Field(default=None, title="회원 수수료 등급")
    email_verified: Optional[bool] = Field(default=None, title="이메일 인증 여부")
    identity_auth_verified: Optional[bool] = Field(default=None, title="실명 인증 여부")
    bank_account_verified: Optional[bool] = Field(default=None, title="계좌 인증 여부")
    two_factor_auth_verified: Optional[bool] = Field(default=None, title="2차 인증 활성화 여부")
    locked: Optional[bool] = Field(default=None, title="계정 보호 상태 여부")
    wallet_locked: Optional[bool] = Field(default=None, title="출금 보호 상태 여부")


class WithdrawsChanceCurrency(BaseModel):
    """화폐 정보입니다."""

    code: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    withdraw_fee: Optional[str] = Field(default=None, title="해당 화폐의 출금 수수료")
    is_coin: bool = Field(..., title="디지털 자산 여부")
    wallet_state: str = Field(..., title="해당 화폐의 지갑 상태")
    wallet_support: List[str] = Field(..., title="해당 화폐가 지원하는 입출금 정보")


class WithdrawsChanceAccount(BaseModel):
    """계좌(자산) 정보입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    balance: str = Field(..., title="주문 가능 금액/수량")
    locked: str = Field(..., title="주문 중 묶여있는 금액/수량")
    avg_buy_price: str = Field(..., title="매수평균가")
    avg_buy_price_modified: bool = Field(..., title="매수평균가 수정 여부")
    unit_currency: str = Field(..., title="평단가 기준 화폐")


class WithdrawsChanceWithdrawLimit(BaseModel):
    """출금 제약 정보입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    onetime: Optional[str] = Field(default=None, title="1회 출금 한도")
    daily: Optional[str] = Field(default=None, title="1일 출금 한도")
    remaining_daily: Optional[str] = Field(default=None, title="1일 잔여 출금 한도")
    remaining_daily_fiat: Optional[str] = Field(default=None, title="1일 잔여 출금 한도(원화 환산)")
    fiat_currency: Optional[str] = Field(default=None, title="원화 환산 기준 화폐")
    minimum: Optional[str] = Field(default=None, title="최소 출금 금액/수량")
    fixed: Optional[int] = Field(default=None, title="출금 금액/수량의 소수점 자리수")
    withdraw_delayed_fiat: Optional[str] = Field(default=None, title="출금 지연 금액(원화)")
    can_withdraw: bool = Field(..., title="출금 지원 여부")
    remaining_daily_krw: Optional[str] = Field(default=None, title="1일 잔여 출금 한도(통합 원화 환산)")


class WithdrawsChanceOutBlock(BaseModel):
    """출금 가능 정보 조회 응답입니다."""

    member_level: WithdrawsChanceMemberLevel = Field(..., title="회원 등급 정보")
    currency: WithdrawsChanceCurrency = Field(..., title="화폐 정보")
    account: WithdrawsChanceAccount = Field(..., title="계좌 정보")
    withdraw_limit: WithdrawsChanceWithdrawLimit = Field(..., title="출금 제약 정보")


class WithdrawsChanceResponse(BithumbResponseBase):
    """출금 가능 정보 조회 응답입니다."""

    block: Optional[WithdrawsChanceOutBlock] = Field(default=None, description="출금 가능 정보")
