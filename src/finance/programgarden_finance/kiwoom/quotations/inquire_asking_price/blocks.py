"""키움증권 주식호가요청 (ka10004) 요청/응답 모델입니다.

KIS는 output1(호가)/output2(예상체결)로 나뉘지만, 키움은 별도 봉투 키가
없어 하나의 최상위 블록으로 합쳐 모델링합니다.
TODO(실계좌 검증): 실제 필드명/구조 확인 필요.
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

    sel_1th_pre_req_pric: Optional[str] = Field(default=None, title="매도호가1", description="TODO(실계좌 검증): 필드명 확인")
    buy_1th_pre_req_pric: Optional[str] = Field(default=None, title="매수호가1", description="TODO(실계좌 검증): 필드명 확인")
    sel_1th_pre_req_qty: Optional[str] = Field(default=None, title="매도호가잔량1")
    buy_1th_pre_req_qty: Optional[str] = Field(default=None, title="매수호가잔량1")
    tot_sel_req: Optional[str] = Field(default=None, title="총매도호가잔량")
    tot_buy_req: Optional[str] = Field(default=None, title="총매수호가잔량")
    cur_prc: Optional[str] = Field(default=None, title="현재가")


class InquireAskingPriceResponse(KiwoomResponseBase):
    """주식호가요청 응답입니다."""

    block: Optional[InquireAskingPriceOutBlock] = Field(default=None, description="호가 정보")
