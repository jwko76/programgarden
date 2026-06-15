"""빗썸(Bithumb) 주문 조회(Order, 비공개 API) 테스트입니다.

대상: orders_chance(주문가능정보), order_detail(개별주문조회), orders(주문리스트조회).
주문 생성/취소(order_new/order_cancel)는 ``test_bithumb_order_lifecycle.py``에서 다룹니다.

- ``Test*Mock`` 클래스: ``requests_mock`` + 더미 access_key/secret_key로 요청/응답을 검증합니다.
- ``TestOrderQueryLive`` 클래스: ``.env``에 ``BITHUMB_ACCESS_KEY``/``BITHUMB_SECRET_KEY``가
  설정되어 있으면 실제(읽기 전용) API를 호출합니다 (없으면 skip).
"""

import os

import jwt
import pytest
from dotenv import load_dotenv

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.order.orders_chance import OrdersChanceInBlock
from programgarden_finance.bithumb.order.order_detail import OrderDetailInBlock
from programgarden_finance.bithumb.order.orders import OrdersInBlock

load_dotenv()

ACCESS_KEY = "test-access-key"
SECRET_KEY = "test-secret-key-0123456789abcdef0123456789abcdef"


def _order():
    bithumb = Bithumb()
    bithumb.로그인(accesskey=ACCESS_KEY, secretkey=SECRET_KEY)
    return bithumb.주문()


def _assert_valid_auth_header(request) -> dict:
    auth = request.headers["Authorization"]
    assert auth.startswith("Bearer ")
    payload = jwt.decode(auth.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])
    assert payload["access_key"] == ACCESS_KEY
    return payload


_ORDERS_CHANCE_SAMPLE = {
    "bid_fee": "0.0004",
    "ask_fee": "0.0004",
    "maker_bid_fee": "0.0004",
    "maker_ask_fee": "0.0004",
    "market": {
        "id": "KRW-BTC",
        "name": "BTC/KRW",
        "order_sides": ["ask", "bid"],
        "bid_types": ["limit", "price"],
        "ask_types": ["limit", "market"],
        "bid": {"currency": "KRW", "price_unit": None, "min_total": "5000"},
        "ask": {"currency": "BTC", "price_unit": None, "min_total": "5000"},
        "max_total": "1000000000",
        "state": "active",
    },
    "bid_account": {
        "currency": "KRW",
        "balance": "1000000",
        "locked": "0",
        "avg_buy_price": "0",
        "avg_buy_price_modified": False,
        "unit_currency": "KRW",
    },
    "ask_account": {
        "currency": "BTC",
        "balance": "0.1",
        "locked": "0",
        "avg_buy_price": "95000000",
        "avg_buy_price_modified": False,
        "unit_currency": "KRW",
    },
}

_ORDER_OUT_COMMON = {
    "uuid": "9e8f8eba-7050-4837-82c3-768e2e63b58a",
    "side": "bid",
    "ord_type": "limit",
    "price": "95500000",
    "state": "wait",
    "market": "KRW-BTC",
    "created_at": "2026-06-14T12:00:00+09:00",
    "volume": "0.01",
    "remaining_volume": "0.01",
    "reserved_fee": "0.0",
    "remaining_fee": "0.0",
    "paid_fee": "0.0",
    "locked": "955000",
    "executed_volume": "0.0",
    "executed_funds": "0",
    "trades_count": 0,
}


# ---------------------------------------------------------------------------
# Mock tests
# ---------------------------------------------------------------------------


class TestOrdersChanceMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(URLS.ORDERS_CHANCE_URL, json=_ORDERS_CHANCE_SAMPLE)

        response = _order().주문가능정보(OrdersChanceInBlock(market="KRW-BTC")).req()

        assert response.error_msg is None
        block = response.block
        assert block.market.id == "KRW-BTC"
        assert block.bid_account.currency == "KRW"
        assert block.ask_account.balance == "0.1"

        payload = _assert_valid_auth_header(requests_mock.last_request)
        assert "query_hash" in payload
        assert "market=KRW-BTC" in requests_mock.last_request.url

    def test_error_envelope(self, requests_mock):
        requests_mock.get(
            URLS.ORDERS_CHANCE_URL,
            status_code=400,
            json={"error": {"name": "validation_error", "message": "market is required"}},
        )

        response = _order().주문가능정보(OrdersChanceInBlock(market="KRW-BTC")).req()

        assert response.block is None
        assert response.error_name == "validation_error"
        assert response.error_msg == "market is required"


class TestOrderDetailMock:
    def test_request_with_uuid(self, requests_mock):
        payload = {**_ORDER_OUT_COMMON, "trades": []}
        requests_mock.get(URLS.ORDER_URL, json=payload)

        response = _order().개별주문조회(
            OrderDetailInBlock(uuid="9e8f8eba-7050-4837-82c3-768e2e63b58a")
        ).req()

        assert response.error_msg is None
        assert response.block.uuid == "9e8f8eba-7050-4837-82c3-768e2e63b58a"
        assert response.block.trades == []

        payload_jwt = _assert_valid_auth_header(requests_mock.last_request)
        assert "query_hash" in payload_jwt
        assert "uuid=9e8f8eba" in requests_mock.last_request.url

    def test_request_with_trades(self, requests_mock):
        payload = {
            **_ORDER_OUT_COMMON,
            "state": "done",
            "trades": [
                {
                    "market": "KRW-BTC",
                    "uuid": "trade-uuid-1",
                    "price": "95500000",
                    "volume": "0.01",
                    "funds": "955000",
                    "side": "bid",
                    "created_at": "2026-06-14T12:00:01+09:00",
                }
            ],
        }
        requests_mock.get(URLS.ORDER_URL, json=payload)

        response = _order().개별주문조회(
            OrderDetailInBlock(uuid="9e8f8eba-7050-4837-82c3-768e2e63b58a")
        ).req()

        assert response.error_msg is None
        assert len(response.block.trades) == 1
        assert response.block.trades[0].price == "95500000"


class TestOrdersListMock:
    def test_request_with_filters(self, requests_mock):
        requests_mock.get(URLS.ORDERS_URL, json=[_ORDER_OUT_COMMON])

        response = _order().주문리스트조회(
            OrdersInBlock(market="KRW-BTC", state="wait", limit=10)
        ).req()

        assert response.error_msg is None
        assert response.blocks[0].state == "wait"

        payload_jwt = _assert_valid_auth_header(requests_mock.last_request)
        assert "query_hash" in payload_jwt
        assert "state=wait" in requests_mock.last_request.url
        assert "limit=10" in requests_mock.last_request.url

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.ORDERS_URL, json=[])

        response = _order().주문리스트조회().req()

        assert response.error_msg is None
        assert response.blocks == []


# ---------------------------------------------------------------------------
# Live tests (.env의 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY 필요, 없으면 skip)
# ---------------------------------------------------------------------------

_HAS_CREDENTIALS = bool(os.getenv("BITHUMB_ACCESS_KEY")) and bool(os.getenv("BITHUMB_SECRET_KEY"))


@pytest.mark.skipif(not _HAS_CREDENTIALS, reason="BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY가 설정되지 않았습니다.")
class TestOrderQueryLive:
    @pytest.fixture
    def live_order(self):
        bithumb = Bithumb()
        bithumb.로그인(
            accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
            secretkey=os.getenv("BITHUMB_SECRET_KEY"),
        )
        return bithumb.주문()

    def test_orders_chance(self, live_order):
        response = live_order.주문가능정보(OrdersChanceInBlock(market="KRW-BTC")).req()
        assert response.error_msg is None, response.error_msg
        assert response.block is not None
        assert response.block.market.id == "KRW-BTC"

    def test_orders_list(self, live_order):
        response = live_order.주문리스트조회(OrdersInBlock(market="KRW-BTC", limit=1)).req()
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None
