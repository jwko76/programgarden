"""빗썸(Bithumb) 시세(Market, 공개 API) 테스트입니다.

- ``Test*Mock`` 클래스: ``requests_mock``으로 요청 URL/파라미터/응답 파싱을 검증합니다 (API 키 불필요).
- ``TestMarketLive`` 클래스: 실제 ``api.bithumb.com`` 공개 API를 호출합니다 (API 키 불필요, 항상 실행).
"""

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.market.market_all import MarketAllInBlock
from programgarden_finance.bithumb.market.ticker import TickerInBlock
from programgarden_finance.bithumb.market.orderbook import OrderbookInBlock
from programgarden_finance.bithumb.market.trades_ticks import TradesTicksInBlock
from programgarden_finance.bithumb.market.candles_minutes import CandlesMinutesInBlock
from programgarden_finance.bithumb.market.candles_days import CandlesDaysInBlock
from programgarden_finance.bithumb.market.candles_weeks import CandlesWeeksInBlock
from programgarden_finance.bithumb.market.candles_months import CandlesMonthsInBlock
from programgarden_finance.bithumb.market.fee_inout import FeeInoutInBlock


def _market():
    return Bithumb().시세()


# ---------------------------------------------------------------------------
# Sample payloads (빗썸 공식 응답 스키마를 따른 합성 데이터)
# ---------------------------------------------------------------------------

_TICKER_SAMPLE = {
    "market": "KRW-BTC",
    "trade_date": "20260614",
    "trade_time": "030000",
    "trade_date_kst": "20260614",
    "trade_time_kst": "120000",
    "trade_timestamp": 1749900000000,
    "opening_price": 95000000.0,
    "high_price": 96000000.0,
    "low_price": 94000000.0,
    "trade_price": 95500000.0,
    "prev_closing_price": 94800000.0,
    "change": "RISE",
    "change_price": 700000.0,
    "change_rate": 0.00738,
    "signed_change_price": 700000.0,
    "signed_change_rate": 0.00738,
    "trade_volume": 0.0123,
    "acc_trade_price": 12345678900.0,
    "acc_trade_price_24h": 23456789000.0,
    "acc_trade_volume": 123.456,
    "acc_trade_volume_24h": 234.567,
    "highest_52_week_price": 100000000.0,
    "highest_52_week_date": "2025-12-01",
    "lowest_52_week_price": 40000000.0,
    "lowest_52_week_date": "2025-01-15",
    "timestamp": 1749900000123,
}

_ORDERBOOK_SAMPLE = {
    "market": "KRW-BTC",
    "timestamp": 1749900000123,
    "total_ask_size": 12.345,
    "total_bid_size": 23.456,
    "orderbook_units": [
        {"ask_price": 95600000.0, "bid_price": 95500000.0, "ask_size": 0.1234, "bid_size": 0.5678},
    ],
}

_TRADES_TICKS_SAMPLE = {
    "market": "KRW-BTC",
    "trade_date_utc": "2026-06-14",
    "trade_time_utc": "03:00:00",
    "timestamp": 1749900000123,
    "trade_price": 95500000.0,
    "trade_volume": 0.0123,
    "prev_closing_price": 94800000.0,
    "change_price": 700000.0,
    "ask_bid": "BID",
    "sequential_id": 1749900000123001,
}

_FEE_INOUT_SAMPLE = {
    "name": "비트코인",
    "currency": "BTC",
    "networks": [
        {
            "net_name": "Bitcoin",
            "deposit_fee_quantity": "0",
            "deposit_minimum_quantity": "0.001",
            "withdraw_fee_quantity": "0.0005",
            "withdraw_rate": None,
            "withdraw_fee_min": None,
            "withdraw_fee_max": None,
            "withdraw_minimum_quantity": "0.001",
        },
    ],
}

_CANDLE_BASE_SAMPLE = {
    "market": "KRW-BTC",
    "candle_date_time_utc": "2026-06-14T00:00:00",
    "candle_date_time_kst": "2026-06-14T09:00:00",
    "opening_price": 95000000.0,
    "high_price": 96000000.0,
    "low_price": 94000000.0,
    "trade_price": 95500000.0,
    "timestamp": 1749868800000,
    "candle_acc_trade_price": 1234567890.0,
    "candle_acc_trade_volume": 12.345,
}


# ---------------------------------------------------------------------------
# Mock tests
# ---------------------------------------------------------------------------


class TestMarketAllMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(
            URLS.MARKET_ALL_URL,
            json=[{"market": "KRW-BTC", "korean_name": "비트코인", "english_name": "Bitcoin"}],
        )

        response = _market().거래대상목록(MarketAllInBlock(isDetails=False)).req()

        assert response.error_msg is None
        assert response.status_code == 200
        assert len(response.blocks) == 1
        assert response.blocks[0].market == "KRW-BTC"
        # bool 쿼리 파라미터는 소문자 "true"/"false"로 직렬화되어야 합니다.
        assert "isDetails=false" in requests_mock.last_request.url

    def test_no_params(self, requests_mock):
        requests_mock.get(URLS.MARKET_ALL_URL, json=[])

        response = _market().거래대상목록().req()

        assert response.error_msg is None
        assert response.blocks == []

    def test_error_envelope(self, requests_mock):
        requests_mock.get(
            URLS.MARKET_ALL_URL,
            status_code=400,
            json={"error": {"name": "invalid_parameter", "message": "잘못된 요청입니다."}},
        )

        response = _market().거래대상목록().req()

        assert response.blocks is None
        assert response.error_name == "invalid_parameter"
        assert response.error_msg == "잘못된 요청입니다."
        assert response.status_code == 400


class TestTickerMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(URLS.TICKER_URL, json=[_TICKER_SAMPLE])

        response = _market().현재가(TickerInBlock(markets="KRW-BTC,KRW-ETH")).req()

        assert response.error_msg is None
        assert response.blocks[0].market == "KRW-BTC"
        assert response.blocks[0].trade_price == 95500000.0
        assert "markets=KRW-BTC%2CKRW-ETH" in requests_mock.last_request.url


class TestOrderbookMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(URLS.ORDERBOOK_URL, json=[_ORDERBOOK_SAMPLE])

        response = _market().호가(OrderbookInBlock(markets="KRW-BTC")).req()

        assert response.error_msg is None
        unit = response.blocks[0].orderbook_units[0]
        assert unit.ask_price == 95600000.0
        assert unit.bid_size == 0.5678


class TestTradesTicksMock:
    def test_request_with_optional_params(self, requests_mock):
        requests_mock.get(URLS.TRADES_TICKS_URL, json=[_TRADES_TICKS_SAMPLE])

        response = _market().체결내역(TradesTicksInBlock(market="KRW-BTC", count=5)).req()

        assert response.error_msg is None
        assert response.blocks[0].ask_bid == "BID"
        assert "market=KRW-BTC" in requests_mock.last_request.url
        assert "count=5" in requests_mock.last_request.url


class TestCandlesMinutesMock:
    def test_unit_in_path_not_in_query(self, requests_mock):
        requests_mock.get(URLS.candles_minutes_url(1), json=[{**_CANDLE_BASE_SAMPLE, "unit": 1}])

        response = _market().분캔들(CandlesMinutesInBlock(market="KRW-BTC", unit=1, count=1)).req()

        assert response.error_msg is None
        assert response.blocks[0].unit == 1
        assert requests_mock.last_request.url.startswith(URLS.candles_minutes_url(1))
        assert "unit=" not in requests_mock.last_request.url


class TestCandlesDaysMock:
    def test_request_and_parse(self, requests_mock):
        payload = {
            **_CANDLE_BASE_SAMPLE,
            "prev_closing_price": 94800000.0,
            "change_price": 700000.0,
            "change_rate": 0.00738,
        }
        requests_mock.get(URLS.CANDLES_DAYS_URL, json=[payload])

        response = _market().일캔들(CandlesDaysInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None
        assert response.blocks[0].change_rate == 0.00738


class TestCandlesWeeksMock:
    def test_request_and_parse(self, requests_mock):
        payload = {**_CANDLE_BASE_SAMPLE, "first_day_of_period": "2026-06-08"}
        requests_mock.get(URLS.CANDLES_WEEKS_URL, json=[payload])

        response = _market().주캔들(CandlesWeeksInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None
        assert response.blocks[0].first_day_of_period == "2026-06-08"


class TestCandlesMonthsMock:
    def test_request_and_parse(self, requests_mock):
        payload = {**_CANDLE_BASE_SAMPLE, "first_day_of_period": "2026-06-01"}
        requests_mock.get(URLS.CANDLES_MONTHS_URL, json=[payload])

        response = _market().월캔들(CandlesMonthsInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None
        assert response.blocks[0].first_day_of_period == "2026-06-01"


class TestFeeInoutMock:
    def test_currency_in_path_not_in_query(self, requests_mock):
        requests_mock.get(URLS.fee_inout_url("BTC"), json=[_FEE_INOUT_SAMPLE])

        response = _market().입출금수수료조회(FeeInoutInBlock(currency="BTC")).req()

        assert response.error_msg is None
        assert response.blocks[0].currency == "BTC"
        assert response.blocks[0].networks[0].net_name == "Bitcoin"
        assert requests_mock.last_request.url == URLS.fee_inout_url("BTC")
        assert "currency=" not in requests_mock.last_request.url

    def test_error_envelope(self, requests_mock):
        requests_mock.get(
            URLS.fee_inout_url("XXX"),
            status_code=400,
            json={"error": {"name": "invalid_parameter", "message": "잘못된 요청입니다."}},
        )

        response = _market().입출금수수료조회(FeeInoutInBlock(currency="XXX")).req()

        assert response.blocks is None
        assert response.error_name == "invalid_parameter"
        assert response.error_msg == "잘못된 요청입니다."


# ---------------------------------------------------------------------------
# Live tests (실제 api.bithumb.com 호출, API 키 불필요)
# ---------------------------------------------------------------------------


class TestMarketLive:
    def test_market_all(self):
        response = _market().거래대상목록(MarketAllInBlock(isDetails=False)).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks
        assert any(item.market == "KRW-BTC" for item in response.blocks)

    def test_ticker(self):
        response = _market().현재가(TickerInBlock(markets="KRW-BTC")).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks
        assert response.blocks[0].market == "KRW-BTC"
        assert response.blocks[0].trade_price > 0

    def test_orderbook(self):
        response = _market().호가(OrderbookInBlock(markets="KRW-BTC")).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks
        assert response.blocks[0].orderbook_units

    def test_trades_ticks(self):
        response = _market().체결내역(TradesTicksInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks
        assert response.blocks[0].market == "KRW-BTC"

    def test_candles_minutes(self):
        response = _market().분캔들(CandlesMinutesInBlock(market="KRW-BTC", unit=1, count=1)).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks
        assert response.blocks[0].unit == 1

    def test_candles_days(self):
        response = _market().일캔들(CandlesDaysInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks

    def test_candles_weeks(self):
        response = _market().주캔들(CandlesWeeksInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks

    def test_candles_months(self):
        response = _market().월캔들(CandlesMonthsInBlock(market="KRW-BTC", count=1)).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks

    def test_fee_inout(self):
        response = _market().입출금수수료조회(FeeInoutInBlock(currency="BTC")).req()

        assert response.error_msg is None, response.error_msg
        assert response.blocks
        assert response.blocks[0].currency == "BTC"
        assert response.blocks[0].networks
