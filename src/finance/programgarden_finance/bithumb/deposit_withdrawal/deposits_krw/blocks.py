"""빗썸 원화 입금 리스트 조회 (GET /v1/deposits/krw) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions

DepositKrwState = Literal["PROCESSING", "ACCEPTED", "CANCELLED"]


class DepositsKrwInBlock(BaseModel):
    """원화 입금 리스트 조회 쿼리 파라미터입니다."""

    state: Optional[DepositKrwState] = Field(
        default=None,
        title="입금 상태",
        description="PROCESSING(진행중)/ACCEPTED(완료)/CANCELLED(취소)",
        examples=["ACCEPTED"],
    )
    uuids: Optional[List[str]] = Field(default=None, title="입금 고유 ID 목록")
    txids: Optional[List[str]] = Field(default=None, title="입금 TXID 목록")
    page: Optional[int] = Field(default=None, title="페이지 번호", description="기본 1", examples=[1])
    limit: Optional[int] = Field(default=None, title="조회 개수", description="기본 100, 최대 100", examples=[100])
    order_by: Optional[Literal["asc", "desc"]] = Field(
        default=None, title="정렬 방식", description="created_at 기준 정렬, 기본 desc", examples=["desc"]
    )


class DepositsKrwRequest(BaseModel):
    """원화 입금 리스트 조회 요청입니다."""

    params: DepositsKrwInBlock = Field(default_factory=DepositsKrwInBlock, description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class DepositKrwListItem(BaseModel):
    """원화 입금 리스트 조회 응답 항목입니다."""

    type: str = Field(..., title="입출금 종류", examples=["deposit"])
    uuid: str = Field(..., title="입금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["KRW"])
    txid: Optional[str] = Field(default=None, title="입금 트랜잭션 ID")
    state: str = Field(..., title="입금 상태", examples=["ACCEPTED"])
    created_at: str = Field(..., title="입금 생성 시간")
    done_at: Optional[str] = Field(default=None, title="입금 완료 시간")
    amount: str = Field(..., title="입금 금액", examples=["60000"])
    fee: str = Field(..., title="입금 수수료", examples=["0"])
    transaction_type: str = Field(..., title="입금 유형", description="default(일반입금)/internal(바로입금)")


class DepositsKrwResponse(BithumbResponseBase):
    """원화 입금 리스트 조회 응답입니다."""

    blocks: Optional[List[DepositKrwListItem]] = Field(default=None, description="원화 입금 내역 목록")
