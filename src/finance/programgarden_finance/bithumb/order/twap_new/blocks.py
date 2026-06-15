"""빗썸 TWAP 주문 등록 (POST /v1/twap) 요청/응답 모델입니다."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class TwapNewInBlock(BaseModel):
    """TWAP 주문 등록 요청 본문(JSON body)입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    side: Literal["bid", "ask"] = Field(..., title="주문 종류", description="bid(매수)/ask(매도)", examples=["bid"])
    duration: str = Field(
        ...,
        title="주문 진행 시간(초)",
        description="TWAP 주문이 진행되는 시간(초). 최소 300, 최대 43200.",
        examples=["3600"],
    )
    frequency: str = Field(
        ...,
        title="분할 주문 간격(초)",
        description="15/20/30/60/120 중 하나만 허용됩니다.",
        examples=["60"],
    )
    volume: Optional[str] = Field(
        default=None,
        title="주문 수량",
        description="side가 ask(매도)인 경우 필수입니다.",
        examples=["0.5"],
    )
    price: Optional[str] = Field(
        default=None,
        title="주문 가격",
        description="side가 bid(매수)인 경우 필수입니다.",
        examples=["100000000"],
    )


class TwapNewRequest(BaseModel):
    """TWAP 주문 등록 요청입니다."""

    body: TwapNewInBlock = Field(..., description="요청 본문(JSON body)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class TwapNewOutBlock(BaseModel):
    """TWAP 주문 등록 응답입니다 (POST /v1/twap, 200)."""

    algo_order_id: str = Field(..., title="TWAP 주문의 고유 ID", examples=["TWAP-A01B02C03D04E05F06"])


class TwapNewResponse(BithumbResponseBase):
    """TWAP 주문 등록 응답입니다."""

    block: Optional[TwapNewOutBlock] = Field(default=None, description="등록된 TWAP 주문 정보")
