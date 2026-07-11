"""KIS 주식현재가 호가/예상체결 (FHKST01010200) 요청/응답 모델입니다."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from ...models import KisResponseBase, SetupOptions


class InquireAskingPriceInBlock(BaseModel):
    """호가/예상체결 조회 쿼리 파라미터입니다."""

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


class InquireAskingPriceRequest(BaseModel):
    """호가/예상체결 조회 요청입니다."""

    params: InquireAskingPriceInBlock = Field(..., description="요청 파라미터")
    options: Optional[SetupOptions] = Field(default=None, description="요청 옵션")


class InquireAskingPriceOutBlock1(BaseModel):
    """호가 정보(output1)입니다. 매도/매수 10호가와 잔량을 담습니다."""

    model_config = ConfigDict(extra="ignore")

    askp1: Optional[str] = Field(default=None, title="매도호가 1")
    askp2: Optional[str] = Field(default=None, title="매도호가 2")
    askp3: Optional[str] = Field(default=None, title="매도호가 3")
    askp4: Optional[str] = Field(default=None, title="매도호가 4")
    askp5: Optional[str] = Field(default=None, title="매도호가 5")
    bidp1: Optional[str] = Field(default=None, title="매수호가 1")
    bidp2: Optional[str] = Field(default=None, title="매수호가 2")
    bidp3: Optional[str] = Field(default=None, title="매수호가 3")
    bidp4: Optional[str] = Field(default=None, title="매수호가 4")
    bidp5: Optional[str] = Field(default=None, title="매수호가 5")
    askp_rsqn1: Optional[str] = Field(default=None, title="매도호가 잔량 1")
    askp_rsqn2: Optional[str] = Field(default=None, title="매도호가 잔량 2")
    askp_rsqn3: Optional[str] = Field(default=None, title="매도호가 잔량 3")
    askp_rsqn4: Optional[str] = Field(default=None, title="매도호가 잔량 4")
    askp_rsqn5: Optional[str] = Field(default=None, title="매도호가 잔량 5")
    bidp_rsqn1: Optional[str] = Field(default=None, title="매수호가 잔량 1")
    bidp_rsqn2: Optional[str] = Field(default=None, title="매수호가 잔량 2")
    bidp_rsqn3: Optional[str] = Field(default=None, title="매수호가 잔량 3")
    bidp_rsqn4: Optional[str] = Field(default=None, title="매수호가 잔량 4")
    bidp_rsqn5: Optional[str] = Field(default=None, title="매수호가 잔량 5")
    total_askp_rsqn: Optional[str] = Field(default=None, title="총 매도호가 잔량")
    total_bidp_rsqn: Optional[str] = Field(default=None, title="총 매수호가 잔량")
    aspr_acpt_hour: Optional[str] = Field(default=None, title="호가 접수 시간")


class InquireAskingPriceOutBlock2(BaseModel):
    """예상체결 정보(output2)입니다."""

    model_config = ConfigDict(extra="ignore")

    antc_cnpr: Optional[str] = Field(default=None, title="예상 체결가")
    antc_cnqn: Optional[str] = Field(default=None, title="예상 체결량")
    antc_vol: Optional[str] = Field(default=None, title="예상 거래량")
    antc_cntg_vrss: Optional[str] = Field(default=None, title="예상 체결 대비")
    antc_cntg_vrss_sign: Optional[str] = Field(default=None, title="예상 체결 대비 부호")
    antc_cntg_prdy_ctrt: Optional[str] = Field(default=None, title="예상 체결 전일 대비율")
    stck_prpr: Optional[str] = Field(default=None, title="주식 현재가")


class InquireAskingPriceResponse(KisResponseBase):
    """호가/예상체결 조회 응답입니다."""

    block1: Optional[InquireAskingPriceOutBlock1] = Field(default=None, description="호가 정보 (output1)")
    block2: Optional[InquireAskingPriceOutBlock2] = Field(default=None, description="예상체결 정보 (output2)")
