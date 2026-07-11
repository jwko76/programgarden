"""KIS 국내주식 기간별 시세 (FHKST03010100) 요청/응답 모델입니다."""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class InquireDailyItemChartPriceInBlock(BaseModel):
    """기간별 시세 조회 쿼리 파라미터입니다."""

    model_config = ConfigDict(populate_by_name=True)

    fid_cond_mrkt_div_code: str = Field(
        default="J",
        serialization_alias="FID_COND_MRKT_DIV_CODE",
        title="시장 분류 코드",
    )
    fid_input_iscd: str = Field(
        ...,
        serialization_alias="FID_INPUT_ISCD",
        title="종목코드",
        examples=["005930"],
    )
    fid_input_date_1: str = Field(
        ...,
        serialization_alias="FID_INPUT_DATE_1",
        title="조회 시작일자",
        description="YYYYMMDD",
        examples=["20260101"],
    )
    fid_input_date_2: str = Field(
        ...,
        serialization_alias="FID_INPUT_DATE_2",
        title="조회 종료일자",
        description="YYYYMMDD",
        examples=["20260711"],
    )
    fid_period_div_code: str = Field(
        default="D",
        serialization_alias="FID_PERIOD_DIV_CODE",
        title="기간 분류 코드",
        description="D: 일봉, W: 주봉, M: 월봉, Y: 년봉",
    )
    fid_org_adj_prc: str = Field(
        default="0",
        serialization_alias="FID_ORG_ADJ_PRC",
        title="수정주가 여부",
        description="0: 수정주가, 1: 원주가",
    )


class InquireDailyItemChartPriceRequest(BaseModel):
    """기간별 시세 조회 요청입니다."""

    params: InquireDailyItemChartPriceInBlock = Field(..., description="요청 파라미터")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquireDailyItemChartPriceOutBlock1(BaseModel):
    """종목 현재 정보(output1)입니다."""

    model_config = ConfigDict(extra="ignore")

    stck_prpr: Optional[str] = Field(default=None, title="주식 현재가")
    prdy_vrss: Optional[str] = Field(default=None, title="전일 대비")
    prdy_ctrt: Optional[str] = Field(default=None, title="전일 대비율")
    hts_kor_isnm: Optional[str] = Field(default=None, title="HTS 한글 종목명")
    stck_shrn_iscd: Optional[str] = Field(default=None, title="주식 단축 종목코드")


class InquireDailyItemChartPriceOutBlock2(BaseModel):
    """일봉 캔들(output2 항목)입니다. 최신 캔들이 배열 앞쪽에 옵니다."""

    model_config = ConfigDict(extra="ignore")

    stck_bsop_date: Optional[str] = Field(default=None, title="영업일자", description="YYYYMMDD")
    stck_oprc: Optional[str] = Field(default=None, title="시가")
    stck_hgpr: Optional[str] = Field(default=None, title="고가")
    stck_lwpr: Optional[str] = Field(default=None, title="저가")
    stck_clpr: Optional[str] = Field(default=None, title="종가")
    acml_vol: Optional[str] = Field(default=None, title="누적 거래량")
    acml_tr_pbmn: Optional[str] = Field(default=None, title="누적 거래대금")
    prdy_vrss: Optional[str] = Field(default=None, title="전일 대비")
    prdy_vrss_sign: Optional[str] = Field(default=None, title="전일 대비 부호")


class InquireDailyItemChartPriceResponse(KisResponseBase):
    """기간별 시세 조회 응답입니다."""

    block1: Optional[InquireDailyItemChartPriceOutBlock1] = Field(default=None, description="종목 현재 정보 (output1)")
    blocks: Optional[List[InquireDailyItemChartPriceOutBlock2]] = Field(default=None, description="일봉 캔들 목록 (output2)")
