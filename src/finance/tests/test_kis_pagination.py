"""KIS 잔고조회 tr_cont 연속조회(페이지네이션) 테스트 (requests_mock 기반).

핵심 검증: 응답 헤더 tr_cont가 F/M(다음 페이지 있음)이면 ctx_area_fk100/
nk100을 다음 요청에 반영해 자동으로 페이지를 이어 붙인다. D/E(마지막)면
1회 요청으로 끝나야 한다.
"""

from programgarden_finance import Kis
from programgarden_finance.kis.config import URLS

TOKEN_URL = f"{URLS.PAPER_URL}{URLS.TOKEN_PATH}"
BALANCE_URL = f"{URLS.PAPER_URL}{URLS.INQUIRE_BALANCE_PATH}"


def _login(requests_mock) -> Kis:
    requests_mock.post(TOKEN_URL, json={"access_token": "tok", "expires_in": 86400})
    client = Kis(paper_trading=True, use_token_file_cache=False)
    client.login(appkey="ak", appsecretkey="sk", account_no="12345678")
    return client


def _page(symbols, tr_cont_next: bool, fk="", nk=""):
    return {
        "rt_cd": "0", "msg_cd": "MCA00000", "msg1": "OK",
        "output1": [
            {"pdno": s, "prdt_name": f"종목{s}", "hldg_qty": "1", "ord_psbl_qty": "1",
             "pchs_avg_pric": "1000", "prpr": "1100", "evlu_amt": "1100",
             "evlu_pfls_amt": "100", "evlu_pfls_rt": "10.0"}
            for s in symbols
        ],
        "output2": [{"dnca_tot_amt": "5000000", "tot_evlu_amt": "1100"}],
        "ctx_area_fk100": "NEXTFK" if tr_cont_next else "",
        "ctx_area_nk100": "NEXTNK" if tr_cont_next else "",
    }


class TestSinglePage:
    def test_no_continuation_when_last_page(self, requests_mock):
        kis = _login(requests_mock)
        requests_mock.get(
            BALANCE_URL,
            json=_page(["005930"], tr_cont_next=False),
            headers={"tr_cont": "D"},
        )
        resp = kis.accno().inquire_balance().req_all()

        assert resp.error_msg is None
        assert len(resp.blocks) == 1
        assert len(requests_mock.request_history) == 2  # 토큰 1 + 잔고 1


class TestMultiPage:
    def test_merges_two_pages(self, requests_mock):
        kis = _login(requests_mock)
        requests_mock.get(
            BALANCE_URL,
            [
                {"json": _page(["005930"], tr_cont_next=True), "headers": {"tr_cont": "F"}},
                {"json": _page(["000660"], tr_cont_next=False), "headers": {"tr_cont": "D"}},
            ],
        )
        resp = kis.accno().inquire_balance().req_all()

        assert resp.error_msg is None
        assert [b.pdno for b in resp.blocks] == ["005930", "000660"]
        balance_calls = [r for r in requests_mock.request_history if URLS.INQUIRE_BALANCE_PATH in r.path]
        assert len(balance_calls) == 2
        # (req_all_async는 aiohttp 경로라 requests_mock으로 검증 불가 — 동기 경로로 로직 커버)
        # 두 번째 요청은 첫 응답의 연속조회 키를 그대로 사용해야 함
        assert balance_calls[1].qs["ctx_area_fk100"] == ["nextfk"]
        assert balance_calls[1].qs["ctx_area_nk100"] == ["nextnk"]
        assert balance_calls[1].headers["tr_cont"] == "N"
        # 계좌 요약은 마지막 페이지 기준
        assert resp.block2.dnca_tot_amt == "5000000"

    def test_max_pages_guard_stops_iteration(self, requests_mock):
        """tr_cont가 계속 F를 반환해도 max_pages 상한에서 멈춰야 한다 (무한루프 방지)."""
        kis = _login(requests_mock)
        requests_mock.get(
            BALANCE_URL,
            json=_page(["005930"], tr_cont_next=True),
            headers={"tr_cont": "F"},
        )
        resp = kis.accno().inquire_balance().req_all(max_pages=3)

        balance_calls = [r for r in requests_mock.request_history if URLS.INQUIRE_BALANCE_PATH in r.path]
        assert len(balance_calls) == 3
        assert len(resp.blocks) == 3  # 페이지마다 1건씩 누적
