"""빗썸 분(分) 캔들 조회 (GET /v1/candles/minutes/{unit}) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions
from .._candles_common import CandleBaseOutBlock, CandlesQueryInBlock

CandleMinuteUnit = Literal[1, 3, 5, 10, 15, 30, 60, 240]


class CandlesMinutesInBlock(CandlesQueryInBlock):
    """분 캔들 조회 쿼리 파라미터입니다."""

    unit: CandleMinuteUnit = Field(
        default=1,
        title="분 단위",
        description="1, 3, 5, 10, 15, 30, 60, 240 중 하나입니다 (URL 경로에 포함되며 쿼리 파라미터로는 전송되지 않습니다).",
        examples=[1],
    )


class CandlesMinutesRequest(BaseModel):
    """분 캔들 조회 요청입니다."""

    params: CandlesMinutesInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class CandlesMinutesOutBlock(CandleBaseOutBlock):
    """분 캔들 조회 응답 항목입니다."""

    unit: int = Field(..., title="분 단위", examples=[1])


class CandlesMinutesResponse(BithumbResponseBase):
    """분 캔들 조회 응답입니다."""

    blocks: Optional[List[CandlesMinutesOutBlock]] = Field(default=None, description="분 캔들 목록")
