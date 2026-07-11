"""KIS 매수가능조회 (TTTC8908R/VTTC8908R) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class InquirePsblOrderInBlock(BaseModel):
    """매수가능조회 쿼리 파라미터입니다."""

    model_config = ConfigDict(populate_by_name=True)

    cano: str = Field(..., serialization_alias="CANO", title="종합계좌번호")
    acnt_prdt_cd: str = Field(default="01", serialization_alias="ACNT_PRDT_CD", title="계좌상품코드")
    pdno: str = Field(..., serialization_alias="PDNO", title="상품번호(종목코드)", examples=["005930"])
    ord_unpr: str = Field(
        default="0",
        serialization_alias="ORD_UNPR",
        title="주문단가",
        description="시장가 확인 시 0",
    )
    ord_dvsn: str = Field(
        default="01",
        serialization_alias="ORD_DVSN",
        title="주문구분",
        description="00: 지정가, 01: 시장가",
    )
    cma_evlu_amt_icld_yn: str = Field(default="N", serialization_alias="CMA_EVLU_AMT_ICLD_YN", title="CMA평가금액포함여부")
    ovrs_icld_yn: str = Field(default="N", serialization_alias="OVRS_ICLD_YN", title="해외포함여부")


class InquirePsblOrderRequest(BaseModel):
    """매수가능조회 요청입니다."""

    params: InquirePsblOrderInBlock = Field(..., description="요청 파라미터")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquirePsblOrderOutBlock(BaseModel):
    """매수가능 정보(output)입니다."""

    model_config = ConfigDict(extra="ignore")

    ord_psbl_cash: Optional[str] = Field(default=None, title="주문가능현금")
    nrcvb_buy_amt: Optional[str] = Field(default=None, title="미수없는매수금액")
    nrcvb_buy_qty: Optional[str] = Field(default=None, title="미수없는매수수량")
    max_buy_amt: Optional[str] = Field(default=None, title="최대매수금액")
    max_buy_qty: Optional[str] = Field(default=None, title="최대매수수량")
    psbl_qty_calc_unpr: Optional[str] = Field(default=None, title="가능수량계산단가")


class InquirePsblOrderResponse(KisResponseBase):
    """매수가능조회 응답입니다."""

    block: Optional[InquirePsblOrderOutBlock] = Field(default=None, description="매수가능 정보 (output)")
