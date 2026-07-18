"""키움증권 계좌 TR(잔고/주문인출가능금액) 테스트 (requests_mock 기반)."""

import pytest

from programgarden_finance.kiwoom import Kiwoom
from programgarden_finance.kiwoom.config import URLS
from programgarden_finance.kiwoom.accno.inquire_balance import InquireBalanceInBlock
from programgarden_finance.kiwoom.accno.inquire_psbl_order import InquirePsblOrderInBlock

TOKEN_URL = f"{URLS.MOCK_URL}{URLS.TOKEN_PATH}"
ACNT_URL = f"{URLS.MOCK_URL}{URLS.ACNT_PATH}"

# 리스트 키·요약 필드명은 2026-07-18 모의서버 라이브 응답으로 확인됨
BALANCE_RESPONSE = {
    "return_code": 0, "return_msg": "정상",
    "acnt_evlt_remn_indv_tot": [
        {
            "stk_cd": "005930", "stk_nm": "삼성전자",
            "rmnd_qty": "10", "pur_pric": "70000",
            "cur_prc": "71900", "evlt_amt": "719000",
            "evltv_prft": "19000", "prft_rt": "2.71",
        },
    ],
    "prsm_dpst_aset_amt": "000000010000000",
    "tot_pur_amt": "700000",
    "tot_evlt_amt": "10719000",
    "tot_evlt_pl": "19000",
    "tot_prft_rt": "000000002.71",
}


@pytest.fixture
def kiwoom(requests_mock) -> Kiwoom:
    requests_mock.post(TOKEN_URL, json={"token": "tok", "return_code": 0})
    client = Kiwoom(paper_trading=True, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


class TestInquireBalanceMock:
    def test_success_with_auto_account(self, kiwoom, requests_mock):
        requests_mock.post(ACNT_URL, json=BALANCE_RESPONSE)

        # params 생략 → 로그인 시 등록한 계좌번호 자동 사용
        resp = kiwoom.accno().inquire_balance().req()

        assert resp.error_msg is None
        assert len(resp.blocks) == 1
        assert resp.blocks[0].stk_cd == "005930"
        assert resp.blocks[0].rmnd_qty == "10"
        assert resp.blocks[0].prft_rt == "2.71"
        assert resp.block.prsm_dpst_aset_amt == "000000010000000"
        assert resp.block.tot_prft_rt == "000000002.71"

        req = requests_mock.last_request
        assert req.headers["api-id"] == "kt00018"
        assert req.headers["cont-yn"] == "N"
        body = req.json()
        assert body["acnt_no"] == "12345678"

    def test_error_envelope(self, kiwoom, requests_mock):
        requests_mock.post(
            ACNT_URL,
            json={"return_code": 5, "return_msg": "계좌 조회 실패"},
        )
        resp = kiwoom.accno().inquire_balance().req()
        assert resp.error_msg is not None
        assert resp.return_code == 5
        assert resp.blocks is None

    def test_real_mode_domain(self, requests_mock):
        requests_mock.post(
            f"{URLS.PROD_URL}{URLS.TOKEN_PATH}", json={"token": "tok", "return_code": 0}
        )
        requests_mock.post(f"{URLS.PROD_URL}{URLS.ACNT_PATH}", json=BALANCE_RESPONSE)
        kiwoom_real = Kiwoom(paper_trading=False, use_token_file_cache=False)
        kiwoom_real.login(appkey="ak", appsecretkey="sk", account_no="12345678")

        resp = kiwoom_real.accno().inquire_balance(
            InquireBalanceInBlock(acnt_no="12345678")
        ).req()

        assert resp.error_msg is None
        assert requests_mock.last_request.url.startswith(URLS.PROD_URL)


class TestInquirePsblOrderMock:
    def test_success(self, kiwoom, requests_mock):
        requests_mock.post(
            ACNT_URL,
            json={
                "return_code": 0, "return_msg": "정상",
                "ord_alow_amt": "10000000",
                "max_buy_amt": "10000000",
                "max_buy_qty": "139",
            },
        )
        resp = kiwoom.accno().inquire_psbl_order(
            InquirePsblOrderInBlock(acnt_no="", stk_cd="005930", uv="71900")
        ).req()

        assert resp.error_msg is None
        assert resp.block.ord_alow_amt == "10000000"
        assert resp.block.max_buy_qty == "139"

        req = requests_mock.last_request
        assert req.headers["api-id"] == "kt00010"
        body = req.json()
        assert body["acnt_no"] == "12345678"  # 빈 값 → 자동 채움
        assert body["stk_cd"] == "005930"
