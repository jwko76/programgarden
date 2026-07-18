"""키움증권 주문 TR(현금 매수/매도, 정정/취소) 테스트.

핵심 검증: api-id 분기 (매수 kt10000 / 매도 kt10001 / 정정 kt10002 /
취소 kt10003) — KIS의 TTTC/VTTC tr_id 분기에 대응하는 헤더 검증입니다.
"""

import pytest

from programgarden_finance.kiwoom import Kiwoom
from programgarden_finance.kiwoom.config import URLS
from programgarden_finance.kiwoom.order.order_cash.blocks import OrderCashBodyBlock
from programgarden_finance.kiwoom.order.order_rvsecncl.blocks import OrderRvsecnclBodyBlock

TOKEN_URL = f"{URLS.MOCK_URL}{URLS.TOKEN_PATH}"
ORDR_URL = f"{URLS.MOCK_URL}{URLS.ORDR_PATH}"

ORDER_RESPONSE = {
    "return_code": 0, "return_msg": "주문 전송 완료 되었습니다.",
    "ord_no": "0000117057",
}


def _login(requests_mock) -> Kiwoom:
    requests_mock.post(TOKEN_URL, json={"token": "tok", "return_code": 0})
    client = Kiwoom(paper_trading=True, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


class TestOrderCashApiIdMatrix:
    """매수/매도 api-id를 전수 단언합니다."""

    @pytest.mark.parametrize(
        "side,expected_api_id",
        [("buy", "kt10000"), ("sell", "kt10001")],
    )
    def test_api_id_by_side(self, requests_mock, side, expected_api_id):
        kiwoom = _login(requests_mock)
        requests_mock.post(ORDR_URL, json=ORDER_RESPONSE)

        body = OrderCashBodyBlock(acnt_no="", stk_cd="005930", ord_qty="10", ord_uv="60000")
        order = kiwoom.order()
        tr = order.order_cash_buy(body) if side == "buy" else order.order_cash_sell(body)
        resp = tr.req()

        assert resp.error_msg is None
        assert resp.block.ord_no == "0000117057"
        assert requests_mock.last_request.headers["api-id"] == expected_api_id


class TestOrderCashMock:
    def test_buy_body_fields(self, requests_mock):
        kiwoom = _login(requests_mock)
        requests_mock.post(ORDR_URL, json=ORDER_RESPONSE)

        resp = kiwoom.order().order_cash_buy(
            OrderCashBodyBlock(acnt_no="", stk_cd="005930", ord_qty="10", ord_uv="60000")
        ).req()

        assert resp.error_msg is None
        body = requests_mock.last_request.json()
        # 키움은 소문자 필드명을 그대로 사용 (KIS의 대문자 alias와 다름)
        assert body["acnt_no"] == "12345678"  # 자동 채움
        assert body["stk_cd"] == "005930"
        assert body["ord_qty"] == "10"
        assert body["ord_uv"] == "60000"
        assert body["dmst_stex_tp"] == "KRX"

        headers = requests_mock.last_request.headers
        assert headers["authorization"] == "Bearer tok"
        assert "appkey" not in headers  # TR 요청에는 appkey/secretkey 헤더가 없음
        assert "appsecret" not in headers

    def test_market_order_price_zero(self, requests_mock):
        kiwoom = _login(requests_mock)
        requests_mock.post(ORDR_URL, json=ORDER_RESPONSE)

        kiwoom.order().order_cash_sell(
            OrderCashBodyBlock(acnt_no="", stk_cd="005930", ord_qty="10")
        ).req()

        body = requests_mock.last_request.json()
        assert body["ord_uv"] == "0"  # 시장가는 단가 0 (기본값)

    def test_order_rejection_return_code(self, requests_mock):
        kiwoom = _login(requests_mock)
        requests_mock.post(
            ORDR_URL,
            json={"return_code": 9, "return_msg": "주문가능금액을 초과했습니다."},
        )
        resp = kiwoom.order().order_cash_buy(
            OrderCashBodyBlock(acnt_no="", stk_cd="005930", ord_qty="99999", ord_uv="60000")
        ).req()

        assert resp.error_msg is not None
        assert resp.return_code == 9
        assert resp.block is None


class TestOrderRvsecnclApiIdMatrix:
    @pytest.mark.parametrize(
        "mode,expected_api_id",
        [("modify", "kt10002"), ("cancel", "kt10003")],
    )
    def test_api_id_by_mode(self, requests_mock, mode, expected_api_id):
        kiwoom = _login(requests_mock)
        requests_mock.post(ORDR_URL, json=ORDER_RESPONSE)

        body = OrderRvsecnclBodyBlock(acnt_no="", orig_ord_no="0000117057", stk_cd="005930")
        order = kiwoom.order()
        tr = order.order_modify(body) if mode == "modify" else order.order_cancel(body)
        resp = tr.req()

        assert resp.error_msg is None
        assert requests_mock.last_request.headers["api-id"] == expected_api_id

    def test_cancel_body_fields(self, requests_mock):
        kiwoom = _login(requests_mock)
        requests_mock.post(ORDR_URL, json=ORDER_RESPONSE)

        kiwoom.order().order_cancel(
            OrderRvsecnclBodyBlock(acnt_no="", orig_ord_no="0000117057", stk_cd="005930")
        ).req()

        body = requests_mock.last_request.json()
        assert body["orig_ord_no"] == "0000117057"
        assert body["stk_cd"] == "005930"
        assert body["ord_qty"] == "0"
        assert body["ord_uv"] == "0"


class TestExpiredTokenRetry:
    def test_401_response_triggers_reissue_and_retry(self, requests_mock):
        kiwoom = _login(requests_mock)
        kiwoom.token_manager.ensure_fresh_token()

        # 1차 응답: HTTP 401(만료) → 재발급 후 재시도 → 2차 응답: 성공
        requests_mock.post(
            ORDR_URL,
            [
                {"status_code": 401, "json": {"return_code": 1, "return_msg": "토큰이 만료되었습니다."}},
                {"json": ORDER_RESPONSE},
            ],
        )
        resp = kiwoom.order().order_cash_buy(
            OrderCashBodyBlock(acnt_no="", stk_cd="005930", ord_qty="1", ord_uv="60000")
        ).req()

        assert resp.error_msg is None
        assert resp.block.ord_no == "0000117057"
        order_calls = [
            r for r in requests_mock.request_history
            if URLS.ORDR_PATH in r.path
        ]
        assert len(order_calls) == 2


class TestKoreanAliases:
    def test_order_korean_aliases_exist(self, requests_mock):
        kiwoom = _login(requests_mock)
        order = kiwoom.order()
        assert order.현금매수 is not None
        assert order.현금매도 is not None
        assert order.정정 is not None
        assert order.취소 is not None
