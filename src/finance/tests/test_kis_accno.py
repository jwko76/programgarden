"""KIS 계좌 TR(잔고/매수가능조회) 테스트 (requests_mock 기반)."""

import pytest

from programgarden_finance import Kis
from programgarden_finance.kis.config import URLS
from programgarden_finance.kis.accno.inquire_balance import InquireBalanceInBlock
from programgarden_finance.kis.accno.inquire_psbl_order import InquirePsblOrderInBlock

TOKEN_URL = f"{URLS.PAPER_URL}{URLS.TOKEN_PATH}"
BALANCE_URL = f"{URLS.PAPER_URL}{URLS.INQUIRE_BALANCE_PATH}"
PSBL_URL = f"{URLS.PAPER_URL}{URLS.INQUIRE_PSBL_ORDER_PATH}"

BALANCE_RESPONSE = {
    "rt_cd": "0", "msg_cd": "MCA00000", "msg1": "OK",
    "output1": [
        {
            "pdno": "005930", "prdt_name": "삼성전자",
            "hldg_qty": "10", "ord_psbl_qty": "10",
            "pchs_avg_pric": "70000.00", "prpr": "71900",
            "evlu_amt": "719000", "evlu_pfls_amt": "19000",
            "evlu_pfls_rt": "2.71",
        },
    ],
    "output2": [
        {
            "dnca_tot_amt": "10000000", "prvs_rcdl_excc_amt": "9990000",
            "tot_evlu_amt": "10719000", "pchs_amt_smtl_amt": "700000",
            "evlu_pfls_smtl_amt": "19000",
        }
    ],
}


@pytest.fixture
def kis(requests_mock) -> Kis:
    requests_mock.post(TOKEN_URL, json={"access_token": "tok", "expires_in": 86400})
    client = Kis(paper_trading=True, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678", account_product_code="01")
    return client


class TestInquireBalanceMock:
    def test_success_with_auto_account(self, kis, requests_mock):
        requests_mock.get(BALANCE_URL, json=BALANCE_RESPONSE)

        # params 생략 → 로그인 시 등록한 계좌번호 자동 사용
        resp = kis.accno().inquire_balance().req()

        assert resp.error_msg is None
        assert len(resp.blocks) == 1
        assert resp.blocks[0].pdno == "005930"
        assert resp.blocks[0].hldg_qty == "10"
        assert resp.block2.dnca_tot_amt == "10000000"

        req = requests_mock.last_request
        assert req.headers["tr_id"] == "VTTC8434R"  # 모의투자 tr_id
        assert req.qs["cano"] == ["12345678"]
        assert req.qs["acnt_prdt_cd"] == ["01"]

    def test_real_mode_tr_id(self, requests_mock):
        requests_mock.post(
            f"{URLS.REAL_URL}{URLS.TOKEN_PATH}",
            json={"access_token": "tok", "expires_in": 86400},
        )
        requests_mock.get(
            f"{URLS.REAL_URL}{URLS.INQUIRE_BALANCE_PATH}", json=BALANCE_RESPONSE
        )
        kis_real = Kis(paper_trading=False, use_token_file_cache=False)
        kis_real.login(appkey="ak", appsecretkey="sk", account_no="12345678")

        resp = kis_real.accno().inquire_balance(
            InquireBalanceInBlock(cano="12345678")
        ).req()

        assert resp.error_msg is None
        assert requests_mock.last_request.headers["tr_id"] == "TTTC8434R"  # 실전 tr_id


class TestInquirePsblOrderMock:
    def test_success(self, kis, requests_mock):
        requests_mock.get(
            PSBL_URL,
            json={
                "rt_cd": "0", "msg_cd": "MCA00000", "msg1": "OK",
                "output": {
                    "ord_psbl_cash": "10000000",
                    "max_buy_amt": "10000000",
                    "max_buy_qty": "139",
                },
            },
        )
        resp = kis.accno().inquire_psbl_order(
            InquirePsblOrderInBlock(cano="", pdno="005930", ord_unpr="71900")
        ).req()

        assert resp.error_msg is None
        assert resp.block.ord_psbl_cash == "10000000"
        assert resp.block.max_buy_qty == "139"

        req = requests_mock.last_request
        assert req.headers["tr_id"] == "VTTC8908R"
        assert req.qs["cano"] == ["12345678"]  # 빈 값 → 자동 채움
        assert req.qs["pdno"] == ["005930"]
