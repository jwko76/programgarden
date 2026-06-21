"""Pydantic models for LS Securities OpenAPI t1974 (ELW기초자산동일종목(t1974)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1974RequestHeader(BlockRequestHeader):
    pass


class T1974ResponseHeader(BlockResponseHeader):
    pass

class T1974InBlock(BaseModel):
    """t1974InBlock — input block. 입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1974OutBlock(BaseModel):
    """t1974OutBlock — output block. 출력"""

    cnt: int = Field(
        default=0,
        title="종목갯수",
        description="cnt — long(4). Consume as returned by LS.",
    )

class T1974OutBlock1(BaseModel):
    """t1974OutBlock1 — output block (occurs — list of rows). 출력1"""

    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    hname: str = Field(
        default="",
        title="종목명",
        description="hname — char(40). Consume as returned by LS.",
    )
    cpgubun: str = Field(
        default="",
        title="콜/풋구분",
        description="cpgubun — char(2). Consume as returned by LS.",
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
    volume: float = Field(
        default=0.0,
        title="거래량",
        description="volume — float(12). Consume as returned by LS.",
    )

class T1974Request(BaseModel):
    """Request envelope for t1974."""

    header: T1974RequestHeader = T1974RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1974",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1974",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1974Response(BaseModel):
    """Response envelope for t1974."""

    header: Optional[T1974ResponseHeader] = None
    block: Optional[T1974OutBlock] = None
    block1: List[T1974OutBlock1] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1974RequestHeader",
    "T1974ResponseHeader",
    "T1974InBlock",
    "T1974OutBlock",
    "T1974OutBlock1",
    "T1974Request",
    "T1974Response",
]