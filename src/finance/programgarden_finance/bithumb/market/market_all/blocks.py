"""빗썸 거래대상목록 조회 (GET /v1/market/all) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class MarketAllInBlock(BaseModel):
    """거래대상목록 조회 쿼리 파라미터입니다."""

    isDetails: Optional[bool] = Field(
        default=None,
        title="유의종목 필드 노출 여부",
        description="true일 경우 market_warning 필드를 포함한 상세 정보를 반환합니다.",
        examples=[True],
    )


class MarketAllRequest(BaseModel):
    """거래대상목록 조회 요청입니다."""

    params: MarketAllInBlock = Field(default_factory=MarketAllInBlock, description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class MarketAllOutBlock(BaseModel):
    """거래대상목록 조회 응답 항목입니다."""

    market: str = Field(..., title="마켓 코드", description="ex. KRW-BTC", examples=["KRW-BTC"])
    korean_name: str = Field(..., title="한글명", examples=["비트코인"])
    english_name: str = Field(..., title="영문명", examples=["Bitcoin"])
    market_warning: Optional[str] = Field(
        default=None,
        title="유의 종목 여부",
        description="NONE(해당 없음) 또는 CAUTION(투자유의)",
        examples=["NONE"],
    )


class MarketAllResponse(BithumbResponseBase):
    """거래대상목록 조회 응답입니다."""

    blocks: Optional[List[MarketAllOutBlock]] = Field(default=None, description="거래 가능한 마켓 목록")
