"""빗썸 실시간 WebSocket(``real_base.py`` + ``real/``) 단위 테스트입니다.

실제 WebSocket 연결 없이 ``asyncio.Event`` / mock을 사용해 구독 추적,
리스너 등록, cap 강제, 연결 상태 검사를 검증합니다.
"""

import asyncio
import json
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from programgarden_finance.bithumb.real_base import (
    BithumbRealBase,
    BithumbSubscriptionLimitExceeded,
    DEFAULT_MAX_SUBSCRIBE_CODES,
    _get_response_model,
)
from programgarden_finance.bithumb.real import BithumbReal
from programgarden_finance.bithumb.real.ticker.blocks import TickerRealResponse
from programgarden_finance.bithumb.real.trade.blocks import TradeRealResponse
from programgarden_finance.bithumb.real.orderbook.blocks import (
    OrderbookRealResponse,
    OrderbookRealUnit,
)
from programgarden_finance.bithumb.client import Bithumb


# ──────────────────────────── 픽스처 헬퍼 ────────────────────────────


def _make_connected_base(max_subscribe_codes: int = 5) -> BithumbRealBase:
    """연결 상태로 설정된 BithumbRealBase 인스턴스를 반환합니다."""
    base = BithumbRealBase(max_subscribe_codes=max_subscribe_codes)
    base._connected_event.set()
    base._ws = AsyncMock()
    base._ws.send = AsyncMock()
    return base


# ──────────────────────────── 모델 캐시 ─────────────────────────────


class TestGetResponseModel:
    def test_ticker_model_is_ticker_real_response(self):
        model = _get_response_model("ticker")
        assert model is TickerRealResponse

    def test_trade_model_is_trade_real_response(self):
        model = _get_response_model("trade")
        assert model is TradeRealResponse

    def test_orderbook_model_is_orderbook_real_response(self):
        model = _get_response_model("orderbook")
        assert model is OrderbookRealResponse

    def test_unknown_stream_type_returns_none(self):
        model = _get_response_model("__unknown_type__")
        assert model is None


# ──────────────────────────── 구독 추적 ─────────────────────────────


class TestSubscriptionTracking:
    def test_add_codes_tracks_correctly(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
        assert base._subscribed_codes["ticker"] == ["KRW-BTC", "KRW-ETH"]

    def test_add_codes_deduplicates(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC"], "ticker")
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
        assert base._subscribed_codes["ticker"] == ["KRW-BTC", "KRW-ETH"]

    def test_remove_codes_updates_list(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
            base._remove_codes(["KRW-BTC"], "ticker")
        assert base._subscribed_codes["ticker"] == ["KRW-ETH"]

    def test_remove_all_codes_clears_key(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC"], "ticker")
            base._remove_codes(["KRW-BTC"], "ticker")
        assert "ticker" not in base._subscribed_codes

    def test_remove_nonexistent_code_is_noop(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC"], "ticker")
            base._remove_codes(["KRW-XRP"], "ticker")  # 없는 코드
        assert base._subscribed_codes["ticker"] == ["KRW-BTC"]

    def test_get_subscribed_codes_returns_copy(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC"], "ticker")
        result = base.get_subscribed_codes()
        result["ticker"].append("MUTATE")
        assert base._subscribed_codes["ticker"] == ["KRW-BTC"]


# ──────────────────────────── 구독 count / cap ───────────────────────


class TestSubscriptionCount:
    def test_count_is_max_across_types(self):
        base = _make_connected_base(max_subscribe_codes=0)
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
            base._add_codes(["KRW-BTC"], "trade")
        assert base.get_subscription_count() == 2  # max(2, 1)

    def test_count_zero_when_empty(self):
        base = _make_connected_base()
        assert base.get_subscription_count() == 0

    def test_capacity_decreases_after_add(self):
        base = _make_connected_base(max_subscribe_codes=5)
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
        assert base.get_subscription_capacity() == 3

    def test_capacity_none_when_disabled(self):
        base = _make_connected_base(max_subscribe_codes=0)
        assert base.get_subscription_capacity() is None

    def test_cap_raises_on_exceed(self):
        base = _make_connected_base(max_subscribe_codes=2)
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
            with pytest.raises(BithumbSubscriptionLimitExceeded):
                base._add_codes(["KRW-XRP"], "ticker")

    def test_cap_passes_on_reduplicate(self):
        """이미 구독 중인 코드 재추가는 cap 에 영향 없음."""
        base = _make_connected_base(max_subscribe_codes=2)
        with patch("asyncio.create_task"):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
            base._add_codes(["KRW-BTC"], "ticker")  # 중복 — cap 초과 없음

    def test_cap_disabled_allows_many(self):
        base = _make_connected_base(max_subscribe_codes=0)
        with patch("asyncio.create_task"):
            base._add_codes([f"KRW-C{i}" for i in range(50)], "ticker")
        assert len(base._subscribed_codes["ticker"]) == 50


# ──────────────────────────── 리스너 등록/해제 ───────────────────────


class TestListenerRegistration:
    def test_on_message_registers_listener(self):
        base = _make_connected_base()
        cb = lambda msg: None
        base._on_message("ticker", cb)
        assert base._on_message_listeners["ticker"] is cb

    def test_on_remove_message_unregisters_listener(self):
        base = _make_connected_base()
        base._on_message("ticker", lambda msg: None)
        base._on_remove_message("ticker")
        assert "ticker" not in base._on_message_listeners

    def test_on_message_raises_when_not_connected(self):
        base = BithumbRealBase()
        with pytest.raises(RuntimeError, match="연결"):
            base._on_message("ticker", lambda msg: None)

    def test_on_remove_raises_when_not_connected(self):
        base = BithumbRealBase()
        with pytest.raises(RuntimeError, match="연결"):
            base._on_remove_message("ticker")


# ──────────────────────────── add/remove 연결 검사 ───────────────────


class TestConnectionGuards:
    def test_add_codes_raises_when_not_connected(self):
        base = BithumbRealBase()
        with pytest.raises(RuntimeError, match="연결"):
            base._add_codes(["KRW-BTC"], "ticker")

    def test_remove_codes_raises_when_not_connected(self):
        base = BithumbRealBase()
        with pytest.raises(RuntimeError, match="연결"):
            base._remove_codes(["KRW-BTC"], "ticker")


# ──────────────────────────── 메시지 전송 검증 ───────────────────────


class TestSubscriptionMessages:
    def test_add_codes_sends_full_list(self):
        base = _make_connected_base(max_subscribe_codes=0)
        sent_messages: List[str] = []

        def capture_task(coro):
            sent_messages.append(coro)
            coro.close()
            return MagicMock()

        with patch("asyncio.create_task", side_effect=capture_task):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")

        assert len(sent_messages) == 1

    def test_remove_codes_sends_remaining_list(self):
        base = _make_connected_base(max_subscribe_codes=0)
        calls: List[str] = []

        def capture(coro):
            calls.append(coro)
            coro.close()
            return MagicMock()

        with patch("asyncio.create_task", side_effect=capture):
            base._add_codes(["KRW-BTC", "KRW-ETH"], "ticker")
            base._remove_codes(["KRW-BTC"], "ticker")

        # add 1회 + remove 1회 = 총 2회
        assert len(calls) == 2


# ──────────────────────────── staleness ─────────────────────────────


class TestStaleness:
    def test_staleness_zero_before_first_message(self):
        base = BithumbRealBase()
        assert base.get_staleness_sec() == 0.0

    def test_staleness_positive_after_message(self):
        import time
        base = BithumbRealBase()
        base._last_message_time = time.time() - 5.0
        assert base.get_staleness_sec() >= 5.0


# ──────────────────────────── BithumbReal 싱글톤 ─────────────────────


class TestBithumbRealSingleton:
    def test_real_returns_same_instance(self):
        Bithumb._clear_all_real_instances()
        bithumb = Bithumb()
        r1 = bithumb.real()
        r2 = bithumb.real()
        assert r1 is r2

    def test_different_bithumb_returns_different_real(self):
        Bithumb._clear_all_real_instances()
        b1, b2 = Bithumb(), Bithumb()
        assert b1.real() is not b2.real()

    def test_real_is_bithumb_real_instance(self):
        Bithumb._clear_all_real_instances()
        bithumb = Bithumb()
        assert isinstance(bithumb.real(), BithumbReal)


# ──────────────────────────── 응답 모델 파싱 ─────────────────────────


TICKER_PAYLOAD = {
    "type": "ticker",
    "code": "KRW-BTC",
    "opening_price": 95000000.0,
    "high_price": 96000000.0,
    "low_price": 94000000.0,
    "trade_price": 95500000.0,
    "prev_closing_price": 94800000.0,
    "acc_trade_price": 12345678900.0,
    "change": "RISE",
    "change_price": 700000.0,
    "signed_change_price": 700000.0,
    "change_rate": 0.00738,
    "signed_change_rate": 0.00738,
    "ask_bid": "BID",
    "trade_volume": 0.0123,
    "acc_trade_volume": 123.456,
    "trade_date": "20260619",
    "trade_time": "123456",
    "trade_timestamp": 1750334400000,
    "acc_ask_volume": 60.0,
    "acc_bid_volume": 63.456,
    "highest_52_week_price": 120000000.0,
    "highest_52_week_date": "2025-12-01",
    "lowest_52_week_price": 60000000.0,
    "lowest_52_week_date": "2025-08-15",
    "market_state": "ACTIVE",
    "is_trading_suspended": False,
    "delisting_date": None,
    "market_warning": "NONE",
    "timestamp": 1750334400123,
    "acc_trade_price_24h": 23456789000.0,
    "acc_trade_volume_24h": 234.567,
    "stream_type": "REALTIME",
}

TRADE_PAYLOAD = {
    "type": "trade",
    "code": "KRW-BTC",
    "trade_price": 95500000.0,
    "trade_volume": 0.0123,
    "ask_bid": "BID",
    "prev_closing_price": 94800000.0,
    "change": "RISE",
    "change_price": 700000.0,
    "trade_date": "20260619",
    "trade_time": "123456",
    "trade_timestamp": 1750334400000,
    "timestamp": 1750334400123,
    "sequential_id": 1234567890123456789,
    "stream_type": "REALTIME",
}

ORDERBOOK_PAYLOAD = {
    "type": "orderbook",
    "code": "KRW-BTC",
    "timestamp": 1750334400123,
    "total_ask_size": 10.5,
    "total_bid_size": 15.2,
    "orderbook_units": [
        {"ask_price": 95600000.0, "bid_price": 95500000.0, "ask_size": 0.1234, "bid_size": 0.5678}
    ],
    "stream_type": "REALTIME",
    "level": 0.0,
}


class TestResponseModels:
    def test_ticker_parses_correctly(self):
        r = TickerRealResponse.model_validate(TICKER_PAYLOAD)
        assert r.code == "KRW-BTC"
        assert r.trade_price == 95500000.0
        assert r.change == "RISE"
        assert r.stream_type == "REALTIME"
        assert r.error_msg is None

    def test_trade_parses_correctly(self):
        r = TradeRealResponse.model_validate(TRADE_PAYLOAD)
        assert r.code == "KRW-BTC"
        assert r.ask_bid == "BID"
        assert r.sequential_id == 1234567890123456789
        assert r.error_msg is None

    def test_orderbook_parses_correctly(self):
        r = OrderbookRealResponse.model_validate(ORDERBOOK_PAYLOAD)
        assert r.code == "KRW-BTC"
        assert len(r.orderbook_units) == 1
        assert r.orderbook_units[0].ask_price == 95600000.0
        assert r.error_msg is None

    def test_ticker_delisting_date_nullable(self):
        r = TickerRealResponse.model_validate(TICKER_PAYLOAD)
        assert r.delisting_date is None

    def test_orderbook_level_optional(self):
        payload = dict(ORDERBOOK_PAYLOAD)
        del payload["level"]
        r = OrderbookRealResponse.model_validate(payload)
        assert r.level is None


# ──────────────────────────── BithumbReal 스트림 클라이언트 ──────────


class TestBithumbRealStreamClients:
    def _make_real(self) -> BithumbReal:
        real = BithumbReal(max_subscribe_codes=0)
        real._connected_event.set()
        real._ws = AsyncMock()
        return real

    def test_ticker_client_accessible(self):
        real = self._make_real()
        client = real.ticker()
        from programgarden_finance.bithumb.real.ticker.client import RealTicker
        assert isinstance(client, RealTicker)

    def test_trade_client_accessible(self):
        real = self._make_real()
        client = real.trade()
        from programgarden_finance.bithumb.real.trade.client import RealTrade
        assert isinstance(client, RealTrade)

    def test_orderbook_client_accessible(self):
        real = self._make_real()
        client = real.orderbook()
        from programgarden_finance.bithumb.real.orderbook.client import RealOrderbook
        assert isinstance(client, RealOrderbook)

    def test_ticker_listener_registered(self):
        real = self._make_real()
        cb = lambda msg: None
        with patch("asyncio.create_task"):
            real.ticker().add_ticker_codes(["KRW-BTC"])
        real.ticker().on_ticker(cb)
        assert real._on_message_listeners["ticker"] is cb

    def test_trade_listener_registered(self):
        real = self._make_real()
        cb = lambda msg: None
        with patch("asyncio.create_task"):
            real.trade().add_trade_codes(["KRW-BTC"])
        real.trade().on_trade(cb)
        assert real._on_message_listeners["trade"] is cb

    def test_orderbook_listener_registered(self):
        real = self._make_real()
        cb = lambda msg: None
        with patch("asyncio.create_task"):
            real.orderbook().add_orderbook_codes(["KRW-BTC"])
        real.orderbook().on_orderbook(cb)
        assert real._on_message_listeners["orderbook"] is cb

    def test_stream_clients_raise_before_connect(self):
        real = BithumbReal()
        with pytest.raises(RuntimeError):
            real.ticker()

    def test_korean_alias_현재가(self):
        real = self._make_real()
        client = real.현재가()
        from programgarden_finance.bithumb.real.ticker.client import RealTicker
        assert isinstance(client, RealTicker)

    def test_korean_alias_체결(self):
        real = self._make_real()
        client = real.체결()
        from programgarden_finance.bithumb.real.trade.client import RealTrade
        assert isinstance(client, RealTrade)

    def test_korean_alias_호가(self):
        real = self._make_real()
        client = real.호가()
        from programgarden_finance.bithumb.real.orderbook.client import RealOrderbook
        assert isinstance(client, RealOrderbook)


# ──────────────────────────── DEFAULT_MAX_SUBSCRIBE_CODES ────────────


class TestDefaults:
    def test_default_max_subscribe_codes(self):
        assert DEFAULT_MAX_SUBSCRIBE_CODES == 15

    def test_bithumb_real_default_cap(self):
        real = BithumbReal()
        assert real._max_subscribe_codes == DEFAULT_MAX_SUBSCRIBE_CODES
