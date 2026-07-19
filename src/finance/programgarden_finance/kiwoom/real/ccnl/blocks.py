"""키움증권 실시간 주식체결 (type "0B") 응답 모델입니다.

KIS는 파이프 구분 위치 기반 필드지만, 키움은 JSON 메시지이므로 필드명
기반으로 직접 파싱합니다(``model_validate``). 필드명은 공식 문서 미확인
상태의 최선 추정치입니다.
TODO(실계좌 검증): 실제 필드명 확인 필요.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CcnlRealResponse(BaseModel):
    """실시간 주식체결 응답입니다."""

    model_config = ConfigDict(extra="ignore")

    type: Optional[str] = Field(default="0B", title="실시간 타입")
    item: Optional[str] = Field(default=None, title="종목코드")
    cur_prc: Optional[str] = Field(default=None, title="현재가")
    pred_pre: Optional[str] = Field(default=None, title="전일대비")
    flu_rt: Optional[str] = Field(default=None, title="등락률(%)")
    cntr_qty: Optional[str] = Field(default=None, title="체결량")
    acc_trde_qty: Optional[str] = Field(default=None, title="누적거래량")
    cntr_tm: Optional[str] = Field(default=None, title="체결시간", description="HHMMSS")
    open_pric: Optional[str] = Field(default=None, title="시가")
    high_pric: Optional[str] = Field(default=None, title="고가")
    low_pric: Optional[str] = Field(default=None, title="저가")
