"""키움증권 계좌평가잔고내역요청 (kt00018) 요청/응답 모델입니다.

필드명은 공식 문서 미확인 상태에서 키움 REST API의 일반적인 소문자
약어 스타일을 따른 최선 추정치입니다. 키움 응답은 KIS의 output/output1/
output2 같은 별도 봉투 키가 없어, 보유 종목 리스트는 이름 있는 리스트
키(``stk_acnt_evlt_prst``)로, 계좌 요약은 최상위 키로 온다고 가정합니다.
TODO(실계좌 검증): 실제 필드명/구조 확인 필요.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class InquireBalanceInBlock(BaseModel):
    """계좌평가잔고내역요청 POST 바디입니다."""

    model_config = ConfigDict(populate_by_name=True)

    acnt_no: str = Field(
        ...,
        title="계좌번호",
        description="키움 계좌번호(전체). KIS의 cano+acnt_prdt_cd 2단 구조 대신 단일 필드로 가정 (TODO(실계좌 검증)).",
    )
    qry_tp: str = Field(
        default="1",
        title="조회구분",
        description="1: 합산, 2: 개별 (TODO(실계좌 검증): 정확한 코드값 확인)",
    )
    dmst_stex_tp: str = Field(
        default="KRX",
        title="국내거래소구분",
        description="KRX 등 (TODO(실계좌 검증))",
    )


class InquireBalanceRequest(BaseModel):
    """계좌평가잔고내역요청 요청입니다."""

    body: InquireBalanceInBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquireBalanceOutBlock1(BaseModel):
    """보유 종목 항목입니다 (``stk_acnt_evlt_prst`` 리스트의 각 원소로 추정)."""

    model_config = ConfigDict(extra="ignore")

    stk_cd: Optional[str] = Field(default=None, title="종목코드")
    stk_nm: Optional[str] = Field(default=None, title="종목명")
    rmnd_qty: Optional[str] = Field(default=None, title="보유수량")
    pur_pric: Optional[str] = Field(default=None, title="매입가")
    cur_prc: Optional[str] = Field(default=None, title="현재가")
    evlt_amt: Optional[str] = Field(default=None, title="평가금액")
    evltv_prft: Optional[str] = Field(default=None, title="평가손익")
    pl_rt: Optional[str] = Field(default=None, title="손익율(%)")


class InquireBalanceOutBlock2(BaseModel):
    """계좌 요약입니다. 응답 최상위 키에서 직접 추출한다고 가정합니다."""

    model_config = ConfigDict(extra="ignore")

    entr: Optional[str] = Field(default=None, title="예수금")
    tot_pur_amt: Optional[str] = Field(default=None, title="총매입금액")
    tot_evlt_amt: Optional[str] = Field(default=None, title="총평가금액")
    tot_evlt_pl: Optional[str] = Field(default=None, title="총평가손익금액")
    tot_pl_rt: Optional[str] = Field(default=None, title="총손익율(%)")


class InquireBalanceResponse(KiwoomResponseBase):
    """계좌평가잔고내역요청 응답입니다."""

    blocks: Optional[List[InquireBalanceOutBlock1]] = Field(default=None, description="보유 종목 목록 (stk_acnt_evlt_prst)")
    block: Optional[InquireBalanceOutBlock2] = Field(default=None, description="계좌 요약")
