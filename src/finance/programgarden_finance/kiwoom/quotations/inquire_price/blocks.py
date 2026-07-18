"""키움증권 종목기본정보요청 (ka10001, 현재가 포함) 요청/응답 모델입니다.

키움 필드명은 KIS의 UPPER_SNAKE 별칭과 달리 이미 소문자 약어이므로
별도 serialization_alias가 필요 없다고 가정합니다.
TODO(실계좌 검증): 실제 필드명 확인 필요.
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
    per: Optional[str] = Field(default=None, title="PER", description="TODO(실계좌 검증): 필드명 확인")
    pbr: Optional[str] = Field(default=None, title="PBR", description="TODO(실계좌 검증): 필드명 확인")


class InquirePriceResponse(KiwoomResponseBase):
    """종목기본정보요청 응답입니다."""

    block: Optional[InquirePriceOutBlock] = Field(default=None, description="현재가/종목기본정보")
