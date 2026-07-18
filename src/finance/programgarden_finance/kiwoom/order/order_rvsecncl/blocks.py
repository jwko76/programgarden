"""키움증권 주식 정정/취소 (kt10002 정정 / kt10003 취소) 요청/응답 모델입니다.

KIS는 하나의 TR(TTTC0803U)에 RVSE_CNCL_DVSN_CD 필드로 정정/취소를
구분하지만, 키움은 api-id 자체가 다릅니다(kt10002/kt10003). 따라서 이
바디 모델에는 정정/취소 구분 필드가 없고, TR 모듈(``TrOrderRvsecncl``)
생성 시 ``mode`` 인자로 api-id를 선택합니다.
TODO(실계좌 검증): 필드명/필수 여부 확인.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class OrderRvsecnclBodyBlock(BaseModel):
    """주식 정정/취소 요청 POST 바디입니다.

    취소 주문 시 ord_uv는 "0"으로 설정합니다.
    """

    model_config = ConfigDict(populate_by_name=True)

    acnt_no: str = Field(..., title="계좌번호")
    dmst_stex_tp: str = Field(
        default="KRX",
        title="국내거래소구분",
        description="KRX 등 (TODO(실계좌 검증))",
    )
    orig_ord_no: str = Field(
        ...,
        title="원주문번호",
        description="정정/취소할 원주문의 주문번호",
    )
    stk_cd: str = Field(..., title="종목코드", examples=["005930"])
    ord_qty: str = Field(
        default="0",
        title="주문수량",
        description="정정/취소 수량. 잔량 전부 처리 규칙은 미확인 (TODO(실계좌 검증))",
    )
    ord_uv: str = Field(
        default="0",
        title="주문단가",
        description="취소 시 0. 정정 시 신규 단가",
    )
    trde_tp: str = Field(
        default="0",
        title="매매구분(주문유형)",
        description="지정가/시장가 등 코드값 (TODO(실계좌 검증): 정확한 코드값 확인)",
    )


class OrderRvsecnclRequest(BaseModel):
    """주식 정정/취소 요청입니다."""

    body: OrderRvsecnclBodyBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class OrderRvsecnclOutBlock(BaseModel):
    """정정/취소 접수 결과입니다. 응답 최상위 키에서 직접 추출한다고 가정합니다."""

    model_config = ConfigDict(extra="ignore")

    ord_no: Optional[str] = Field(default=None, title="주문번호(정정/취소 접수 번호)")


class OrderRvsecnclResponse(KiwoomResponseBase):
    """주식 정정/취소 응답입니다."""

    block: Optional[OrderRvsecnclOutBlock] = Field(default=None, description="정정/취소 접수 결과")
