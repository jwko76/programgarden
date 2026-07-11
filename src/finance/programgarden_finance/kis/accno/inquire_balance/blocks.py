"""KIS 주식잔고조회 (TTTC8434R/VTTC8434R) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class InquireBalanceInBlock(BaseModel):
    """주식잔고조회 쿼리 파라미터입니다."""

    model_config = ConfigDict(populate_by_name=True)

    cano: str = Field(
        ...,
        serialization_alias="CANO",
        title="종합계좌번호",
        description="계좌번호 앞 8자리",
    )
    acnt_prdt_cd: str = Field(
        default="01",
        serialization_alias="ACNT_PRDT_CD",
        title="계좌상품코드",
        description="계좌번호 뒤 2자리",
    )
    afhr_flpr_yn: str = Field(default="N", serialization_alias="AFHR_FLPR_YN", title="시간외단일가여부")
    ofl_yn: str = Field(default="", serialization_alias="OFL_YN", title="오프라인여부")
    inqr_dvsn: str = Field(default="02", serialization_alias="INQR_DVSN", title="조회구분", description="01: 대출일별, 02: 종목별")
    unpr_dvsn: str = Field(default="01", serialization_alias="UNPR_DVSN", title="단가구분")
    fund_sttl_icld_yn: str = Field(default="N", serialization_alias="FUND_STTL_ICLD_YN", title="펀드결제분포함여부")
    fncg_amt_auto_rdpt_yn: str = Field(default="N", serialization_alias="FNCG_AMT_AUTO_RDPT_YN", title="융자금액자동상환여부")
    prcs_dvsn: str = Field(default="00", serialization_alias="PRCS_DVSN", title="처리구분", description="00: 전일매매포함, 01: 전일매매미포함")
    ctx_area_fk100: str = Field(default="", serialization_alias="CTX_AREA_FK100", title="연속조회검색조건100")
    ctx_area_nk100: str = Field(default="", serialization_alias="CTX_AREA_NK100", title="연속조회키100")


class InquireBalanceRequest(BaseModel):
    """주식잔고조회 요청입니다."""

    params: InquireBalanceInBlock = Field(..., description="요청 파라미터")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquireBalanceOutBlock1(BaseModel):
    """보유 종목 항목(output1)입니다."""

    model_config = ConfigDict(extra="ignore")

    pdno: Optional[str] = Field(default=None, title="상품번호(종목코드)")
    prdt_name: Optional[str] = Field(default=None, title="상품명(종목명)")
    hldg_qty: Optional[str] = Field(default=None, title="보유수량")
    ord_psbl_qty: Optional[str] = Field(default=None, title="주문가능수량")
    pchs_avg_pric: Optional[str] = Field(default=None, title="매입평균가격")
    pchs_amt: Optional[str] = Field(default=None, title="매입금액")
    prpr: Optional[str] = Field(default=None, title="현재가")
    evlu_amt: Optional[str] = Field(default=None, title="평가금액")
    evlu_pfls_amt: Optional[str] = Field(default=None, title="평가손익금액")
    evlu_pfls_rt: Optional[str] = Field(default=None, title="평가손익율(%)")
    trad_dvsn_name: Optional[str] = Field(default=None, title="매매구분명")


class InquireBalanceOutBlock2(BaseModel):
    """계좌 요약(output2)입니다."""

    model_config = ConfigDict(extra="ignore")

    dnca_tot_amt: Optional[str] = Field(default=None, title="예수금총금액")
    nxdy_excc_amt: Optional[str] = Field(default=None, title="익일정산금액(D+1 예수금)")
    prvs_rcdl_excc_amt: Optional[str] = Field(default=None, title="가수도정산금액(D+2 예수금)")
    tot_evlu_amt: Optional[str] = Field(default=None, title="총평가금액")
    pchs_amt_smtl_amt: Optional[str] = Field(default=None, title="매입금액합계금액")
    evlu_amt_smtl_amt: Optional[str] = Field(default=None, title="평가금액합계금액")
    evlu_pfls_smtl_amt: Optional[str] = Field(default=None, title="평가손익합계금액")
    nass_amt: Optional[str] = Field(default=None, title="순자산금액")


class InquireBalanceResponse(KisResponseBase):
    """주식잔고조회 응답입니다."""

    blocks: Optional[List[InquireBalanceOutBlock1]] = Field(default=None, description="보유 종목 목록 (output1)")
    block2: Optional[InquireBalanceOutBlock2] = Field(default=None, description="계좌 요약 (output2)")
