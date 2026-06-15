"""빗썸 원화 출금 리스트 조회 (GET /v1/withdraws/krw) 요청/응답 모델입니다."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ...models import BithumbResponseBase, SetupOptions

WithdrawKrwState = Literal["PROCESSING", "DONE", "CANCELLED"]


class WithdrawsKrwInBlock(BaseModel):
    """원화 출금 리스트 조회 쿼리 파라미터입니다."""

    state: Optional[WithdrawKrwState] = Field(
        default=None,
        title="출금 상태",
        description="PROCESSING(진행중)/DONE(완료)/CANCELLED(취소)",
        examples=["DONE"],
    )
    uuids: Optional[List[str]] = Field(default=None, title="출금 고유 ID 목록")
    txids: Optional[List[str]] = Field(default=None, title="출금 TXID 목록")
    page: Optional[int] = Field(default=None, title="페이지 번호", description="기본 1", examples=[1])
    limit: Optional[int] = Field(default=None, title="조회 개수", description="기본 100, 최대 100", examples=[100])
    order_by: Optional[Literal["asc", "desc"]] = Field(
        default=None, title="정렬 방식", description="created_at 기준 정렬, 기본 desc", examples=["desc"]
    )


class WithdrawsKrwRequest(BaseModel):
    """원화 출금 리스트 조회 요청입니다."""

    params: WithdrawsKrwInBlock = Field(default_factory=WithdrawsKrwInBlock, description="요청 파라미터")
    options: SetupOptions = Field(
        default_factory=lambda: SetupOptions(rate_limit_count=120),
        description="요청 옵션 (Private API rate limit 적용)",
    )


class WithdrawKrwListItem(BaseModel):
    """원화 출금 리스트 조회 응답 항목입니다."""

    type: str = Field(..., title="입출금 종류", examples=["withdraw"])
    uuid: str = Field(..., title="출금에 대한 고유 아이디")
    currency: str = Field(..., title="화폐를 의미하는 영문 대문자 코드", examples=["KRW"])
    net_type: Optional[str] = Field(default=None, title="출금 네트워크", description="원화 출금은 null입니다.")
    txid: Optional[str] = Field(default=None, title="출금 트랜잭션 ID")
    state: str = Field(..., title="출금 상태", examples=["DONE"])
    created_at: str = Field(..., title="출금 생성 시각")
    done_at: Optional[str] = Field(default=None, title="출금 완료 시각")
    amount: str = Field(..., title="출금 금액", examples=["6000"])
    fee: str = Field(..., title="출금 수수료", examples=["1000"])
    transaction_type: str = Field(..., title="출금 유형", description="default(일반출금)")


class WithdrawsKrwResponse(BithumbResponseBase):
    """원화 출금 리스트 조회 응답입니다."""

    blocks: Optional[List[WithdrawKrwListItem]] = Field(default=None, description="원화 출금 내역 목록")
