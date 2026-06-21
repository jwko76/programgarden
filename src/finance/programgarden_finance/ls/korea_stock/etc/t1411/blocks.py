"""Pydantic models for LS Securities OpenAPI t1411 (증거금율별종목조회(t1411)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1411RequestHeader(BlockRequestHeader):
    pass


class T1411ResponseHeader(BlockResponseHeader):
    pass

class T1411InBlock(BaseModel):
    """t1411InBlock — input block. 기본입력"""

    gubun: str = Field(
        ...,
        title="시장구분",
        description="gubun — char(1). Consume as returned by LS.",
    )
    jongchk: str = Field(
        ...,
        title="위탁신용구분",
        description="jongchk — char(1). Consume as returned by LS.",
    )
    jkrate: str = Field(
        ...,
        title="증거금율구분",
        description="jkrate — char(1). Consume as returned by LS.",
    )
    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    idx: int = Field(
        ...,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1411OutBlock(BaseModel):
    """t1411OutBlock — output block. 출력"""

    jkrate: int = Field(
        default=0,
        title="위탁증거금율",
        description="jkrate — long(3). Consume as returned by LS.",
    )
    sjkrate: int = Field(
        default=0,
        title="신용증거금율",
        description="sjkrate — long(3). Consume as returned by LS.",
    )
    idx: int = Field(
        default=0,
        title="IDX",
        description="idx — long(4). Consume as returned by LS.",
    )

class T1411OutBlock1(BaseModel):
    """t1411OutBlock1 — output block (occurs — list of rows). 출력1"""

    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(20). Consume as returned by LS.",
    )
    jkrate: int = Field(
        default=0,
        title="위탁증거금율",
        description="jkrate — long(3). Consume as returned by LS.",
    )
    sjkrate: int = Field(
        default=0,
        title="신용증거금율",
        description="sjkrate — long(3). Consume as returned by LS.",
    )
    subprice: int = Field(
        default=0,
        title="대용가",
        description="subprice — long(8). Consume as returned by LS.",
    )
    recprice: int = Field(
        default=0,
        title="전일종가",
        description="recprice — long(8). Consume as returned by LS.",
    )
    price: int = Field(
        default=0,
        title="현재가",
        description="price — long(8). Consume as returned by LS.",
    )
    sign: str = Field(
        default="",
        title="전일대비구분",
        description="sign — char(1). Consume as returned by LS.",
    )
    change: int = Field(
        default=0,
        title="전일대비",
        description="change — long(8). Consume as returned by LS.",
    )
    diff: float = Field(
        default=0.0,
        title="등락율",
        description="diff — float(6.2). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="누적거래량",
        description="volume — long(12). Consume as returned by LS.",
    )

class T1411Request(BaseModel):
    """Request envelope for t1411."""

    header: T1411RequestHeader = T1411RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1411",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1411",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1411Response(BaseModel):
    """Response envelope for t1411."""

    header: Optional[T1411ResponseHeader] = None
    block: Optional[T1411OutBlock] = None
    block1: List[T1411OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1411RequestHeader",
    "T1411ResponseHeader",
    "T1411InBlock",
    "T1411OutBlock",
    "T1411OutBlock1",
    "T1411Request",
    "T1411Response",
]