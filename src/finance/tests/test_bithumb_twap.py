"""빗썸(Bithumb) TWAP 주문(twap_new/twap_cancel/twap_list) 테스트입니다.

- ``Test*Mock`` 클래스: ``requests_mock``으로 요청 본문/쿼리 파라미터, JWT
  Authorization 헤더(query_hash 포함), 응답 파싱을 검증합니다 (실거래 없음).
- ``TestTwapListLive`` 클래스: ``.env``에 ``BITHUMB_ACCESS_KEY``/``BITHUMB_SECRET_KEY``가
  설정되어 있으면 TWAP 주문내역 조회(읽기 전용)를 실제로 호출합니다 (없으면 skip).

TWAP 주문 등록/취소(twap_new/twap_cancel)는 최소 5분 이상 지속되는 실주문이라
mock 테스트만 진행합니다 (실거래 테스트 생략).
"""

import os

import hashlib
from urllib.parse import urlencode

import jwt
import pytest
from dotenv import load_dotenv

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.order.twap_new import TwapNewInBlock
from programgarden_finance.bithumb.order.twap_cancel import TwapCancelInBlock
from programgarden_finance.bithumb.order.twap_list import TwapListInBlock

load_dotenv()

ACCESS_KEY = "test-access-key"
SECRET_KEY = "test-secret-key-0123456789abcdef0123456789abcdef"


def _order():
    bithumb = Bithumb()
    bithumb.로그인(accesskey=ACCESS_KEY, secretkey=SECRET_KEY)
    return bithumb.주문()


def _decode_auth(request) -> dict:
    auth = request.headers["Authorization"]
    assert auth.startswith("Bearer ")
    return jwt.decode(auth.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])


class TestTwapNewMock:
    def test_bid_order_with_price(self, requests_mock):
        requests_mock.post(URLS.TWAP_URL, json={"algo_order_id": "TWAP-A01B02C03D04E05F06"})

        response = _order().TWAP주문(
            TwapNewInBlock(market="KRW-BTC", side="bid", duration="3600", frequency="60", price="100000000")
        ).req()

        assert response.error_msg is None
        assert response.block.algo_order_id == "TWAP-A01B02C03D04E05F06"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {
            "market": "KRW-BTC",
            "side": "bid",
            "duration": "3600",
            "frequency": "60",
            "price": "100000000",
        }

        payload = _decode_auth(requests_mock.last_request)
        assert payload["query_hash_alg"] == "SHA512"
        expected_hash = hashlib.sha512(urlencode(sent_body, doseq=True).encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_ask_order_with_volume(self, requests_mock):
        requests_mock.post(URLS.TWAP_URL, json={"algo_order_id": "TWAP-B02C03D04E05F06A01"})

        _order().TWAP주문(
            TwapNewInBlock(market="KRW-BTC", side="ask", duration="600", frequency="30", volume="0.5")
        ).req()

        sent_body = requests_mock.last_request.json()
        assert sent_body["side"] == "ask"
        assert sent_body["volume"] == "0.5"
        assert "price" not in sent_body

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.TWAP_URL,
            status_code=400,
            json={"error": {"name": "validation_error", "message": "frequency는 15/20/30/60/120만 허용됩니다."}},
        )

        response = _order().TWAP주문(
            TwapNewInBlock(market="KRW-BTC", side="bid", duration="3600", frequency="45", price="100000000")
        ).req()

        assert response.block is None
        assert response.error_name == "validation_error"


class TestTwapCancelMock:
    def test_request_with_algo_order_id(self, requests_mock):
        requests_mock.delete(URLS.TWAP_URL, json={"algo_order_id": "C0101000000001799625"})

        response = _order().TWAP주문취소(
            TwapCancelInBlock(algo_order_id="C0101000000001799625")
        ).req()

        assert response.error_msg is None
        assert response.block.algo_order_id == "C0101000000001799625"
        assert "algo_order_id=C0101000000001799625" in requests_mock.last_request.url

        payload = _decode_auth(requests_mock.last_request)
        expected_hash = hashlib.sha512(
            urlencode({"algo_order_id": "C0101000000001799625"}, doseq=True).encode()
        ).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_error_envelope(self, requests_mock):
        requests_mock.delete(
            URLS.TWAP_URL,
            status_code=404,
            json={"error": {"name": "twap_order_not_found", "message": "TWAP 주문을 찾을 수 없습니다."}},
        )

        response = _order().TWAP주문취소(TwapCancelInBlock(algo_order_id="non-existent")).req()

        assert response.block is None
        assert response.error_name == "twap_order_not_found"


_TWAP_LIST_SAMPLE = {
    "has_next": False,
    "next_key": None,
    "orders": [
        {
            "uuid": "TWAP-A01B02C03D04E05F06",
            "side": "bid",
            "price": "100000000",
            "state": "done",
            "market": "KRW-BTC",
            "created_at": "2026-06-10T12:00:00+09:00",
            "volume": "0.001",
            "finished_at": "2026-06-10T13:00:00+09:00",
            "total_order_count": 60,
            "total_trades_count": 60,
            "progress_count": 60,
            "total_executed_amount": "100000",
            "total_executed_volume": "0.001",
            "avg_trade_price": "100000000",
            "wallet_id": "wallet-1",
        }
    ],
}


class TestTwapListMock:
    def test_request_with_params(self, requests_mock):
        requests_mock.get(URLS.TWAP_URL, json=_TWAP_LIST_SAMPLE)

        response = _order().TWAP주문조회(
            TwapListInBlock(market="KRW-BTC", state="done", limit=10)
        ).req()

        assert response.error_msg is None
        assert response.block.has_next is False
        assert response.block.orders[0].uuid == "TWAP-A01B02C03D04E05F06"
        assert response.block.orders[0].state == "done"

        assert "market=KRW-BTC" in requests_mock.last_request.url
        assert "state=done" in requests_mock.last_request.url
        assert "limit=10" in requests_mock.last_request.url

        payload = _decode_auth(requests_mock.last_request)
        assert "query_hash" in payload

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.TWAP_URL, json={"has_next": False, "next_key": None, "orders": []})

        response = _order().TWAP주문조회().req()

        assert response.error_msg is None
        assert response.block.orders == []


# ---------------------------------------------------------------------------
# Live tests (.env의 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY 필요, 없으면 skip)
# TWAP 주문내역 조회(GET /v1/twap)는 읽기 전용이므로 라이브 호출만 진행합니다.
# ---------------------------------------------------------------------------

_HAS_CREDENTIALS = bool(os.getenv("BITHUMB_ACCESS_KEY")) and bool(os.getenv("BITHUMB_SECRET_KEY"))


@pytest.mark.skipif(not _HAS_CREDENTIALS, reason="BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY가 설정되지 않았습니다.")
class TestTwapListLive:
    @pytest.fixture
    def live_order(self):
        bithumb = Bithumb()
        bithumb.로그인(
            accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
            secretkey=os.getenv("BITHUMB_SECRET_KEY"),
        )
        return bithumb.주문()

    def test_twap_list(self, live_order):
        response = live_order.TWAP주문조회().req()
        if response.error_name == "out_of_scope":
            pytest.skip("API 키에 TWAP 주문 조회 권한이 없습니다 (out_of_scope).")
        if response.error_name == "NotAllowIP":
            pytest.skip("API 키의 IP 허용 목록에 현재 클라이언트 IP가 등록되어 있지 않습니다 (NotAllowIP).")
        assert response.error_msg is None, response.error_msg
        assert response.block is not None
