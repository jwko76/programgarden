"""키움증권 주식일봉차트조회요청 (ka10081) 요청/응답 모델입니다.

캔들 목록은 이름 있는 리스트 키(``stk_dt_pole``)로 온다고 가정합니다.
TODO(실계좌 검증): 실제 필드명/리스트 키 확인 필요.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KiwoomResponseBase, SetupOptions


class InquireDailyItemChartPriceInBlock(BaseModel):
    """주식일봉차트조회요청 POST 바디입니다."""

    model_config = ConfigDict(populate_by_name=True)

    stk_cd: str = Field(..., title="종목코드", examples=["005930"])
    base_dt: str = Field(..., title="기준일자", description="YYYYMMDD", examples=["20260711"])
    upd_stkpc_tp: str = Field(
        default="1",
        title="수정주가구분",
        description="0: 원주가, 1: 수정주가 (TODO(실계좌 검증): 정확한 코드값 확인)",
    )


class InquireDailyItemChartPriceRequest(BaseModel):
    """주식일봉차트조회요청 요청입니다."""

    body: InquireDailyItemChartPriceInBlock = Field(..., description="요청 본문")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquireDailyItemChartPriceOutCandle(BaseModel):
    """일봉 캔들입니다 (``stk_dt_pole`` 리스트의 각 원소로 추정)."""

    model_config = ConfigDict(extra="ignore")

    dt: Optional[str] = Field(default=None, title="일자", description="YYYYMMDD")
    open_pric: Optional[str] = Field(default=None, title="시가")
    high_pric: Optional[str] = Field(default=None, title="고가")
    low_pric: Optional[str] = Field(default=None, title="저가")
    cur_prc: Optional[str] = Field(default=None, title="종가(현재가)")
    trde_qty: Optional[str] = Field(default=None, title="거래량")


class InquireDailyItemChartPriceResponse(KiwoomResponseBase):
    """주식일봉차트조회요청 응답입니다."""

    blocks: Optional[List[InquireDailyItemChartPriceOutCandle]] = Field(
        default=None, description="일봉 캔들 목록 (stk_dt_pole)"
    )
