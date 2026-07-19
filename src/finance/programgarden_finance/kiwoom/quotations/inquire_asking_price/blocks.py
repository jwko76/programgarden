"""키움증권 주식호가요청 (ka10004) 요청/응답 모델입니다.

KIS는 output1(호가)/output2(예상체결)로 나뉘지만, 키움은 별도 봉투 키가
없어 하나의 최상위 블록으로 합쳐 모델링합니다.

필드명은 2026-07-18 모의서버 라이브 응답으로 확인됨: 최우선호가는
``sel_fpr_bid``/``buy_fpr_bid``(fpr = first price)이고 2~10차는
``sel_2th_pre_bid`` 형식이며 ``_bid``가 가격, ``_req``가 잔량입니다.
호가 가격에는 등락 부호(+/-)가 붙습니다.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class InquireAskingPriceInBlock(BaseModel):
    """주식호가요청 POST 바디입니다."""

    model_config = ConfigDict(populate_by_name=True)

    stk_cd: str = Field(..., title="종목코드", examples=["005930"])


class InquireAskingPriceRequest(BaseModel):
    """주식호가요청 요청입니다."""

    body: InquireAskingPriceInBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquireAskingPriceOutBlock(BaseModel):
    """호가 정보입니다. 응답 최상위 키에서 직접 추출한다고 가정합니다."""

    model_config = ConfigDict(extra="ignore")

    sel_fpr_bid: Optional[str] = Field(default=None, title="매도최우선호가", description="등락 부호(+/-) 포함")
    sel_fpr_req: Optional[str] = Field(default=None, title="매도최우선호가잔량")
    buy_fpr_bid: Optional[str] = Field(default=None, title="매수최우선호가", description="등락 부호(+/-) 포함")
    buy_fpr_req: Optional[str] = Field(default=None, title="매수최우선호가잔량")
    tot_sel_req: Optional[str] = Field(default=None, title="총매도호가잔량")
    tot_buy_req: Optional[str] = Field(default=None, title="총매수호가잔량")
    bid_req_base_tm: Optional[str] = Field(default=None, title="호가잔량기준시간", description="HHMMSS")


class InquireAskingPriceResponse(KiwoomResponseBase):
    """주식호가요청 응답입니다."""

    block: Optional[InquireAskingPriceOutBlock] = Field(default=None, description="호가 정보")
