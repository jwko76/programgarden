"""키움증권 시세 TR(현재가/호가/일봉) 테스트 (requests_mock 기반, 실제 API 호출 없음)."""

import pytest

from programgarden_finance.kiwoom import Kiwoom
from programgarden_finance.kiwoom.config import URLS
from programgarden_finance.kiwoom.quotations.inquire_price import InquirePriceInBlock
from programgarden_finance.kiwoom.quotations.inquire_asking_price import InquireAskingPriceInBlock
from programgarden_finance.kiwoom.quotations.inquire_daily_itemchartprice import (
    InquireDailyItemChartPriceInBlock,
)

TOKEN_URL = f"{URLS.MOCK_URL}{URLS.TOKEN_PATH}"


@pytest.fixture
def kiwoom(requests_mock) -> Kiwoom:
    requests_mock.post(TOKEN_URL, json={"token": "tok", "return_code": 0})
    client = Kiwoom(paper_trading=True, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


class TestInquirePriceMock:
    def test_success(self, kiwoom, requests_mock):
        requests_mock.post(
            f"{URLS.MOCK_URL}{URLS.STKINFO_PATH}",
            json={
                "return_code": 0, "return_msg": "정상",
                "stk_cd": "005930", "stk_nm": "삼성전자",
                "cur_prc": "71900", "pred_pre": "-100", "flu_rt": "-0.14",
                "open_pric": "72000", "high_pric": "72100", "low_pric": "71500",
                "trde_qty": "9999999",
            },
        )
        resp = kiwoom.quotations().inquire_price(
            InquirePriceInBlock(stk_cd="005930")
        ).req()

        assert resp.error_msg is None
        assert resp.return_code == 0
        assert resp.block.cur_prc == "71900"
        assert resp.block.stk_nm == "삼성전자"

        req = requests_mock.last_request
        assert req.headers["api-id"] == "ka10001"
        assert req.headers["authorization"] == "Bearer tok"
        assert req.headers["cont-yn"] == "N"
        body = req.json()
        assert body["stk_cd"] == "005930"

    def test_error_return_code(self, kiwoom, requests_mock):
        requests_mock.post(
            f"{URLS.MOCK_URL}{URLS.STKINFO_PATH}",
            json={"return_code": 1, "return_msg": "유효하지 않은 종목"},
        )
        resp = kiwoom.quotations().inquire_price(
            InquirePriceInBlock(stk_cd="999999")
        ).req()
        assert resp.error_msg is not None
        assert resp.return_code == 1
        assert resp.block is None

    def test_http_error_status(self, kiwoom, requests_mock):
        requests_mock.post(
            f"{URLS.MOCK_URL}{URLS.STKINFO_PATH}",
            status_code=500,
            json={"return_code": 0},
        )
        resp = kiwoom.quotations().inquire_price(
            InquirePriceInBlock(stk_cd="005930")
        ).req()
        assert resp.error_msg is not None


class TestInquireAskingPriceMock:
    def test_success(self, kiwoom, requests_mock):
        requests_mock.post(
            f"{URLS.MOCK_URL}{URLS.MRKCOND_PATH}",
            json={
                "return_code": 0, "return_msg": "정상",
                "sel_1th_pre_req_pric": "72000", "buy_1th_pre_req_pric": "71900",
                "sel_1th_pre_req_qty": "1000", "buy_1th_pre_req_qty": "2000",
                "tot_sel_req": "50000", "tot_buy_req": "60000",
            },
        )
        resp = kiwoom.quotations().inquire_asking_price(
            InquireAskingPriceInBlock(stk_cd="005930")
        ).req()

        assert resp.error_msg is None
        assert resp.block.sel_1th_pre_req_pric == "72000"
        assert resp.block.buy_1th_pre_req_pric == "71900"
        assert requests_mock.last_request.headers["api-id"] == "ka10004"


class TestInquireDailyItemChartPriceMock:
    def test_success_filters_empty_candles(self, kiwoom, requests_mock):
        requests_mock.post(
            f"{URLS.MOCK_URL}{URLS.CHART_PATH}",
            json={
                "return_code": 0, "return_msg": "정상",
                "stk_dt_pole": [
                    {"dt": "20260711", "open_pric": "72000", "high_pric": "72100",
                     "low_pric": "71500", "cur_prc": "71900", "trde_qty": "9999999"},
                    {"dt": "20260710", "open_pric": "71000", "high_pric": "72500",
                     "low_pric": "70900", "cur_prc": "72000", "trde_qty": "8888888"},
                    {},  # 키움도 빈 항목이 섞여 올 수 있음 → 필터링돼야 함
                ],
            },
        )
        resp = kiwoom.quotations().inquire_daily_itemchartprice(
            InquireDailyItemChartPriceInBlock(stk_cd="005930", base_dt="20260711")
        ).req()

        assert resp.error_msg is None
        assert len(resp.blocks) == 2  # 빈 캔들 제외
        assert resp.blocks[0].dt == "20260711"
        assert resp.blocks[0].cur_prc == "71900"

        req = requests_mock.last_request
        assert req.headers["api-id"] == "ka10081"
        body = req.json()
        assert body["stk_cd"] == "005930"
        assert body["base_dt"] == "20260711"


class TestKoreanAliases:
    """한글 별칭이 영문 메서드와 동일하게 동작하는지 확인합니다."""

    def test_korean_aliases_behave_same_as_english(self, kiwoom, requests_mock):
        requests_mock.post(
            f"{URLS.MOCK_URL}{URLS.STKINFO_PATH}",
            json={"return_code": 0, "stk_cd": "005930", "cur_prc": "71900"},
        )

        q_en = kiwoom.quotations()
        q_ko = kiwoom.시세()

        resp_en = q_en.inquire_price(InquirePriceInBlock(stk_cd="005930")).req()
        resp_ko = q_ko.현재가(InquirePriceInBlock(stk_cd="005930")).req()

        assert resp_en.block.cur_prc == resp_ko.block.cur_prc == "71900"
        assert q_en.호가 is not None
        assert q_en.일봉 is not None
        assert kiwoom.계좌 is not None
        assert kiwoom.주문 is not None
        assert kiwoom.로그인 is not None
        assert kiwoom.실시간 is not None
