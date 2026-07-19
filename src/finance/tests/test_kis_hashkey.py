"""KIS hashkey(POST 본문 위변조 방지) 헤더 테스트 (requests_mock 기반).

핵심 검증: use_hashkey=True일 때만 /uapi/hashkey를 호출하고 그 결과를
주문 요청의 hashkey 헤더에 첨부한다. 기본값(False)은 기존 동작과 동일해야
하며, hashkey 발급 실패는 주문 자체를 막지 않아야 한다(경고만).
"""

from programgarden_finance import Kis
from programgarden_finance.kis.config import URLS
from programgarden_finance.kis.order.order_cash.blocks import OrderCashBodyBlock

TOKEN_URL = f"{URLS.PAPER_URL}{URLS.TOKEN_PATH}"
ORDER_URL = f"{URLS.PAPER_URL}{URLS.ORDER_CASH_PATH}"
HASHKEY_URL = f"{URLS.PAPER_URL}{URLS.HASHKEY_PATH}"

ORDER_RESPONSE = {
    "rt_cd": "0", "msg_cd": "APBK0013", "msg1": "주문 전송 완료 되었습니다.",
    "output": {"KRX_FWDG_ORD_ORGNO": "00950", "ODNO": "0000117057", "ORD_TMD": "121052"},
}


def _login(requests_mock, use_hashkey: bool = False) -> Kis:
    requests_mock.post(TOKEN_URL, json={"access_token": "tok", "expires_in": 86400})
    client = Kis(paper_trading=True, use_token_file_cache=False, use_hashkey=use_hashkey)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


class TestHashkeyDisabledByDefault:
    def test_no_hashkey_call_when_disabled(self, requests_mock):
        kis = _login(requests_mock, use_hashkey=False)
        requests_mock.post(ORDER_URL, json=ORDER_RESPONSE)

        resp = kis.order().order_cash_buy(
            OrderCashBodyBlock(cano="", pdno="005930", ord_qty="10", ord_unpr="60000")
        ).req()

        assert resp.error_msg is None
        hashkey_calls = [r for r in requests_mock.request_history if URLS.HASHKEY_PATH in r.path]
        assert len(hashkey_calls) == 0
        assert "hashkey" not in requests_mock.last_request.headers


class TestHashkeyEnabled:
    def test_hashkey_fetched_and_attached(self, requests_mock):
        kis = _login(requests_mock, use_hashkey=True)
        requests_mock.post(HASHKEY_URL, json={"HASH": "deadbeef1234"})
        requests_mock.post(ORDER_URL, json=ORDER_RESPONSE)

        resp = kis.order().order_cash_buy(
            OrderCashBodyBlock(cano="", pdno="005930", ord_qty="10", ord_unpr="60000")
        ).req()

        assert resp.error_msg is None
        hashkey_calls = [r for r in requests_mock.request_history if URLS.HASHKEY_PATH in r.path]
        assert len(hashkey_calls) == 1
        # hashkey 요청 본문은 주문 본문과 동일해야 함 (위변조 방지 목적)
        assert hashkey_calls[0].json()["PDNO"] == "005930"
        order_calls = [r for r in requests_mock.request_history if URLS.ORDER_CASH_PATH in r.path]
        assert order_calls[-1].headers["hashkey"] == "deadbeef1234"

    def test_hashkey_failure_does_not_block_order(self, requests_mock):
        """hashkey 발급 실패해도 주문 요청은 정상 진행되어야 한다 (권장 옵션이지 필수 아님)."""
        kis = _login(requests_mock, use_hashkey=True)
        requests_mock.post(HASHKEY_URL, status_code=500, json={})
        requests_mock.post(ORDER_URL, json=ORDER_RESPONSE)

        resp = kis.order().order_cash_buy(
            OrderCashBodyBlock(cano="", pdno="005930", ord_qty="10", ord_unpr="60000")
        ).req()

        assert resp.error_msg is None
        assert resp.block.odno == "0000117057"
        assert "hashkey" not in requests_mock.last_request.headers

    def test_quotation_get_request_skips_hashkey(self, requests_mock):
        """GET 시세 조회는 hashkey 대상이 아님 (POST 주문 전용)."""
        from programgarden_finance.kis.quotations.inquire_price.blocks import InquirePriceInBlock

        kis = _login(requests_mock, use_hashkey=True)
        requests_mock.get(
            f"{URLS.PAPER_URL}{URLS.INQUIRE_PRICE_PATH}",
            json={"rt_cd": "0", "output": {"stck_prpr": "71900"}},
        )
        kis.quotations().inquire_price(InquirePriceInBlock(fid_input_iscd="005930")).req()

        hashkey_calls = [r for r in requests_mock.request_history if URLS.HASHKEY_PATH in r.path]
        assert len(hashkey_calls) == 0

    # 주의: req_async()는 aiohttp를 사용하며 requests_mock이 가로채지 못합니다
    # (이 코드베이스의 다른 KIS 테스트도 req_async를 mock하지 않습니다).
    # 비동기 경로의 hashkey 첨부 로직은 동기 경로와 동일한 _resolve_hashkey_*
    # 헬퍼를 공유하므로 위 동기 테스트로 충분히 커버됩니다.
