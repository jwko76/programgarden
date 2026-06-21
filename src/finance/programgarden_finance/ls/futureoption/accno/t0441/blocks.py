"""Pydantic models for LS Securities OpenAPI t0441 (선물/옵션잔고평가(이동평균)(t0441)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T0441RequestHeader(BlockRequestHeader):
    pass


class T0441ResponseHeader(BlockResponseHeader):
    pass

class T0441InBlock(BaseModel):
    """t0441InBlock — input block. 기본입력"""

    accno: str = Field(
        ...,
        title="계좌번호",
        description="accno — char(11). Consume as returned by LS.",
    )
    passwd: str = Field(
        ...,
        title="비밀번호",
        description="passwd — char(8). Consume as returned by LS.",
    )
    cts_expcode: str = Field(
        ...,
        title="CTS_종목번호",
        description="cts_expcode — char(8). Consume as returned by LS.",
    )
    cts_medocd: str = Field(
        ...,
        title="CTS_매매구분",
        description="cts_medocd — char(1). Consume as returned by LS.",
    )

class T0441OutBlock(BaseModel):
    """t0441OutBlock — output block. 출력"""

    tdtsunik: int = Field(
        default=0,
        title="매매손익합계",
        description="tdtsunik — long(18). Consume as returned by LS.",
    )
    cts_expcode: str = Field(
        default="",
        title="CTS_종목번호",
        description="cts_expcode — char(8). Consume as returned by LS.",
    )
    cts_medocd: str = Field(
        default="",
        title="CTS_매매구분",
        description="cts_medocd — char(1). Consume as returned by LS.",
    )
    tappamt: int = Field(
        default=0,
        title="평가금액",
        description="tappamt — long(18). Consume as returned by LS.",
    )
    tsunik: int = Field(
        default=0,
        title="평가손익",
        description="tsunik — long(18). Consume as returned by LS.",
    )

class T0441OutBlock1(BaseModel):
    """t0441OutBlock1 — output block (occurs — list of rows). 출력1"""

    expcode: str = Field(
        default="",
        title="종목번호",
        description="expcode — char(8). Consume as returned by LS.",
    )
    medosu: str = Field(
        default="",
        title="구분",
        description="medosu — char(4). Consume as returned by LS.",
    )
    jqty: int = Field(
        default=0,
        title="잔고수량",
        description="jqty — long(10). Consume as returned by LS.",
    )
    cqty: int = Field(
        default=0,
        title="청산가능수량",
        description="cqty — long(10). Consume as returned by LS.",
    )
    pamt: float = Field(
        default=0.0,
        title="평균단가",
        description="pamt — float(10.2). Consume as returned by LS.",
    )
    mamt: int = Field(
        default=0,
        title="총매입금액",
        description="mamt — long(18). Consume as returned by LS.",
    )
    medocd: str = Field(
        default="",
        title="매매구분",
        description="medocd — char(1). Consume as returned by LS.",
    )
    dtsunik: int = Field(
        default=0,
        title="매매손익",
        description="dtsunik — long(18). Consume as returned by LS.",
    )
    sysprocseq: int = Field(
        default=0,
        title="처리순번",
        description="sysprocseq — long(10). Consume as returned by LS.",
    )
    price: float = Field(
        default=0.0,
        title="현재가",
        description="price — float(9.2). Consume as returned by LS.",
    )
    appamt: int = Field(
        default=0,
        title="평가금액",
        description="appamt — long(18). Consume as returned by LS.",
    )
    dtsunik1: int = Field(
        default=0,
        title="평가손익",
        description="dtsunik1 — long(18). Consume as returned by LS.",
    )
    sunikrt: float = Field(
        default=0.0,
        title="수익율",
        description="sunikrt — float(10.2). Consume as returned by LS.",
    )

class T0441Request(BaseModel):
    """Request envelope for t0441."""

    header: T0441RequestHeader = T0441RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t0441",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t0441",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T0441Response(BaseModel):
    """Response envelope for t0441."""

    header: Optional[T0441ResponseHeader] = None
    block: Optional[T0441OutBlock] = None
    block1: List[T0441OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T0441RequestHeader",
    "T0441ResponseHeader",
    "T0441InBlock",
    "T0441OutBlock",
    "T0441OutBlock1",
    "T0441Request",
    "T0441Response",
]