"""빗썸 입출금 현황 조회 (GET /v1/status/wallet) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class WalletStatusInBlock(BaseModel):
    """입출금 현황 조회는 쿼리 파라미터가 없습니다."""


class WalletStatusRequest(BaseModel):
    """입출금 현황 조회 요청입니다."""

    params: WalletStatusInBlock = Field(default_factory=WalletStatusInBlock, description="요청 파라미터 (없음)")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WalletStatusOutBlock(BaseModel):
    """입출금 현황 조회 응답 항목 (화폐/네트워크별 입출금 상태)입니다."""

    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    wallet_state: str = Field(
        ...,
        title="입출금 상태",
        description="working(입출금 가능)/withdraw_only(출금만 가능)/deposit_only(입금만 가능)/paused(입출금 중단)/unsupported(지원안함)",
        examples=["working"],
    )
    block_state: str = Field(
        ...,
        title="블록 상태",
        description="normal(정상)/delayed(지연)/inactive(비활성)",
        examples=["normal"],
    )
    block_height: int = Field(..., title="블록 높이", examples=[860000])
    block_updated_at: str = Field(..., title="블록 정보 갱신 시각", examples=["2026-06-14T11:00:00+09:00"])
    block_elapsed_minutes: int = Field(..., title="블록 정보 갱신 이후 경과된 시간(분)", examples=[5])
    net_type: str = Field(..., title="입출금 네트워크 타입", examples=["BTC"])


class WalletStatusResponse(BithumbResponseBase):
    """입출금 현황 조회 응답입니다."""

    blocks: Optional[List[WalletStatusOutBlock]] = Field(default=None, description="화폐/네트워크별 입출금 상태 목록")
