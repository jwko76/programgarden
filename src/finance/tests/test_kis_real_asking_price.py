"""KIS 실시간 호가(H0STASP0) 테스트.

test_kis_real.py의 CCNL 파싱 패턴을 따릅니다: 파이프 프레임 파싱 →
필드 매핑 → RealAskingPrice 클라이언트의 구독 헬퍼.
"""

from unittest.mock import MagicMock

from programgarden_finance.kis.real_base import KisRealBase, _get_response_model
from programgarden_finance.kis.real.asking_price.blocks import AskingPriceRealResponse
from programgarden_finance.kis.real.asking_price.client import RealAskingPrice
from programgarden_finance.kis.config import TR_IDS

# 0: 종목코드, 1: 시간, 2: 시간구분, 3~12: 매도호가1~10, 13~22: 매수호가1~10,
# 23~32: 매도잔량1~10, 33~42: 매수잔량1~10, 43: 총매도잔량, 44: 총매수잔량,
# 47: 예상체결가, 48: 예상체결량
ASKING_PAYLOAD_FIELDS = [str(i) for i in range(50)]
ASKING_PAYLOAD_FIELDS[0] = "005930"
ASKING_PAYLOAD = "^".join(ASKING_PAYLOAD_FIELDS)


def _make_token_manager(paper: bool = True) -> MagicMock:
    tm = MagicMock()
    tm.paper_trading = paper
    tm.ws_url = "ws://ops.koreainvestment.com:31000"
    tm.get_approval_key.return_value = "test-approval-key"
    return tm


class TestGetResponseModelAskingPrice:
    def test_asking_price_model_registered(self):
        assert _get_response_model("H0STASP0") is AskingPriceRealResponse


class TestAskingPriceParsing:
    def test_from_pipe_fields(self):
        resp = AskingPriceRealResponse.from_pipe_fields("H0STASP0", ASKING_PAYLOAD.split("^"))
        assert resp.mksc_shrn_iscd == "005930"
        assert resp.askp1 == "3"
        assert resp.bidp1 == "13"
        assert resp.askp_rsqn1 == "23"
        assert resp.bidp_rsqn1 == "33"
        assert resp.total_askp_rsqn == "43"
        assert resp.total_bidp_rsqn == "44"
        assert resp.antc_cnpr == "47"
        assert resp.raw_fields[0] == "005930"

    def test_short_payload_leaves_missing_fields_none(self):
        resp = AskingPriceRealResponse.from_pipe_fields("H0STASP0", ["005930", "093000"])
        assert resp.mksc_shrn_iscd == "005930"
        assert resp.bsop_hour == "093000"
        assert resp.askp1 is None
        assert resp.total_askp_rsqn is None


class TestRealAskingPriceClient:
    def test_add_asking_price_symbols_uses_correct_tr_id(self):
        base = MagicMock()
        client = RealAskingPrice(base)
        client.add_asking_price_symbols(["005930", "000660"])
        base._add_keys.assert_called_once_with(["005930", "000660"], TR_IDS.REAL_ASKING_PRICE)

    def test_remove_asking_price_symbols(self):
        base = MagicMock()
        client = RealAskingPrice(base)
        client.remove_asking_price_symbols(["005930"])
        base._remove_keys.assert_called_once_with(["005930"], TR_IDS.REAL_ASKING_PRICE)

    def test_on_asking_price_registers_listener(self):
        base = MagicMock()
        client = RealAskingPrice(base)
        listener = lambda r: None
        client.on_asking_price(listener)
        base._on_message.assert_called_once_with(TR_IDS.REAL_ASKING_PRICE, listener)

    def test_korean_aliases_exist(self):
        base = MagicMock()
        client = RealAskingPrice(base)
        assert client.호가등록 is not None
        assert client.호가해제 is not None
        assert client.호가수신 is not None
        assert client.호가수신해제 is not None


class TestKisRealExposesAskingPrice:
    def test_real_client_has_asking_price_method(self):
        from programgarden_finance import KisReal

        real = KisReal(token_manager=_make_token_manager())
        real._connected_event.set()  # asking_price()는 연결 상태를 요구하지 않지만 일관성 위해
        asking = real.asking_price()
        assert isinstance(asking, RealAskingPrice)
        assert real.호가 is not None
