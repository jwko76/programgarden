"""Pydantic models for LS Securities OpenAPI t8425 (전체테마(t8425)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T8425RequestHeader(BlockRequestHeader):
    pass


class T8425ResponseHeader(BlockResponseHeader):
    pass

class T8425InBlock(BaseModel):
    """t8425InBlock — input block. 기본입력"""

    dummy: str = Field(
        ...,
        title="Dummy",
        description="dummy — char(1). Consume as returned by LS.",
    )

class T8425OutBlock(BaseModel):
    """t8425OutBlock — output block (occurs — list of rows). 출력"""

    tmname: str = Field(
        default="",
        title="테마명",
        description="tmname — char(36). Consume as returned by LS.",
    )
    tmcode: str = Field(
        default="",
        title="테마코드",
        description="tmcode — char(4). Consume as returned by LS.",
    )

class T8425Request(BaseModel):
    """Request envelope for t8425."""

    header: T8425RequestHeader = T8425RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t8425",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t8425",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T8425Response(BaseModel):
    """Response envelope for t8425."""

    header: Optional[T8425ResponseHeader] = None
    block: List[T8425OutBlock] = []
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T8425RequestHeader",
    "T8425ResponseHeader",
    "T8425InBlock",
    "T8425OutBlock",
    "T8425Request",
    "T8425Response",
]