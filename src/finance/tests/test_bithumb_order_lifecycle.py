"""빗썸(Bithumb) 주문 생성/취소(order_new/order_cancel) 테스트입니다.

이 파일은 ``requests_mock``으로만 검증합니다 (실거래 없음). 요청 본문/쿼리
파라미터, JWT Authorization 헤더(query_hash 포함), 응답 파싱을 확인합니다.

실거래 주문 생성/취소 테스트는 별도 단계에서, 사용자 확인 후 진행합니다.
"""

import hashlib
from urllib.parse import urlencode

import jwt

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.order.order_new import OrderNewInBlock
from programgarden_finance.bithumb.order.order_cancel import OrderCancelInBlock

ACCESS_KEY = "test-access-key"
SECRET_KEY = "test-secret-key-0123456789abcdef0123456789abcdef"

_ORDER_NEW_SAMPLE = {
    "order_id": "C0101000000001799653",
    "market": "KRW-BTC",
    "side": "bid",
    "order_type": "limit",
    "created_at": "2026-06-14T12:00:00+09:00",
    "client_order_id": None,
    "stp_type": "cancel_taker",
}

_ORDER_CANCEL_SAMPLE = {
    "order_id": "C0101000000001799653",
    "client_order_id": None,
    "created_at": "2026-06-14T12:00:01+09:00",
}


def _order():
    bithumb = Bithumb()
    bithumb.로그인(accesskey=ACCESS_KEY, secretkey=SECRET_KEY)
    return bithumb.주문()


def _decode_auth(request) -> dict:
    auth = request.headers["Authorization"]
    assert auth.startswith("Bearer ")
    return jwt.decode(auth.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])


class TestOrderNewMock:
    def test_request_body_and_auth_header(self, requests_mock):
        requests_mock.post(URLS.ORDER_NEW_URL, status_code=201, json=_ORDER_NEW_SAMPLE)

        response = _order().주문하기(
            OrderNewInBlock(
                market="KRW-BTC",
                side="bid",
                order_type="limit",
                price="10000000",
                volume="0.0006",
            )
        ).req()

        assert response.error_msg is None
        assert response.block.order_id == "C0101000000001799653"
        assert response.block.order_type == "limit"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {
            "market": "KRW-BTC",
            "side": "bid",
            "order_type": "limit",
            "price": "10000000",
            "volume": "0.0006",
        }

        payload = _decode_auth(requests_mock.last_request)
        assert payload["access_key"] == ACCESS_KEY
        assert payload["query_hash_alg"] == "SHA512"
        expected_hash = hashlib.sha512(urlencode(sent_body, doseq=True).encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_market_price_order_omits_volume(self, requests_mock):
        requests_mock.post(URLS.ORDER_NEW_URL, status_code=201, json={**_ORDER_NEW_SAMPLE, "order_type": "price"})

        _order().주문하기(
            OrderNewInBlock(market="KRW-BTC", side="bid", order_type="price", price="10000000")
        ).req()

        sent_body = requests_mock.last_request.json()
        assert "volume" not in sent_body
        assert sent_body["order_type"] == "price"

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.ORDER_NEW_URL,
            status_code=400,
            json={"error": {"name": "under_min_total_bid", "message": "최소 주문 금액 미달"}},
        )

        response = _order().주문하기(
            OrderNewInBlock(market="KRW-BTC", side="bid", order_type="limit", price="1", volume="0.0001")
        ).req()

        assert response.block is None
        assert response.error_name == "under_min_total_bid"
        assert response.error_msg == "최소 주문 금액 미달"


class TestOrderCancelMock:
    def test_request_with_order_id(self, requests_mock):
        requests_mock.delete(URLS.ORDER_CANCEL_URL, json=_ORDER_CANCEL_SAMPLE)

        response = _order().주문취소(
            OrderCancelInBlock(order_id="C0101000000001799653")
        ).req()

        assert response.error_msg is None
        assert response.block.order_id == "C0101000000001799653"
        assert "order_id=C0101000000001799653" in requests_mock.last_request.url

        payload = _decode_auth(requests_mock.last_request)
        assert "query_hash" in payload
        expected_hash = hashlib.sha512(
            urlencode({"order_id": "C0101000000001799653"}, doseq=True).encode()
        ).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_error_envelope(self, requests_mock):
        requests_mock.delete(
            URLS.ORDER_CANCEL_URL,
            status_code=404,
            json={"error": {"name": "order_not_found", "message": "주문을 찾을 수 없습니다."}},
        )

        response = _order().주문취소(OrderCancelInBlock(order_id="non-existent")).req()

        assert response.block is None
        assert response.error_name == "order_not_found"
        assert response.status_code == 404
