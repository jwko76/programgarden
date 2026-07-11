"""KIS 국내주식 실시간 체결가 (H0STCNT0) 응답 모델입니다.

데이터는 ``^`` 구분 위치 기반 필드로 수신됩니다. 주요 필드만 매핑하며
전체 원본 필드는 ``raw_fields`` 로 접근할 수 있습니다.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# H0STCNT0 필드 순서 (KIS Developers 실시간 체결가 명세의 앞부분 주요 필드)
CCNL_FIELD_INDEX = {
    "mksc_shrn_iscd": 0,    # 유가증권 단축 종목코드
    "stck_cntg_hour": 1,    # 주식 체결 시간 (HHMMSS)
    "stck_prpr": 2,         # 주식 현재가
    "prdy_vrss_sign": 3,    # 전일 대비 부호
    "prdy_vrss": 4,         # 전일 대비
    "prdy_ctrt": 5,         # 전일 대비율
    "wghn_avrg_stck_prc": 6,  # 가중 평균 주식 가격
    "stck_oprc": 7,         # 주식 시가
    "stck_hgpr": 8,         # 주식 최고가
    "stck_lwpr": 9,         # 주식 최저가
    "askp1": 10,            # 매도호가1
    "bidp1": 11,            # 매수호가1
    "cntg_vol": 12,         # 체결 거래량
    "acml_vol": 13,         # 누적 거래량
    "acml_tr_pbmn": 14,     # 누적 거래대금
}


class CcnlRealResponse(BaseModel):
    """실시간 체결가 응답입니다."""

    model_config = ConfigDict(extra="ignore")

    tr_id: str = Field(default="H0STCNT0", title="TR ID")
    mksc_shrn_iscd: Optional[str] = Field(default=None, title="종목코드")
    stck_cntg_hour: Optional[str] = Field(default=None, title="체결 시간", description="HHMMSS")
    stck_prpr: Optional[str] = Field(default=None, title="현재가")
    prdy_vrss_sign: Optional[str] = Field(default=None, title="전일 대비 부호")
    prdy_vrss: Optional[str] = Field(default=None, title="전일 대비")
    prdy_ctrt: Optional[str] = Field(default=None, title="전일 대비율(%)")
    wghn_avrg_stck_prc: Optional[str] = Field(default=None, title="가중 평균 주식 가격")
    stck_oprc: Optional[str] = Field(default=None, title="시가")
    stck_hgpr: Optional[str] = Field(default=None, title="고가")
    stck_lwpr: Optional[str] = Field(default=None, title="저가")
    askp1: Optional[str] = Field(default=None, title="매도호가1")
    bidp1: Optional[str] = Field(default=None, title="매수호가1")
    cntg_vol: Optional[str] = Field(default=None, title="체결 거래량")
    acml_vol: Optional[str] = Field(default=None, title="누적 거래량")
    acml_tr_pbmn: Optional[str] = Field(default=None, title="누적 거래대금")
    raw_fields: Optional[List[str]] = Field(default=None, description="원본 전체 필드", repr=False)
    error_msg: Optional[str] = Field(default=None, description="파싱 에러 메시지")

    @classmethod
    def from_pipe_fields(cls, tr_id: str, fields: List[str]) -> "CcnlRealResponse":
        """파이프 프레임의 ``^`` 구분 필드 목록으로 응답을 생성합니다."""
        data = {"tr_id": tr_id, "raw_fields": fields}
        for name, idx in CCNL_FIELD_INDEX.items():
            if idx < len(fields):
                data[name] = fields[idx]
        return cls.model_validate(data)
