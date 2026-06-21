"""Pydantic models for LS Securities OpenAPI t1926 (종목별신용정보(t1926)).
Auto-generated from xingAPI RES spec.
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr
from requests import Response

from ....models import BlockRequestHeader, BlockResponseHeader, SetupOptions


class T1926RequestHeader(BlockRequestHeader):
    pass


class T1926ResponseHeader(BlockResponseHeader):
    pass

class T1926InBlock(BaseModel):
    """t1926InBlock — input block. 기본입력"""

    shcode: str = Field(
        ...,
        title="종목코드",
        description="shcode — char(6). Consume as returned by LS.",
    )

class T1926OutBlock(BaseModel):
    """t1926OutBlock — output block. 출력"""

    ynvolume: int = Field(
        default=0,
        title="융자신규수량",
        description="ynvolume — long(8). Consume as returned by LS.",
    )
    ysvolume: int = Field(
        default=0,
        title="융자상환수량",
        description="ysvolume — long(8). Consume as returned by LS.",
    )
    yjvolume: int = Field(
        default=0,
        title="융자잔고수량",
        description="yjvolume — long(8). Consume as returned by LS.",
    )
    yvchange: int = Field(
        default=0,
        title="융자수량대비",
        description="yvchange — long(8). Consume as returned by LS.",
    )
    ygrate: float = Field(
        default=0.0,
        title="융자공여율",
        description="ygrate — float(9.2). Consume as returned by LS.",
    )
    yjrate: float = Field(
        default=0.0,
        title="융자잔고율",
        description="yjrate — float(9.2). Consume as returned by LS.",
    )
    ynprice: int = Field(
        default=0,
        title="융자신규금액",
        description="ynprice — long(8). Consume as returned by LS.",
    )
    ysprice: int = Field(
        default=0,
        title="융자상환금액",
        description="ysprice — long(8). Consume as returned by LS.",
    )
    yjprice: int = Field(
        default=0,
        title="융자잔고금액",
        description="yjprice — long(8). Consume as returned by LS.",
    )
    yachange: int = Field(
        default=0,
        title="융자금액대비",
        description="yachange — long(8). Consume as returned by LS.",
    )
    dnvolume: int = Field(
        default=0,
        title="대주신규수량",
        description="dnvolume — long(8). Consume as returned by LS.",
    )
    dsvolume: int = Field(
        default=0,
        title="대주상환수량",
        description="dsvolume — long(8). Consume as returned by LS.",
    )
    djvolume: int = Field(
        default=0,
        title="대주잔고수량",
        description="djvolume — long(8). Consume as returned by LS.",
    )
    dvchange: int = Field(
        default=0,
        title="대주수량대비",
        description="dvchange — long(8). Consume as returned by LS.",
    )
    dgrate: float = Field(
        default=0.0,
        title="대주공여율",
        description="dgrate — float(9.2). Consume as returned by LS.",
    )
    djrate: float = Field(
        default=0.0,
        title="대주잔고율",
        description="djrate — float(9.2). Consume as returned by LS.",
    )
    dnprice: int = Field(
        default=0,
        title="대주신규금액",
        description="dnprice — long(8). Consume as returned by LS.",
    )
    dsprice: int = Field(
        default=0,
        title="대주상환금액",
        description="dsprice — long(8). Consume as returned by LS.",
    )
    djprice: int = Field(
        default=0,
        title="대주잔고금액",
        description="djprice — long(8). Consume as returned by LS.",
    )
    dachange: int = Field(
        default=0,
        title="대주금액대비",
        description="dachange — long(8). Consume as returned by LS.",
    )
    mmdate: str = Field(
        default="",
        title="결제일",
        description="mmdate — char(8). Consume as returned by LS.",
    )
    close: int = Field(
        default=0,
        title="결제일종가",
        description="close — long(8). Consume as returned by LS.",
    )
    volume: int = Field(
        default=0,
        title="결제일거래량",
        description="volume — long(10). Consume as returned by LS.",
    )
    value: int = Field(
        default=0,
        title="결제일거래대금",
        description="value — long(12). Consume as returned by LS.",
    )
    pr5days: float = Field(
        default=0.0,
        title="주가5일증가율",
        description="pr5days — float(9.2). Consume as returned by LS.",
    )
    pr20days: float = Field(
        default=0.0,
        title="주가20일증가율",
        description="pr20days — float(9.2). Consume as returned by LS.",
    )
    yj5days: float = Field(
        default=0.0,
        title="융자5일증가율",
        description="yj5days — float(9.2). Consume as returned by LS.",
    )
    yj20days: float = Field(
        default=0.0,
        title="융자20일증가율",
        description="yj20days — float(9.2). Consume as returned by LS.",
    )
    dj5days: float = Field(
        default=0.0,
        title="대주5일증가율",
        description="dj5days — float(9.2). Consume as returned by LS.",
    )
    dj20days: float = Field(
        default=0.0,
        title="대주20일증가율",
        description="dj20days — float(9.2). Consume as returned by LS.",
    )

class T1926Request(BaseModel):
    """Request envelope for t1926."""

    header: T1926RequestHeader = T1926RequestHeader(
        content_type="application/json; charset=utf-8",
        authorization="",
        tr_cd="t1926",
        tr_cont="N",
        tr_cont_key="",
        mac_address="",
    )
    body: dict = {}
    options: SetupOptions = SetupOptions(
        rate_limit_count=1,
        rate_limit_seconds=1,
        on_rate_limit="wait",
        rate_limit_key="t1926",
    )
    _raw_data: Optional[Response] = PrivateAttr(default=None)

class T1926Response(BaseModel):
    """Response envelope for t1926."""

    header: Optional[T1926ResponseHeader] = None
    block: Optional[T1926OutBlock] = None
    rsp_cd: str = ""
    rsp_msg: str = ""
    status_code: Optional[int] = None
    error_msg: Optional[str] = None
    raw_data: Optional[object] = None

__all__ = [
    "T1926RequestHeader",
    "T1926ResponseHeader",
    "T1926InBlock",
    "T1926OutBlock",
    "T1926Request",
    "T1926Response",
]