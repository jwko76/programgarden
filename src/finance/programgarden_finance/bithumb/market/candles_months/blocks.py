"""빗썸 월(月) 캔들 조회 (GET /v1/candles/months) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions
from .._candles_common import CandleBaseOutBlock, CandlesQueryInBlock


class CandlesMonthsInBlock(CandlesQueryInBlock):
    """월 캔들 조회 쿼리 파라미터입니다."""


class CandlesMonthsRequest(BaseModel):
    """월 캔들 조회 요청입니다."""

    params: CandlesMonthsInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class CandlesMonthsOutBlock(CandleBaseOutBlock):
    """월 캔들 조회 응답 항목입니다."""

    first_day_of_period: str = Field(
        ..., title="캔들 기간의 시작일", description="yyyy-MM-dd", examples=["2026-06-01"]
    )


class CandlesMonthsResponse(BithumbResponseBase):
    """월 캔들 조회 응답입니다."""

    blocks: Optional[List[CandlesMonthsOutBlock]] = Field(default=None, description="월 캔들 목록")
