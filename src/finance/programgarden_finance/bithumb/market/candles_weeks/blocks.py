"""빗썸 주(週) 캔들 조회 (GET /v1/candles/weeks) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions
from .._candles_common import CandleBaseOutBlock, CandlesQueryInBlock


class CandlesWeeksInBlock(CandlesQueryInBlock):
    """주 캔들 조회 쿼리 파라미터입니다."""


class CandlesWeeksRequest(BaseModel):
    """주 캔들 조회 요청입니다."""

    params: CandlesWeeksInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class CandlesWeeksOutBlock(CandleBaseOutBlock):
    """주 캔들 조회 응답 항목입니다."""

    first_day_of_period: str = Field(
        ..., title="캔들 기간의 시작일", description="yyyy-MM-dd", examples=["2026-06-08"]
    )


class CandlesWeeksResponse(BithumbResponseBase):
    """주 캔들 조회 응답입니다."""

    blocks: Optional[List[CandlesWeeksOutBlock]] = Field(default=None, description="주 캔들 목록")
