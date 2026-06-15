"""빗썸 일(日) 캔들 조회 (GET /v1/candles/days) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions
from .._candles_common import CandleBaseOutBlock, CandlesQueryInBlock


class CandlesDaysInBlock(CandlesQueryInBlock):
    """일 캔들 조회 쿼리 파라미터입니다."""

    convertingPriceUnit: Optional[str] = Field(
        default=None,
        title="환산 가격 단위",
        description="'KRW'로 설정 시 종가를 KRW로 환산한 converted_trade_price를 응답에 포함합니다.",
        examples=["KRW"],
    )


class CandlesDaysRequest(BaseModel):
    """일 캔들 조회 요청입니다."""

    params: CandlesDaysInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class CandlesDaysOutBlock(CandleBaseOutBlock):
    """일 캔들 조회 응답 항목입니다."""

    prev_closing_price: float = Field(..., title="전일 종가", examples=[94800000.0])
    change_price: float = Field(..., title="전일 종가 대비 변화 금액", examples=[700000.0])
    change_rate: float = Field(..., title="전일 종가 대비 변화율", examples=[0.00738])
    converted_trade_price: Optional[float] = Field(
        default=None, title="종가의 환산 가격", description="convertingPriceUnit 요청 시에만 포함", examples=[95500000.0]
    )


class CandlesDaysResponse(BithumbResponseBase):
    """일 캔들 조회 응답입니다."""

    blocks: Optional[List[CandlesDaysOutBlock]] = Field(default=None, description="일 캔들 목록")
