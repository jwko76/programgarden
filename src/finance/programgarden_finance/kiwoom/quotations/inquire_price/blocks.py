"""키움증권 종목기본정보요청 (ka10001, 현재가 포함) 요청/응답 모델입니다.

필드명은 2026-07-18 모의서버 라이브 응답으로 전부 확인됨. 가격 필드
(cur_prc/open_pric/high_pric/low_pric/pred_pre)에는 등락 부호(+/-)가
붙으므로 절대값 처리가 필요합니다. 응답에는 여기 정의된 것 외에도
eps/roe/bps/시총(mac) 등 재무 필드가 다수 포함됩니다 (extra="ignore").
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class InquirePriceInBlock(BaseModel):
    """종목기본정보요청 POST 바디입니다."""

    model_config = ConfigDict(populate_by_name=True)

    stk_cd: str = Field(
        ...,
        title="종목코드",
        description="6자리 종목코드 (ex. 005930)",
        examples=["005930"],
    )


class InquirePriceRequest(BaseModel):
    """종목기본정보요청 요청입니다."""

    body: InquirePriceInBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquirePriceOutBlock(BaseModel):
    """종목기본정보(현재가) 응답입니다. 응답 최상위 키에서 직접 추출한다고 가정합니다."""

    model_config = ConfigDict(extra="ignore")

    stk_cd: Optional[str] = Field(default=None, title="종목코드")
    stk_nm: Optional[str] = Field(default=None, title="종목명")
    cur_prc: Optional[str] = Field(default=None, title="현재가")
    pred_pre: Optional[str] = Field(default=None, title="전일대비")
    flu_rt: Optional[str] = Field(default=None, title="등락률(%)")
    open_pric: Optional[str] = Field(default=None, title="시가")
    high_pric: Optional[str] = Field(default=None, title="고가")
    low_pric: Optional[str] = Field(default=None, title="저가")
    trde_qty: Optional[str] = Field(default=None, title="거래량")
    per: Optional[str] = Field(default=None, title="PER")
    pbr: Optional[str] = Field(default=None, title="PBR")


class InquirePriceResponse(KiwoomResponseBase):
    """종목기본정보요청 응답입니다."""

    block: Optional[InquirePriceOutBlock] = Field(default=None, description="현재가/종목기본정보")
