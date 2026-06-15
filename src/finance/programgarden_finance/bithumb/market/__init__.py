"""빗썸 시세(공개) API - Market 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import BithumbCredentials, SetupOptions
from ..tr_helpers import set_tr_options
from . import market_all, ticker, orderbook, trades_ticks
from . import candles_minutes, candles_days, candles_weeks, candles_months
from . import fee_inout
from .market_all import MarketAllInBlock, MarketAllRequest, TrMarketAll
from .ticker import TickerInBlock, TickerRequest, TrTicker
from .orderbook import OrderbookInBlock, OrderbookRequest, TrOrderbook
from .trades_ticks import TradesTicksInBlock, TradesTicksRequest, TrTradesTicks
from .candles_minutes import CandlesMinutesInBlock, CandlesMinutesRequest, TrCandlesMinutes
from .candles_days import CandlesDaysInBlock, CandlesDaysRequest, TrCandlesDays
from .candles_weeks import CandlesWeeksInBlock, CandlesWeeksRequest, TrCandlesWeeks
from .candles_months import CandlesMonthsInBlock, CandlesMonthsRequest, TrCandlesMonths
from .fee_inout import FeeInoutInBlock, FeeInoutRequest, TrFeeInout


class Market(metaclass=EnforceKoreanAliasMeta):
    """빗썸 시세(공개) API 카테고리입니다. 인증이 필요하지 않습니다."""

    def __init__(self, credentials: Optional[BithumbCredentials] = None):
        self.credentials = credentials or BithumbCredentials()

    @require_korean_alias
    def market_all(
        self,
        params: Optional[MarketAllInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrMarketAll:
        request_data = MarketAllRequest(params=params or MarketAllInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrMarketAll(request_data)

    거래대상목록 = market_all
    거래대상목록.__doc__ = "빗썸에서 거래 가능한 마켓(거래대상) 목록을 조회합니다."

    @require_korean_alias
    def ticker(self, params: TickerInBlock, options: Optional[SetupOptions] = None) -> TrTicker:
        request_data = TickerRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrTicker(request_data)

    현재가 = ticker
    현재가.__doc__ = "마켓의 현재가(스냅샷) 정보를 조회합니다."

    @require_korean_alias
    def orderbook(self, params: OrderbookInBlock, options: Optional[SetupOptions] = None) -> TrOrderbook:
        request_data = OrderbookRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrOrderbook(request_data)

    호가 = orderbook
    호가.__doc__ = "마켓의 호가 정보를 조회합니다."

    @require_korean_alias
    def trades_ticks(self, params: TradesTicksInBlock, options: Optional[SetupOptions] = None) -> TrTradesTicks:
        request_data = TradesTicksRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrTradesTicks(request_data)

    체결내역 = trades_ticks
    체결내역.__doc__ = "마켓의 최근 체결 내역을 조회합니다."

    @require_korean_alias
    def candles_minutes(self, params: CandlesMinutesInBlock, options: Optional[SetupOptions] = None) -> TrCandlesMinutes:
        request_data = CandlesMinutesRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrCandlesMinutes(request_data)

    분캔들 = candles_minutes
    분캔들.__doc__ = "마켓의 분(分) 캔들을 조회합니다."

    @require_korean_alias
    def candles_days(self, params: CandlesDaysInBlock, options: Optional[SetupOptions] = None) -> TrCandlesDays:
        request_data = CandlesDaysRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrCandlesDays(request_data)

    일캔들 = candles_days
    일캔들.__doc__ = "마켓의 일(日) 캔들을 조회합니다."

    @require_korean_alias
    def candles_weeks(self, params: CandlesWeeksInBlock, options: Optional[SetupOptions] = None) -> TrCandlesWeeks:
        request_data = CandlesWeeksRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrCandlesWeeks(request_data)

    주캔들 = candles_weeks
    주캔들.__doc__ = "마켓의 주(週) 캔들을 조회합니다."

    @require_korean_alias
    def candles_months(self, params: CandlesMonthsInBlock, options: Optional[SetupOptions] = None) -> TrCandlesMonths:
        request_data = CandlesMonthsRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrCandlesMonths(request_data)

    월캔들 = candles_months
    월캔들.__doc__ = "마켓의 월(月) 캔들을 조회합니다."

    @require_korean_alias
    def fee_inout(self, params: FeeInoutInBlock, options: Optional[SetupOptions] = None) -> TrFeeInout:
        request_data = FeeInoutRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrFeeInout(request_data)

    입출금수수료조회 = fee_inout
    입출금수수료조회.__doc__ = "화폐별 입출금 수수료를 조회합니다."


__all__ = [
    Market,
    market_all,
    ticker,
    orderbook,
    trades_ticks,
    candles_minutes,
    candles_days,
    candles_weeks,
    candles_months,
    fee_inout,
]
