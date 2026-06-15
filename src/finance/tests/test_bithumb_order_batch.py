"""빗썸(Bithumb) 다건 주문/취소(order_new_batch/order_cancel_batch) 테스트입니다.

이 파일은 ``requests_mock``으로만 검증합니다 (실거래 없음). 요청 본문, JWT
Authorization 헤더(query_hash 포함), 응답 파싱을 확인합니다.

[!] 다건 주문/취소는 ``urlencode(doseq=True)``가 아닌 자체 직렬화 규칙
(``batch_orders[i][key]=value``, ``order_ids[]=value``)으로 query_hash를
계산해야 합니다 (공식 문서 기준). 이 파일은 그 규칙을 직접 재현하여 검증합니다.

실거래 다건 주문 생성/취소 테스트는 별도 단계(예제 스크립트)에서, 사용자 확인 후
진행합니다.
"""

import hashlib

import jwt

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.order.order_new_batch import (
    BatchOrderItem,
    OrderNewBatchInBlock,
)
from programgarden_finance.bithumb.order.order_cancel_batch import OrderCancelBatchInBlock

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


def _batch_orders_query_string(batch_orders: list) -> str:
    """공식 문서의 ``batch_orders[i][key]=value`` 직렬화 규칙을 직접 재현합니다."""
    parts = []
    for index, order in enumerate(batch_orders):
        for key, value in order.items():
            parts.append(f"batch_orders[{index}][{key}]={value}")
    return "&".join(parts)


def _cancel_batch_query_string(order_ids=None, client_order_ids=None) -> str:
    """공식 문서의 ``order_ids[]=value&client_order_ids[]=value`` 직렬화 규칙을 재현합니다."""
    parts = []
    for order_id in order_ids or []:
        parts.append(f"order_ids[]={order_id}")
    for client_order_id in client_order_ids or []:
        parts.append(f"client_order_ids[]={client_order_id}")
    return "&".join(parts)


_BATCH_NEW_SAMPLE = {
    "batch_orders_response": [
        {
            "order_id": "C0101000007410713262",
            "market": "KRW-BTC",
            "side": "bid",
            "order_type": "limit",
            "created_at": "2026-01-06T12:08:11+09:00",
            "stp_type": "cancel_taker",
            "client_order_id": "20260106-test00",
        },
        {
            "name": "cross_trading",
            "message": "제출하신 주문은 귀하가 기존에 제출하신 주문과 체결될 수 있어 취소되었습니다.",
            "client_order_id": "20260106-test6",
        },
    ]
}

_BATCH_CANCEL_SAMPLE = {
    "success": [
        {
            "order_id": "C0917000000000070001",
            "client_order_id": "my-order-001",
            "created_at": "2026-06-14T12:00:01+09:00",
        }
    ],
    "fail": [
        {
            "order_id": "C0917000000000070002",
            "error": {"name": "order_not_found", "message": "주문을 찾지 못했습니다."},
        }
    ],
}


class TestOrderNewBatchMock:
    def test_request_body_and_auth_header_single_order(self, requests_mock):
        requests_mock.post(URLS.ORDER_NEW_BATCH_URL, json=_BATCH_NEW_SAMPLE)

        response = _order().다건주문(
            OrderNewBatchInBlock(
                batch_orders=[
                    BatchOrderItem(market="KRW-BTC", side="bid", order_type="limit", price="10000000", volume="0.0006")
                ]
            )
        ).req()

        assert response.error_msg is None
        assert len(response.block.batch_orders_response) == 2
        assert response.block.batch_orders_response[0].order_id == "C0101000007410713262"
        assert response.block.batch_orders_response[1].name == "cross_trading"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {
            "batch_orders": [
                {"market": "KRW-BTC", "side": "bid", "order_type": "limit", "price": "10000000", "volume": "0.0006"}
            ]
        }

        payload = _decode_auth(requests_mock.last_request)
        assert payload["query_hash_alg"] == "SHA512"
        expected_query = _batch_orders_query_string(sent_body["batch_orders"])
        assert expected_query == (
            "batch_orders[0][market]=KRW-BTC"
            "&batch_orders[0][side]=bid"
            "&batch_orders[0][order_type]=limit"
            "&batch_orders[0][price]=10000000"
            "&batch_orders[0][volume]=0.0006"
        )
        expected_hash = hashlib.sha512(expected_query.encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_request_body_and_auth_header_multiple_orders(self, requests_mock):
        requests_mock.post(URLS.ORDER_NEW_BATCH_URL, json=_BATCH_NEW_SAMPLE)

        _order().다건주문(
            OrderNewBatchInBlock(
                batch_orders=[
                    BatchOrderItem(market="KRW-BTC", side="bid", order_type="limit", price="10000000", volume="0.0006"),
                    BatchOrderItem(market="KRW-ETH", side="ask", order_type="market", volume="0.01"),
                ]
            )
        ).req()

        sent_body = requests_mock.last_request.json()
        payload = _decode_auth(requests_mock.last_request)
        expected_query = _batch_orders_query_string(sent_body["batch_orders"])
        assert expected_query == (
            "batch_orders[0][market]=KRW-BTC"
            "&batch_orders[0][side]=bid"
            "&batch_orders[0][order_type]=limit"
            "&batch_orders[0][price]=10000000"
            "&batch_orders[0][volume]=0.0006"
            "&batch_orders[1][market]=KRW-ETH"
            "&batch_orders[1][side]=ask"
            "&batch_orders[1][order_type]=market"
            "&batch_orders[1][volume]=0.01"
        )
        expected_hash = hashlib.sha512(expected_query.encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.ORDER_NEW_BATCH_URL,
            status_code=400,
            json={"error": {"name": "validation_error", "message": "batch_orders는 최소 1건 이상이어야 합니다."}},
        )

        response = _order().다건주문(
            OrderNewBatchInBlock(batch_orders=[BatchOrderItem(market="KRW-BTC", side="bid", order_type="market", volume="0.001")])
        ).req()

        assert response.block is None
        assert response.error_name == "validation_error"


class TestOrderCancelBatchMock:
    def test_request_with_order_ids(self, requests_mock):
        requests_mock.post(URLS.ORDER_CANCEL_BATCH_URL, json=_BATCH_CANCEL_SAMPLE)

        response = _order().다건주문취소(
            OrderCancelBatchInBlock(order_ids=["C0917000000000070001", "C0917000000000070002"])
        ).req()

        assert response.error_msg is None
        assert response.block.success[0].order_id == "C0917000000000070001"
        assert response.block.fail[0].error.name == "order_not_found"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {"order_ids": ["C0917000000000070001", "C0917000000000070002"]}

        payload = _decode_auth(requests_mock.last_request)
        expected_query = _cancel_batch_query_string(order_ids=sent_body["order_ids"])
        assert expected_query == "order_ids[]=C0917000000000070001&order_ids[]=C0917000000000070002"
        expected_hash = hashlib.sha512(expected_query.encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_request_with_client_order_ids(self, requests_mock):
        requests_mock.post(URLS.ORDER_CANCEL_BATCH_URL, json={"success": [], "fail": []})

        _order().다건주문취소(
            OrderCancelBatchInBlock(client_order_ids=["my-order-001", "my-order-002"])
        ).req()

        sent_body = requests_mock.last_request.json()
        assert sent_body == {"client_order_ids": ["my-order-001", "my-order-002"]}

        payload = _decode_auth(requests_mock.last_request)
        expected_query = _cancel_batch_query_string(client_order_ids=sent_body["client_order_ids"])
        assert expected_query == "client_order_ids[]=my-order-001&client_order_ids[]=my-order-002"
        expected_hash = hashlib.sha512(expected_query.encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_request_with_both_order_ids_and_client_order_ids(self, requests_mock):
        requests_mock.post(URLS.ORDER_CANCEL_BATCH_URL, json={"success": [], "fail": []})

        _order().다건주문취소(
            OrderCancelBatchInBlock(order_ids=["C001"], client_order_ids=["my-order-001"])
        ).req()

        sent_body = requests_mock.last_request.json()
        payload = _decode_auth(requests_mock.last_request)
        expected_query = _cancel_batch_query_string(
            order_ids=sent_body["order_ids"], client_order_ids=sent_body["client_order_ids"]
        )
        assert expected_query == "order_ids[]=C001&client_order_ids[]=my-order-001"
        expected_hash = hashlib.sha512(expected_query.encode()).hexdigest()
        assert payload["query_hash"] == expected_hash

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.ORDER_CANCEL_BATCH_URL,
            status_code=400,
            json={"error": {"name": "validation_error", "message": "order_ids 또는 client_order_ids가 필요합니다."}},
        )

        response = _order().다건주문취소(OrderCancelBatchInBlock(order_ids=["C001"])).req()

        assert response.block is None
        assert response.error_name == "validation_error"
