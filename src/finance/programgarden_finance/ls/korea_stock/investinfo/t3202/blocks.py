"""Pydantic models for LS Securities OpenAPI t3202 (종목별증시일정(t3202)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T3202RequestHeader(BlockRequestHeader):
    pass


class T3202ResponseHeader(BlockResponseHeader):
    pass

class T3202InBlock(BaseModel):
    """t3202InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    date: str = Field(
        ...,
        title="조회일자",
        description="date — char(8). Consume as returned by LS.",
    )

class T3202OutBlock(BaseModel):
    """t3202OutBlock — output block (occurs — list of rows). 출력"""

    recdt: str = Field(
        default="",
        title="기준일",
        description="recdt — char(8). Consume as returned by LS.",
    )
    tableid: str = Field(
        default="",
        title="테이블아이디",
        description="tableid — char(6). Consume as returned by LS.",
    )
    upgu: str = Field(
        default="",
        title="업무구분",
        description="upgu — char(2). Consume as returned by LS.",
    )
    custno: str = Field(
        default="",
        title="발행체번호",
        description="custno — char(5). Consume as returned by LS.",
    )
    custnm: str = Field(
        default="",
        title="발행회사명",
        description="custnm — char(80). Consume as returned by LS.",
    )
    shcode: str = Field(
        default="",
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )
    upunm: str = Field(
        default="",
        title="업무명",
        description="upunm — char(20). Consume as returned by LS.",
    )

class T3202Request(BaseModel):
    """Request envelope for t3202."""

    header: T3202RequestHeader = T3202RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t3202",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t3202",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T3202Response(BaseModel):
    """Response envelope for t3202."""

    header: Optional[T3202ResponseHeader] = None
    block: List[T3202OutBlock] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T3202RequestHeader",
    "T3202ResponseHeader",
    "T3202InBlock",
    "T3202OutBlock",
    "T3202Request",
    "T3202Response",
]