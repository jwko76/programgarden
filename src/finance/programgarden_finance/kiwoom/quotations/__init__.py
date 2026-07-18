"""키움증권 시세 API - Quotations 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import SetupOptions
from ..token_manager import KiwoomTokenManager
from ..tr_helpers import set_tr_options
from . import inquire_price, inquire_asking_price, inquire_daily_itemchartprice
from .inquire_price import InquirePriceInBlock, InquirePriceRequest, TrInquirePrice
from .inquire_asking_price import (
    InquireAskingPriceInBlock,
    InquireAskingPriceRequest,
    TrInquireAskingPrice,
)
from .inquire_daily_itemchartprice import (
    InquireDailyItemChartPriceInBlock,
    InquireDailyItemChartPriceRequest,
    TrInquireDailyItemChartPrice,
)


class Quotations(metaclass=EnforceKoreanAliasMeta):
    """키움증권 시세 API 카테고리입니다. 접근토큰 인증이 필요합니다."""

    def __init__(self, token_manager: KiwoomTokenManager):
        self.token_manager = token_manager

    @require_korean_alias
    def inquire_price(
        self, params: InquirePriceInBlock, options: Optional[SetupOptions] = None
    ) -> TrInquirePrice:
        request_data = InquirePriceRequest(body=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquirePrice(request_data)

    현재가 = inquire_price
    현재가.__doc__ = "종목의 기본정보(현재가 포함)를 조회합니다. (ka10001)"

    @require_korean_alias
    def inquire_asking_price(
        self, params: InquireAskingPriceInBlock, options: Optional[SetupOptions] = None
    ) -> TrInquireAskingPrice:
        request_data = InquireAskingPriceRequest(body=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquireAskingPrice(request_data)

    호가 = inquire_asking_price
    호가.__doc__ = "종목의 호가 정보를 조회합니다. (ka10004)"

    @require_korean_alias
    def inquire_daily_itemchartprice(
        self, params: InquireDailyItemChartPriceInBlock, options: Optional[SetupOptions] = None
    ) -> TrInquireDailyItemChartPrice:
        request_data = InquireDailyItemChartPriceRequest(body=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquireDailyItemChartPrice(request_data)

    일봉 = inquire_daily_itemchartprice
    일봉.__doc__ = "종목의 일봉 차트 데이터를 조회합니다. (ka10081)"


__all__ = [
    Quotations,
    inquire_price,
    inquire_asking_price,
    inquire_daily_itemchartprice,
]
