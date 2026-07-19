"""KIS 국내주식 실시간 호가 (H0STASP0) 응답 모델입니다.

데이터는 ``^`` 구분 위치 기반 필드로 수신됩니다. 호가 1~3단계와 총잔량 등
주요 필드만 매핑하며, 전체 원본 필드는 ``raw_fields`` 로 접근할 수 있습니다.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# H0STASP0 필드 순서 (KIS Developers 실시간 호가 명세)
# 0: 종목코드, 1: 영업시간, 2: 시간구분코드,
# 3~12: 매도호가1~10, 13~22: 매수호가1~10,
# 23~32: 매도호가잔량1~10, 33~42: 매수호가잔량1~10,
# 43: 총매도호가잔량, 44: 총매수호가잔량,
# 45: 시간외총매도호가잔량, 46: 시간외총매수호가잔량,
# 47: 예상체결가, 48: 예상체결량
ASKING_PRICE_FIELD_INDEX = {
    "mksc_shrn_iscd": 0,     # 유가증권 단축 종목코드
    "bsop_hour": 1,          # 영업 시간 (HHMMSS)
    "hour_cls_code": 2,      # 시간 구분 코드 (0: 장중)
    "askp1": 3,              # 매도호가1
    "askp2": 4,
    "askp3": 5,
    "bidp1": 13,             # 매수호가1
    "bidp2": 14,
    "bidp3": 15,
    "askp_rsqn1": 23,        # 매도호가잔량1
    "askp_rsqn2": 24,
    "askp_rsqn3": 25,
    "bidp_rsqn1": 33,        # 매수호가잔량1
    "bidp_rsqn2": 34,
    "bidp_rsqn3": 35,
    "total_askp_rsqn": 43,   # 총매도호가잔량
    "total_bidp_rsqn": 44,   # 총매수호가잔량
    "antc_cnpr": 47,         # 예상체결가
    "antc_cnqn": 48,         # 예상체결량
}


class AskingPriceRealResponse(BaseModel):
    """실시간 호가 응답입니다."""

    model_config = ConfigDict(extra="ignore")

    tr_id: str = Field(default="H0STASP0", title="TR ID")
    mksc_shrn_iscd: Optional[str] = Field(default=None, title="종목코드")
    bsop_hour: Optional[str] = Field(default=None, title="영업 시간", description="HHMMSS")
    hour_cls_code: Optional[str] = Field(default=None, title="시간 구분 코드", description="0: 장중")
    askp1: Optional[str] = Field(default=None, title="매도호가1")
    askp2: Optional[str] = Field(default=None, title="매도호가2")
    askp3: Optional[str] = Field(default=None, title="매도호가3")
    bidp1: Optional[str] = Field(default=None, title="매수호가1")
    bidp2: Optional[str] = Field(default=None, title="매수호가2")
    bidp3: Optional[str] = Field(default=None, title="매수호가3")
    askp_rsqn1: Optional[str] = Field(default=None, title="매도호가잔량1")
    askp_rsqn2: Optional[str] = Field(default=None, title="매도호가잔량2")
    askp_rsqn3: Optional[str] = Field(default=None, title="매도호가잔량3")
    bidp_rsqn1: Optional[str] = Field(default=None, title="매수호가잔량1")
    bidp_rsqn2: Optional[str] = Field(default=None, title="매수호가잔량2")
    bidp_rsqn3: Optional[str] = Field(default=None, title="매수호가잔량3")
    total_askp_rsqn: Optional[str] = Field(default=None, title="총매도호가잔량")
    total_bidp_rsqn: Optional[str] = Field(default=None, title="총매수호가잔량")
    antc_cnpr: Optional[str] = Field(default=None, title="예상체결가")
    antc_cnqn: Optional[str] = Field(default=None, title="예상체결량")
    raw_fields: Optional[List[str]] = Field(default=None, description="원본 전체 필드", repr=False)
    error_msg: Optional[str] = Field(default=None, description="파싱 에러 메시지")

    @classmethod
    def from_pipe_fields(cls, tr_id: str, fields: List[str]) -> "AskingPriceRealResponse":
        """파이프 프레임의 ``^`` 구분 필드 목록으로 응답을 생성합니다."""
        data = {"tr_id": tr_id, "raw_fields": fields}
        for name, idx in ASKING_PRICE_FIELD_INDEX.items():
            if idx < len(fields):
                data[name] = fields[idx]
        return cls.model_validate(data)
