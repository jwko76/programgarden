"""키움증권 주식 현금매수/매도 (kt10000 매수 / kt10001 매도) 요청/응답 모델입니다.

필드명은 지시된 최선 추정치를 그대로 사용합니다.
TODO(실계좌 검증): trde_tp 코드값(지정가/시장가 등) 및 dmst_stex_tp
정확한 값 확인 필요.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class OrderCashBodyBlock(BaseModel):
    """주식 현금매수/매도 요청 POST 바디입니다.

    trde_tp(매매구분/주문유형): 지정가/시장가 등 코드값 미확인.
    시장가 주문 시 ord_uv는 "0"으로 설정합니다.
    """

    model_config = ConfigDict(populate_by_name=True)

    acnt_no: str = Field(..., title="계좌번호")
    dmst_stex_tp: str = Field(
        default="KRX",
        title="국내거래소구분",
        description="KRX 등 (TODO(실계좌 검증))",
    )
    stk_cd: str = Field(..., title="종목코드", examples=["005930"])
    ord_qty: str = Field(..., title="주문수량", examples=["10"])
    ord_uv: str = Field(
        default="0",
        title="주문단가",
        description="지정가 주문 가격. 시장가는 0",
        examples=["60000"],
    )
    trde_tp: str = Field(
        default="0",
        title="매매구분(주문유형)",
        description="지정가/시장가 등 코드값 (TODO(실계좌 검증): 정확한 코드값 확인)",
    )


class OrderCashRequest(BaseModel):
    """주식 현금매수/매도 요청입니다."""

    body: OrderCashBodyBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class OrderCashOutBlock(BaseModel):
    """주문 접수 결과입니다. 응답 최상위 키에서 직접 추출한다고 가정합니다."""

    model_config = ConfigDict(extra="ignore")

    ord_no: Optional[str] = Field(default=None, title="주문번호")


class OrderCashResponse(KiwoomResponseBase):
    """주식 현금매수/매도 응답입니다."""

    block: Optional[OrderCashOutBlock] = Field(default=None, description="주문 접수 결과")
