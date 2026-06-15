"""빗썸 최근 체결 내역 조회 (GET /v1/trades/ticks) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions


class TradesTicksInBlock(BaseModel):
    """최근 체결 내역 조회 쿼리 파라미터입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    to: Optional[str] = Field(
        default=None,
        title="마지막 체결 시각",
        description="HHmmss 또는 HH:mm:ss 형식 (KST 기준). 비워서 요청 시 가장 최근 체결 기준",
        examples=["120000"],
    )
    count: Optional[int] = Field(default=None, title="체결 개수", description="최대 500개", examples=[100])
    cursor: Optional[str] = Field(
        default=None, title="페이지네이션 커서", description="응답의 sequential_id를 다음 요청의 cursor로 사용"
    )
    daysAgo: Optional[int] = Field(
        default=None, title="과거 데이터 조회", description="최근 7일 이내 데이터 조회 (1~7)", examples=[1]
    )


class TradesTicksRequest(BaseModel):
    """최근 체결 내역 조회 요청입니다."""

    params: TradesTicksInBlock = Field(..., description="요청 파라미터")
    options: SetupOptions = Field(default_factory=SetupOptions, description="요청 옵션")


class TradesTicksOutBlock(BaseModel):
    """최근 체결 내역 조회 응답 항목입니다."""

    market: str = Field(..., title="마켓 코드", examples=["KRW-BTC"])
    trade_date_utc: str = Field(..., title="체결 일자(UTC)", description="yyyy-MM-dd", examples=["2026-06-14"])
    trade_time_utc: str = Field(..., title="체결 시각(UTC)", description="HH:mm:ss", examples=["03:34:56"])
    timestamp: int = Field(..., title="체결 타임스탬프(ms)", examples=[1749900896123])
    trade_price: float = Field(..., title="체결 가격", examples=[95500000.0])
    trade_volume: float = Field(..., title="체결량", examples=[0.0123])
    prev_closing_price: float = Field(..., title="전일 종가", examples=[94800000.0])
    change_price: float = Field(..., title="전일 종가 대비 변화액", examples=[700000.0])
    ask_bid: str = Field(..., title="매도/매수 구분", description="ASK(매도)/BID(매수)", examples=["BID"])
    sequential_id: int = Field(..., title="체결 번호", description="페이지네이션 커서로 사용 가능", examples=[1749900896123001])


class TradesTicksResponse(BithumbResponseBase):
    """최근 체결 내역 조회 응답입니다."""

    blocks: Optional[List[TradesTicksOutBlock]] = Field(default=None, description="최근 체결 내역 목록")
