"""KIS 주문 TR(현금 매수/매도, 정정취소) 테스트.

핵심 검증: 실전/모의 tr_id 분기 (TTTC↔VTTC) — 잘못된 tr_id는 실주문 사고로
이어질 수 있어 양 모드 모두 헤더를 단언합니다.
"""

import pytest

from programgarden_finance import Kis
from programgarden_finance.kis.config import URLS
from programgarden_finance.kis.order.order_cash.blocks import OrderCashBodyBlock
from programgarden_finance.kis.order.order_rvsecncl.blocks import OrderRvsecnclBodyBlock

ORDER_RESPONSE = {
    "rt_cd": "0", "msg_cd": "APBK0013", "msg1": "주문 전송 완료 되었습니다.",
    "output": {
        "KRX_FWDG_ORD_ORGNO": "00950",
        "ODNO": "0000117057",
        "ORD_TMD": "121052",
    },
}


def _login(paper: bool, requests_mock) -> Kis:
    base = URLS.PAPER_URL if paper else URLS.REAL_URL
    requests_mock.post(
        f"{base}{URLS.TOKEN_PATH}",
        json={"access_token": "tok", "expires_in": 86400},
    )
    client = Kis(paper_trading=paper, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


class TestOrderCashTrIdMatrix:
    """매수/매도 × 실전/모의 4가지 조합의 tr_id를 전수 단언합니다."""

    @pytest.mark.parametrize(
        "paper,side,expected_tr_id",
        [
            (False, "buy", "TTTC0802U"),
            (False, "sell", "TTTC0801U"),
            (True, "buy", "VTTC0802U"),
            (True, "sell", "VTTC0801U"),
        ],
    )
    def test_tr_id_by_mode_and_side(self, requests_mock, paper, side, expected_tr_id):
        kis = _login(paper, requests_mock)
        base = URLS.PAPER_URL if paper else URLS.REAL_URL
        requests_mock.post(f"{base}{URLS.ORDER_CASH_PATH}", json=ORDER_RESPONSE)

        body = OrderCashBodyBlock(cano="", pdno="005930", ord_qty="10", ord_unpr="60000")
        order = kis.order()
        tr = order.order_cash_buy(body) if side == "buy" else order.order_cash_sell(body)
        resp = tr.req()

        assert resp.error_msg is None
        assert resp.block.odno == "0000117057"
        assert requests_mock.last_request.headers["tr_id"] == expected_tr_id


class TestOrderCashMock:
    def test_buy_body_uppercase_aliases(self, requests_mock):
        kis = _login(True, requests_mock)
        requests_mock.post(f"{URLS.PAPER_URL}{URLS.ORDER_CASH_PATH}", json=ORDER_RESPONSE)

        resp = kis.order().order_cash_buy(
            OrderCashBodyBlock(cano="", pdno="005930", ord_dvsn="00", ord_qty="10", ord_unpr="60000")
        ).req()

        assert resp.error_msg is None
        body = requests_mock.last_request.json()
        # KIS는 대문자 키를 요구
        assert body["CANO"] == "12345678"  # 자동 채움
        assert body["ACNT_PRDT_CD"] == "01"
        assert body["PDNO"] == "005930"
        assert body["ORD_DVSN"] == "00"
        assert body["ORD_QTY"] == "10"
        assert body["ORD_UNPR"] == "60000"

    def test_market_order_price_zero(self, requests_mock):
        kis = _login(True, requests_mock)
        requests_mock.post(f"{URLS.PAPER_URL}{URLS.ORDER_CASH_PATH}", json=ORDER_RESPONSE)

        kis.order().order_cash_sell(
            OrderCashBodyBlock(cano="", pdno="005930", ord_dvsn="01", ord_qty="10")
        ).req()

        body = requests_mock.last_request.json()
        assert body["ORD_DVSN"] == "01"
        assert body["ORD_UNPR"] == "0"  # 시장가는 단가 0

    def test_order_rejection_rt_cd(self, requests_mock):
        kis = _login(True, requests_mock)
        requests_mock.post(
            f"{URLS.PAPER_URL}{URLS.ORDER_CASH_PATH}",
            json={"rt_cd": "1", "msg_cd": "APBK0919", "msg1": "주문가능금액을 초과했습니다."},
        )
        resp = kis.order().order_cash_buy(
            OrderCashBodyBlock(cano="", pdno="005930", ord_qty="99999", ord_unpr="60000")
        ).req()

        assert resp.error_msg is not None
        assert resp.rt_cd == "1"
        assert resp.block is None


class TestOrderRvsecnclMock:
    @pytest.mark.parametrize(
        "paper,expected_tr_id",
        [(False, "TTTC0803U"), (True, "VTTC0803U")],
    )
    def test_cancel_tr_id(self, requests_mock, paper, expected_tr_id):
        kis = _login(paper, requests_mock)
        base = URLS.PAPER_URL if paper else URLS.REAL_URL
        requests_mock.post(f"{base}{URLS.ORDER_RVSECNCL_PATH}", json=ORDER_RESPONSE)

        resp = kis.order().order_rvsecncl(
            OrderRvsecnclBodyBlock(cano="", orgn_odno="0000117057")
        ).req()

        assert resp.error_msg is None
        assert requests_mock.last_request.headers["tr_id"] == expected_tr_id

    def test_cancel_full_quantity_defaults(self, requests_mock):
        kis = _login(True, requests_mock)
        requests_mock.post(f"{URLS.PAPER_URL}{URLS.ORDER_RVSECNCL_PATH}", json=ORDER_RESPONSE)

        kis.order().order_rvsecncl(
            OrderRvsecnclBodyBlock(cano="", orgn_odno="0000117057")
        ).req()

        body = requests_mock.last_request.json()
        assert body["ORGN_ODNO"] == "0000117057"
        assert body["RVSE_CNCL_DVSN_CD"] == "02"  # 취소
        assert body["QTY_ALL_ORD_YN"] == "Y"      # 잔량 전부
        assert body["ORD_QTY"] == "0"
        assert body["ORD_UNPR"] == "0"


class TestOrderRvsecnclModify:
    """정정(RVSE_CNCL_DVSN_CD=01) 경로 — 취소(02)와 같은 TR을 공유하므로
    구분 코드가 실제로 정정을 요청하는지 별도로 검증합니다."""

    @pytest.mark.parametrize(
        "paper,expected_tr_id",
        [(False, "TTTC0803U"), (True, "VTTC0803U")],
    )
    def test_modify_tr_id(self, requests_mock, paper, expected_tr_id):
        kis = _login(paper, requests_mock)
        base = URLS.PAPER_URL if paper else URLS.REAL_URL
        requests_mock.post(f"{base}{URLS.ORDER_RVSECNCL_PATH}", json=ORDER_RESPONSE)

        resp = kis.order().order_rvsecncl(
            OrderRvsecnclBodyBlock(
                cano="", orgn_odno="0000117057", rvse_cncl_dvsn_cd="01",
                ord_qty="5", ord_unpr="61000", qty_all_ord_yn="N",
            )
        ).req()

        assert resp.error_msg is None
        assert requests_mock.last_request.headers["tr_id"] == expected_tr_id

    def test_modify_body_fields(self, requests_mock):
        kis = _login(True, requests_mock)
        requests_mock.post(f"{URLS.PAPER_URL}{URLS.ORDER_RVSECNCL_PATH}", json=ORDER_RESPONSE)

        kis.order().order_rvsecncl(
            OrderRvsecnclBodyBlock(
                cano="", orgn_odno="0000117057", rvse_cncl_dvsn_cd="01",
                ord_dvsn="00", ord_qty="5", ord_unpr="61000", qty_all_ord_yn="N",
            )
        ).req()

        body = requests_mock.last_request.json()
        assert body["RVSE_CNCL_DVSN_CD"] == "01"  # 정정 (02 취소와 구분)
        assert body["ORGN_ODNO"] == "0000117057"
        assert body["ORD_UNPR"] == "61000"
        assert body["ORD_QTY"] == "5"
        assert body["QTY_ALL_ORD_YN"] == "N"

    def test_modify_full_quantity_defaults(self, requests_mock):
        """quantity 미지정 시 정정도 취소와 동일하게 잔량 전부(Y)로 처리됩니다."""
        kis = _login(True, requests_mock)
        requests_mock.post(f"{URLS.PAPER_URL}{URLS.ORDER_RVSECNCL_PATH}", json=ORDER_RESPONSE)

        kis.order().order_rvsecncl(
            OrderRvsecnclBodyBlock(cano="", orgn_odno="0000117057", rvse_cncl_dvsn_cd="01", ord_unpr="61000")
        ).req()

        body = requests_mock.last_request.json()
        assert body["QTY_ALL_ORD_YN"] == "Y"
        assert body["ORD_QTY"] == "0"


class TestExpiredTokenRetry:
    def test_expired_token_response_triggers_reissue_and_retry(self, requests_mock):
        kis = _login(True, requests_mock)
        # 토큰을 미리 발급
        kis.token_manager.ensure_fresh_token()

        # 1차 응답: 토큰 만료(EGW00123) → 재발급 후 재시도 → 2차 응답: 성공
        requests_mock.post(
            f"{URLS.PAPER_URL}{URLS.ORDER_CASH_PATH}",
            [
                {"json": {"rt_cd": "1", "msg_cd": "EGW00123", "msg1": "기간이 만료된 token 입니다."}},
                {"json": ORDER_RESPONSE},
            ],
        )
        resp = kis.order().order_cash_buy(
            OrderCashBodyBlock(cano="", pdno="005930", ord_qty="1", ord_unpr="60000")
        ).req()

        assert resp.error_msg is None
        assert resp.block.odno == "0000117057"
        # 주문 엔드포인트가 2회 호출됨 (만료 → 재시도)
        order_calls = [
            r for r in requests_mock.request_history
            if URLS.ORDER_CASH_PATH in r.path
        ]
        assert len(order_calls) == 2
