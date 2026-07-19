"""키움증권 계좌평가잔고내역요청 (kt00018) 요청/응답 모델입니다.

계좌 요약(최상위 키)과 보유 종목 리스트 키(``acnt_evlt_remn_indv_tot``)는
2026-07-18 모의서버 라이브 응답으로 확인됨. 요약에는 예수금(entr) 필드가
없고 추정예탁자산(``prsm_dpst_aset_amt``)이 옵니다 — 예수금 상세는 별도
TR(kt00001 예수금상세현황요청, 미구현)이 필요합니다.

보유 종목 항목 내부 필드는 모의계좌에 보유 종목이 없어 라이브 미확인
(TODO(실계좌 검증): 보유 종목이 있는 계좌로 항목 필드명 확인).
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
    """보유 종목 항목입니다 (``acnt_evlt_remn_indv_tot`` 리스트의 각 원소).

    항목 내부 필드명은 보유 종목이 없는 모의계좌라 라이브 미확인 —
    TODO(실계좌 검증): 보유 종목 보유 후 필드명 확인.
    """

    model_config = ConfigDict(extra="ignore")

    stk_cd: Optional[str] = Field(default=None, title="종목코드")
    stk_nm: Optional[str] = Field(default=None, title="종목명")
    rmnd_qty: Optional[str] = Field(default=None, title="보유수량")
    trde_able_qty: Optional[str] = Field(default=None, title="거래가능수량")
    pur_pric: Optional[str] = Field(default=None, title="매입가")
    cur_prc: Optional[str] = Field(default=None, title="현재가")
    evlt_amt: Optional[str] = Field(default=None, title="평가금액")
    evltv_prft: Optional[str] = Field(default=None, title="평가손익")
    prft_rt: Optional[str] = Field(default=None, title="손익율(%)")


class InquireBalanceOutBlock2(BaseModel):
    """계좌 요약입니다 (응답 최상위 키 — 2026-07-18 모의서버 라이브 확인)."""

    model_config = ConfigDict(extra="ignore")

    prsm_dpst_aset_amt: Optional[str] = Field(default=None, title="추정예탁자산")
    tot_pur_amt: Optional[str] = Field(default=None, title="총매입금액")
    tot_evlt_amt: Optional[str] = Field(default=None, title="총평가금액")
    tot_evlt_pl: Optional[str] = Field(default=None, title="총평가손익금액")
    tot_prft_rt: Optional[str] = Field(default=None, title="총수익률(%)")
    tot_loan_amt: Optional[str] = Field(default=None, title="총대출금액")


class InquireBalanceResponse(KiwoomResponseBase):
    """계좌평가잔고내역요청 응답입니다."""

    blocks: Optional[List[InquireBalanceOutBlock1]] = Field(default=None, description="보유 종목 목록 (stk_acnt_evlt_prst)")
    block: Optional[InquireBalanceOutBlock2] = Field(default=None, description="계좌 요약")
