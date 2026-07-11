"""KIS 시세 TR(현재가/호가/일봉) 테스트 (requests_mock 기반, 실제 API 호출 없음)."""

import pytest

from programgarden_finance import Kis
from programgarden_finance.kis.config import URLS
from programgarden_finance.kis.quotations.inquire_price import InquirePriceInBlock
from programgarden_finance.kis.quotations.inquire_asking_price import InquireAskingPriceInBlock
from programgarden_finance.kis.quotations.inquire_daily_itemchartprice import (
    InquireDailyItemChartPriceInBlock,
)

TOKEN_URL = f"{URLS.PAPER_URL}{URLS.TOKEN_PATH}"


@pytest.fixture
def kis(requests_mock) -> Kis:
    requests_mock.post(TOKEN_URL, json={"access_token": "tok", "expires_in": 86400})
    client = Kis(paper_trading=True, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


class TestInquirePriceMock:
    def test_success(self, kis, requests_mock):
        requests_mock.get(
            f"{URLS.PAPER_URL}{URLS.INQUIRE_PRICE_PATH}",
            json={
                "rt_cd": "0", "msg_cd": "MCA00000", "msg1": "정상처리 되었습니다.",
                "output": {
                    "stck_prpr": "71900", "prdy_vrss": "-100", "prdy_ctrt": "-0.14",
                    "stck_oprc": "72000", "stck_hgpr": "72100", "stck_lwpr": "71500",
                    "acml_vol": "9999999", "per": "12.34", "pbr": "1.23",
                    "hts_kor_isnm": "삼성전자",
                },
            },
        )
        resp = kis.quotations().inquire_price(
            InquirePriceInBlock(fid_input_iscd="005930")
        ).req()

        assert resp.error_msg is None
        assert resp.rt_cd == "0"
        assert resp.block.stck_prpr == "71900"
        assert resp.block.hts_kor_isnm == "삼성전자"

        # 헤더 검증
        req = requests_mock.last_request
        assert req.headers["tr_id"] == "FHKST01010100"
        assert req.headers["authorization"] == "Bearer tok"
        assert req.headers["appkey"] == "ak"
        assert req.headers["custtype"] == "P"
        # 쿼리 파라미터 대문자 alias 검증
        assert req.qs["fid_input_iscd"] == ["005930"]
        assert req.qs["fid_cond_mrkt_div_code"] == ["j"]  # requests_mock은 qs를 소문자로 정규화

    def test_kis_error_rt_cd(self, kis, requests_mock):
        requests_mock.get(
            f"{URLS.PAPER_URL}{URLS.INQUIRE_PRICE_PATH}",
            json={"rt_cd": "1", "msg_cd": "EGW00121", "msg1": "유효하지 않은 종목"},
        )
        resp = kis.quotations().inquire_price(
            InquirePriceInBlock(fid_input_iscd="999999")
        ).req()
        assert resp.error_msg is not None
        assert resp.rt_cd == "1"
        assert resp.block is None


class TestInquireAskingPriceMock:
    def test_success(self, kis, requests_mock):
        requests_mock.get(
            f"{URLS.PAPER_URL}{URLS.INQUIRE_ASKING_PRICE_PATH}",
            json={
                "rt_cd": "0", "msg_cd": "MCA00000", "msg1": "OK",
                "output1": {
                    "askp1": "72000", "bidp1": "71900",
                    "askp_rsqn1": "1000", "bidp_rsqn1": "2000",
                    "total_askp_rsqn": "50000", "total_bidp_rsqn": "60000",
                },
                "output2": {"antc_cnpr": "71950", "stck_prpr": "71900"},
            },
        )
        resp = kis.quotations().inquire_asking_price(
            InquireAskingPriceInBlock(fid_input_iscd="005930")
        ).req()

        assert resp.error_msg is None
        assert resp.block1.askp1 == "72000"
        assert resp.block1.bidp1 == "71900"
        assert resp.block2.antc_cnpr == "71950"
        assert requests_mock.last_request.headers["tr_id"] == "FHKST01010200"


class TestInquireDailyItemChartPriceMock:
    def test_success_filters_empty_candles(self, kis, requests_mock):
        requests_mock.get(
            f"{URLS.PAPER_URL}{URLS.INQUIRE_DAILY_ITEMCHARTPRICE_PATH}",
            json={
                "rt_cd": "0", "msg_cd": "MCA00000", "msg1": "OK",
                "output1": {"stck_prpr": "71900", "hts_kor_isnm": "삼성전자"},
                "output2": [
                    {"stck_bsop_date": "20260711", "stck_oprc": "72000",
                     "stck_hgpr": "72100", "stck_lwpr": "71500",
                     "stck_clpr": "71900", "acml_vol": "9999999"},
                    {"stck_bsop_date": "20260710", "stck_oprc": "71000",
                     "stck_hgpr": "72500", "stck_lwpr": "70900",
                     "stck_clpr": "72000", "acml_vol": "8888888"},
                    {},  # KIS는 빈 항목을 섞어 보낼 수 있음 → 필터링돼야 함
                ],
            },
        )
        resp = kis.quotations().inquire_daily_itemchartprice(
            InquireDailyItemChartPriceInBlock(
                fid_input_iscd="005930",
                fid_input_date_1="20260601",
                fid_input_date_2="20260711",
            )
        ).req()

        assert resp.error_msg is None
        assert len(resp.blocks) == 2  # 빈 캔들 제외
        assert resp.blocks[0].stck_bsop_date == "20260711"
        assert resp.blocks[0].stck_clpr == "71900"

        req = requests_mock.last_request
        assert req.headers["tr_id"] == "FHKST03010100"
        assert req.qs["fid_period_div_code"] == ["d"]


class TestKoreanAliases:
    def test_korean_aliases_exist(self, kis):
        q = kis.quotations()
        assert q.현재가 is not None
        assert q.호가 is not None
        assert q.일봉 is not None
        assert kis.시세 is not None
        assert kis.계좌 is not None
        assert kis.주문 is not None
        assert kis.로그인 is not None
