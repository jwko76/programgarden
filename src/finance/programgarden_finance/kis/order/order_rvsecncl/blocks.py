"""KIS 주식주문(정정취소) (TTTC0803U/VTTC0803U) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class OrderRvsecnclBodyBlock(BaseModel):
    """주식주문(정정취소) 요청 본문입니다.

    - RVSE_CNCL_DVSN_CD: 01 정정, 02 취소
    - QTY_ALL_ORD_YN: Y 잔량 전부, N 일부
    - 취소 주문 시 ORD_UNPR은 "0"으로 설정합니다.
    """

    model_config = ConfigDict(populate_by_name=True)

    cano: str = Field(..., serialization_alias="CANO", title="종합계좌번호")
    acnt_prdt_cd: str = Field(default="01", serialization_alias="ACNT_PRDT_CD", title="계좌상품코드")
    krx_fwdg_ord_orgno: str = Field(
        default="",
        serialization_alias="KRX_FWDG_ORD_ORGNO",
        title="한국거래소전송주문조직번호",
        description="원주문 접수 응답의 KRX_FWDG_ORD_ORGNO (빈 값 허용)",
    )
    orgn_odno: str = Field(
        ...,
        serialization_alias="ORGN_ODNO",
        title="원주문번호",
        description="정정/취소할 원주문의 ODNO",
    )
    ord_dvsn: str = Field(
        default="00",
        serialization_alias="ORD_DVSN",
        title="주문구분",
        description="00: 지정가, 01: 시장가",
    )
    rvse_cncl_dvsn_cd: str = Field(
        default="02",
        serialization_alias="RVSE_CNCL_DVSN_CD",
        title="정정취소구분코드",
        description="01: 정정, 02: 취소",
    )
    ord_qty: str = Field(
        default="0",
        serialization_alias="ORD_QTY",
        title="주문수량",
        description="전량 취소/정정(QTY_ALL_ORD_YN=Y) 시 0",
    )
    ord_unpr: str = Field(
        default="0",
        serialization_alias="ORD_UNPR",
        title="주문단가",
        description="취소 시 0",
    )
    qty_all_ord_yn: str = Field(
        default="Y",
        serialization_alias="QTY_ALL_ORD_YN",
        title="잔량전부주문여부",
        description="Y: 잔량 전부, N: 일부",
    )


class OrderRvsecnclRequest(BaseModel):
    """주식주문(정정취소) 요청입니다."""

    body: OrderRvsecnclBodyBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class OrderRvsecnclOutBlock(BaseModel):
    """정정취소 접수 결과(output)입니다."""

    model_config = ConfigDict(extra="ignore")

    krx_fwdg_ord_orgno: Optional[str] = Field(default=None, title="한국거래소전송주문조직번호", alias="KRX_FWDG_ORD_ORGNO")
    odno: Optional[str] = Field(default=None, title="주문번호(취소 접수 번호)", alias="ODNO")
    ord_tmd: Optional[str] = Field(default=None, title="주문시각", alias="ORD_TMD")


class OrderRvsecnclResponse(KisResponseBase):
    """주식주문(정정취소) 응답입니다."""

    block: Optional[OrderRvsecnclOutBlock] = Field(default=None, description="정정취소 접수 결과 (output)")
