"""KIS 주식주문(현금) (TTTC0802U 매수 / TTTC0801U 매도) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class OrderCashBodyBlock(BaseModel):
    """주식주문(현금) 요청 본문입니다.

    ORD_DVSN(주문구분): 00 지정가, 01 시장가, 03 최유리지정가, 04 최우선지정가 등.
    시장가(01) 주문 시 ORD_UNPR은 "0"으로 설정합니다.
    """

    model_config = ConfigDict(populate_by_name=True)

    cano: str = Field(..., serialization_alias="CANO", title="종합계좌번호", description="계좌번호 앞 8자리")
    acnt_prdt_cd: str = Field(default="01", serialization_alias="ACNT_PRDT_CD", title="계좌상품코드")
    pdno: str = Field(..., serialization_alias="PDNO", title="상품번호(종목코드)", examples=["005930"])
    ord_dvsn: str = Field(
        default="00",
        serialization_alias="ORD_DVSN",
        title="주문구분",
        description="00: 지정가, 01: 시장가",
    )
    ord_qty: str = Field(..., serialization_alias="ORD_QTY", title="주문수량", examples=["10"])
    ord_unpr: str = Field(
        default="0",
        serialization_alias="ORD_UNPR",
        title="주문단가",
        description="지정가 주문 가격. 시장가는 0",
        examples=["60000"],
    )


class OrderCashRequest(BaseModel):
    """주식주문(현금) 요청입니다."""

    body: OrderCashBodyBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class OrderCashOutBlock(BaseModel):
    """주문 접수 결과(output)입니다."""

    model_config = ConfigDict(extra="ignore")

    krx_fwdg_ord_orgno: Optional[str] = Field(default=None, title="한국거래소전송주문조직번호", alias="KRX_FWDG_ORD_ORGNO")
    odno: Optional[str] = Field(default=None, title="주문번호", alias="ODNO")
    ord_tmd: Optional[str] = Field(default=None, title="주문시각", description="HHMMSS", alias="ORD_TMD")


class OrderCashResponse(KisResponseBase):
    """주식주문(현금) 응답입니다."""

    block: Optional[OrderCashOutBlock] = Field(default=None, description="주문 접수 결과 (output)")
