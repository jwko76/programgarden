"""키움증권 실시간 주문체결통보 (type "00") 응답 모델입니다.

필드명은 공식 문서 미확인 상태의 최선 추정치입니다.
TODO(실계좌 검증): 실제 필드명 확인 필요.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderNoticeRealResponse(BaseModel):
    """실시간 주문체결통보 응답입니다."""

    model_config = ConfigDict(extra="ignore")

    type: Optional[str] = Field(default="00", title="실시간 타입")
    acnt_no: Optional[str] = Field(default=None, title="계좌번호")
    ord_no: Optional[str] = Field(default=None, title="주문번호")
    orig_ord_no: Optional[str] = Field(default=None, title="원주문번호")
    stk_cd: Optional[str] = Field(default=None, title="종목코드")
    ord_qty: Optional[str] = Field(default=None, title="주문수량")
    cntr_qty: Optional[str] = Field(default=None, title="체결수량")
    cntr_uv: Optional[str] = Field(default=None, title="체결단가")
    ord_stt: Optional[str] = Field(default=None, title="주문상태", description="접수/체결/거부 등 (TODO(실계좌 검증))")
    cntr_tm: Optional[str] = Field(default=None, title="체결시간", description="HHMMSS")
