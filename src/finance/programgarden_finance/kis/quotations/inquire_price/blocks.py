"""KIS 주식현재가 시세 (FHKST01010100) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class InquirePriceInBlock(BaseModel):
    """주식현재가 시세 쿼리 파라미터입니다."""

    model_config = ConfigDict(populate_by_name=True)

    fid_cond_mrkt_div_code: str = Field(
        default="J",
        serialization_alias="FID_COND_MRKT_DIV_CODE",
        title="시장 분류 코드",
        description="J: 주식/ETF/ETN",
    )
    fid_input_iscd: str = Field(
        ...,
        serialization_alias="FID_INPUT_ISCD",
        title="종목코드",
        description="6자리 종목코드 (ex. 005930)",
        examples=["005930"],
    )


class InquirePriceRequest(BaseModel):
    """주식현재가 시세 요청입니다."""

    params: InquirePriceInBlock = Field(..., description="요청 파라미터")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquirePriceOutBlock(BaseModel):
    """주식현재가 시세 응답(output)입니다. KIS는 모든 값을 문자열로 반환합니다."""

    model_config = ConfigDict(extra="ignore")

    stck_prpr: Optional[str] = Field(default=None, title="주식 현재가")
    prdy_vrss: Optional[str] = Field(default=None, title="전일 대비")
    prdy_vrss_sign: Optional[str] = Field(default=None, title="전일 대비 부호", description="1:상한 2:상승 3:보합 4:하한 5:하락")
    prdy_ctrt: Optional[str] = Field(default=None, title="전일 대비율(%)")
    stck_oprc: Optional[str] = Field(default=None, title="주식 시가")
    stck_hgpr: Optional[str] = Field(default=None, title="주식 최고가")
    stck_lwpr: Optional[str] = Field(default=None, title="주식 최저가")
    stck_mxpr: Optional[str] = Field(default=None, title="주식 상한가")
    stck_llam: Optional[str] = Field(default=None, title="주식 하한가")
    stck_sdpr: Optional[str] = Field(default=None, title="주식 기준가(전일 종가)")
    acml_vol: Optional[str] = Field(default=None, title="누적 거래량")
    acml_tr_pbmn: Optional[str] = Field(default=None, title="누적 거래대금")
    per: Optional[str] = Field(default=None, title="PER")
    pbr: Optional[str] = Field(default=None, title="PBR")
    eps: Optional[str] = Field(default=None, title="EPS")
    bps: Optional[str] = Field(default=None, title="BPS")
    hts_kor_isnm: Optional[str] = Field(default=None, title="HTS 한글 종목명")
    rprs_mrkt_kor_name: Optional[str] = Field(default=None, title="대표 시장 한글명")


class InquirePriceResponse(KisResponseBase):
    """주식현재가 시세 응답입니다."""

    block: Optional[InquirePriceOutBlock] = Field(default=None, description="현재가 정보 (output)")
