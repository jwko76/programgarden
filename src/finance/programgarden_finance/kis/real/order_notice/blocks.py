"""KIS 국내주식 실시간 체결통보 (H0STCNI0 실전 / H0STCNI9 모의) 응답 모델입니다.

AES-256-CBC 복호화 후 ``^`` 구분 위치 기반 필드로 파싱합니다.
"""

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# H0STCNI0/H0STCNI9 필드 순서 (KIS Developers 실시간 체결통보 명세의 주요 필드)
ORDER_NOTICE_FIELD_INDEX = {
    "cust_id": 0,          # 고객 ID (HTS ID)
    "acnt_no": 1,          # 계좌번호
    "oder_no": 2,          # 주문번호
    "ooder_no": 3,         # 원주문번호
    "seln_byov_cls": 4,    # 매도매수구분 (01: 매도, 02: 매수)
    "rctf_cls": 5,         # 정정구분
    "oder_kind": 6,        # 주문종류
    "oder_cond": 7,        # 주문조건
    "stck_shrn_iscd": 8,   # 주식 단축 종목코드
    "cntg_qty": 9,         # 체결 수량
    "cntg_unpr": 10,       # 체결 단가
    "stck_cntg_hour": 11,  # 주식 체결 시간
    "rfus_yn": 12,         # 거부 여부
    "cntg_yn": 13,         # 체결 여부 (1: 주문/정정/취소/거부 접수, 2: 체결)
    "acpt_yn": 14,         # 접수 여부
    "brnc_no": 15,         # 지점번호
    "oder_qty": 16,        # 주문 수량
    "acnt_name": 17,       # 계좌명
    "cntg_isnm": 18,       # 체결 종목명
}


class OrderNoticeRealResponse(BaseModel):
    """실시간 체결통보 응답입니다."""

    model_config = ConfigDict(extra="ignore")

    tr_id: str = Field(default="H0STCNI0", title="TR ID")
    cust_id: Optional[str] = Field(default=None, title="고객 ID (HTS ID)")
    acnt_no: Optional[str] = Field(default=None, title="계좌번호")
    oder_no: Optional[str] = Field(default=None, title="주문번호")
    ooder_no: Optional[str] = Field(default=None, title="원주문번호")
    seln_byov_cls: Optional[str] = Field(default=None, title="매도매수구분", description="01: 매도, 02: 매수")
    rctf_cls: Optional[str] = Field(default=None, title="정정구분")
    oder_kind: Optional[str] = Field(default=None, title="주문종류")
    oder_cond: Optional[str] = Field(default=None, title="주문조건")
    stck_shrn_iscd: Optional[str] = Field(default=None, title="종목코드")
    cntg_qty: Optional[str] = Field(default=None, title="체결 수량")
    cntg_unpr: Optional[str] = Field(default=None, title="체결 단가")
    stck_cntg_hour: Optional[str] = Field(default=None, title="체결 시간")
    rfus_yn: Optional[str] = Field(default=None, title="거부 여부")
    cntg_yn: Optional[str] = Field(default=None, title="체결 여부", description="1: 접수, 2: 체결")
    acpt_yn: Optional[str] = Field(default=None, title="접수 여부")
    brnc_no: Optional[str] = Field(default=None, title="지점번호")
    oder_qty: Optional[str] = Field(default=None, title="주문 수량")
    acnt_name: Optional[str] = Field(default=None, title="계좌명")
    cntg_isnm: Optional[str] = Field(default=None, title="체결 종목명")
    raw_fields: Optional[List[str]] = Field(default=None, description="원본 전체 필드", repr=False)
    error_msg: Optional[str] = Field(default=None, description="파싱 에러 메시지")

    @classmethod
    def from_pipe_fields(cls, tr_id: str, fields: List[str]) -> "OrderNoticeRealResponse":
        """복호화된 ``^`` 구분 필드 목록으로 응답을 생성합니다."""
        data = {"tr_id": tr_id, "raw_fields": fields}
        for name, idx in ORDER_NOTICE_FIELD_INDEX.items():
            if idx < len(fields):
                data[name] = fields[idx]
        return cls.model_validate(data)
