"""빗썸 입금 리스트 조회 (GET /v1/deposits) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions

DepositState = Literal[
    "submitting", "submitted", "almost_accepted", "rejected", "accepted", "processing", "done", "canceled"
]


class DepositsInBlock(BaseModel):
    """입금 리스트 조회 쿼리 파라미터입니다."""

    currency: Optional[str] = Field(default=None, title="화폐 코드", examples=["BTC"])
    state: Optional[DepositState] = Field(
        default=None,
        title="입금 상태",
        description="submitting/submitted/almost_accepted/rejected/accepted/processing/done/canceled",
        examples=["done"],
    )
    uuids: Optional[List[str]] = Field(default=None, title="입금 UUID 목록")
    txids: Optional[List[str]] = Field(default=None, title="입금 트랜잭션 ID 목록")
    limit: Optional[int] = Field(default=None, title="조회 개수", description="기본 100, 최대 100", examples=[100])
    page: Optional[int] = Field(default=None, title="페이지 번호", description="기본 1", examples=[1])
    order_by: Optional[Literal["asc", "desc"]] = Field(
        default=None, title="정렬 방식", description="created_at 기준 정렬, 기본 desc", examples=["desc"]
    )


class DepositsRequest(BaseModel):
    """입금 리스트 조회 요청입니다."""

    params: DepositsInBlock = Field(default_factory=DepositsInBlock, description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositOutBlock(BaseModel):
    """입금 리스트 조회 응답 항목입니다."""

    type: str = Field(..., title="입출금 종류", examples=["deposit"])
    uuid: str = Field(..., title="입금에 대한 고유 아이디", examples=["94332e99-3a87-4a35-ad98-28b0c969f830"])
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["BTC"])
    net_type: Optional[str] = Field(default=None, title="입금 네트워크", examples=["BTC"])
    txid: Optional[str] = Field(default=None, title="입금 트랜잭션 ID")
    state: str = Field(..., title="입금 상태", examples=["done"])
    created_at: str = Field(..., title="입금 생성 시간", examples=["2026-06-10T12:30:00+09:00"])
    done_at: Optional[str] = Field(default=None, title="입금 완료 시간", examples=["2026-06-10T12:40:00+09:00"])
    amount: str = Field(..., title="입금 금액/수량", examples=["1.0"])
    fee: str = Field(..., title="입금 수수료", examples=["0.0"])
    transaction_type: str = Field(..., title="입금 유형", description="default(일반입금)/internal(바로입금)", examples=["default"])


class DepositsResponse(BithumbResponseBase):
    """입금 리스트 조회 응답입니다."""

    blocks: Optional[List[DepositOutBlock]] = Field(default=None, description="입금 내역 목록")
