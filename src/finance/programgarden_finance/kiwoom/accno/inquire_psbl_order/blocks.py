"""키움증권 주문인출가능금액요청 (kt00010) 요청/응답 모델입니다.

주의: 모의투자 서버는 이 TR을 지원하지 않습니다 — 2026-07-18 라이브 확인
결과 return_code=20, "[2000](RC7006:모의투자 조회실패)" 반환. 응답 필드
검증은 실전 서버에서만 가능합니다.
TODO(실계좌 검증): 실전 서버로 실제 필드명/구조 확인 필요.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class InquirePsblOrderInBlock(BaseModel):
    """주문인출가능금액요청 POST 바디입니다."""

    model_config = ConfigDict(populate_by_name=True)

    acnt_no: str = Field(..., title="계좌번호")
    stk_cd: str = Field(..., title="종목코드", examples=["005930"])
    uv: str = Field(
        default="0",
        title="주문단가",
        description="시장가 확인 시 0 (TODO(실계좌 검증))",
    )
    trde_tp: str = Field(
        default="1",
        title="매매구분",
        description="1: 매수, 2: 매도로 추정 (TODO(실계좌 검증): 정확한 코드값 확인)",
    )


class InquirePsblOrderRequest(BaseModel):
    """주문인출가능금액요청 요청입니다."""

    body: InquirePsblOrderInBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquirePsblOrderOutBlock(BaseModel):
    """주문인출가능금액 정보입니다. 응답 최상위 키에서 직접 추출한다고 가정합니다."""

    model_config = ConfigDict(extra="ignore")

    ord_alow_amt: Optional[str] = Field(default=None, title="주문가능금액")
    max_buy_amt: Optional[str] = Field(default=None, title="최대매수가능금액", description="TODO(실계좌 검증): 필드명 확인")
    max_buy_qty: Optional[str] = Field(default=None, title="최대매수가능수량", description="TODO(실계좌 검증): 필드명 확인")


class InquirePsblOrderResponse(KiwoomResponseBase):
    """주문인출가능금액요청 응답입니다."""

    block: Optional[InquirePsblOrderOutBlock] = Field(default=None, description="주문인출가능금액 정보")
