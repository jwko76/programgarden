"""빗썸 API 키 리스트 조회 (GET /v1/api_keys) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class ApiKeysInBlock(BaseModel):
    """API 키 리스트 조회는 쿼리 파라미터가 없습니다."""


class ApiKeysRequest(BaseModel):
    """API 키 리스트 조회 요청입니다."""

    params: ApiKeysInBlock = Field(default_factory=ApiKeysInBlock, description="요청 파라미터 (없음)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class ApiKeysOutBlock(BaseModel):
    """API 키 리스트 조회 응답 항목입니다."""

    access_key: str = Field(
        ...,
        title="API 키",
        examples=["59683c90185742d69fd8fa1bc0cf27785c392afaa56ece"],
    )
    expire_at: str = Field(..., title="API 키 만료 일시", examples=["2026-06-11T09:00:00+09:00"])


class ApiKeysResponse(BithumbResponseBase):
    """API 키 리스트 조회 응답입니다."""

    blocks: Optional[List[ApiKeysOutBlock]] = Field(default=None, description="등록된 API 키 목록")
