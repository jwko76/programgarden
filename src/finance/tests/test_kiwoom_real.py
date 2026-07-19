"""키움증권 실시간 WebSocket(``kiwoom/real_base.py`` + ``kiwoom/real/``) 단위 테스트입니다.

실제 WebSocket 연결 없이 mock을 사용해 검증합니다:
- LOGIN 프레임 구성 (토큰 재사용, approval_key 없음)
- REG/REMOVE 구독/해제 프레임 형식
- JSON 데이터 프레임 파싱 및 type 기반 디스패치
- PING 에코
- 구독 cap 강제 및 재연결 후 재구독 목록 추적
"""

import asyncio
import json
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from programgarden_finance.kiwoom.real_base import (
    KiwoomRealBase,
    KiwoomSubscriptionLimitExceeded,
    _get_response_model,
)
from programgarden_finance.kiwoom.real.ccnl.blocks import CcnlRealResponse
from programgarden_finance.kiwoom.real.order_notice.blocks import OrderNoticeRealResponse


# ──────────────────────────── 헬퍼 ────────────────────────────


def _make_token_manager() -> MagicMock:
    tm = MagicMock()
    tm.ws_url = "wss://api.kiwoom.com:10000"
    tm.get_bearer_token.return_value = "Bearer test-access-token"
    return tm


def _make_connected_base(max_subscribe_keys: int = 5) -> KiwoomRealBase:
    base = KiwoomRealBase(token_manager=_make_token_manager(), max_subscribe_keys=max_subscribe_keys)
    base._connected_event.set()
    base._ws = AsyncMock()
    base._ws.send = AsyncMock()
    return base


def _run_dispatch(base: KiwoomRealBase, frames: List[str]) -> None:
    """비동기 _dispatch를 동기 테스트에서 실행합니다."""
    async def _run():
        for frame in frames:
            await base._dispatch(frame)
        await asyncio.sleep(0.05)  # run_in_executor 리스너 완료 대기

    asyncio.run(_run())


CCNL_DATA = {
    "item": "005930", "cur_prc": "71900", "pred_pre": "-100",
    "flu_rt": "-0.14", "cntr_qty": "15", "acc_trde_qty": "999999",
    "cntr_tm": "093354",
}

ORDER_NOTICE_DATA = {
    "acnt_no": "12345678", "ord_no": "0000117057", "stk_cd": "005930",
    "ord_qty": "10", "cntr_qty": "10", "cntr_uv": "60000", "ord_stt": "체결",
}


# ──────────────────────────── LOGIN 프레임 ────────────────────────────


class TestLoginFrame:
    def test_login_frame_shape(self):
        base = _make_connected_base()
        frame = json.loads(base._build_login_frame())
        assert frame == {"trnm": "LOGIN", "token": "test-access-token"}

    def test_login_frame_strips_bearer_prefix(self):
        base = _make_connected_base()
        # get_bearer_token()이 'Bearer <token>' 형식을 반환해도 LOGIN 프레임엔
        # 토큰 값만 담겨야 합니다.
        frame = json.loads(base._build_login_frame())
        assert "Bearer" not in frame["token"]


# ──────────────────────────── 구독 프레임 ────────────────────────────


class TestSubscribeFrame:
    def test_register_frame_shape(self):
        base = _make_connected_base()
        frame = json.loads(base._build_subscribe_frame("0B", "005930", register=True))
        assert frame["trnm"] == "REG"
        assert frame["grp_no"] == "1"
        assert frame["refresh"] == "1"
        assert frame["data"] == [{"item": ["005930"], "type": ["0B"]}]

    def test_unregister_frame_trnm(self):
        base = _make_connected_base()
        frame = json.loads(base._build_subscribe_frame("0B", "005930", register=False))
        assert frame["trnm"] == "REMOVE"


class TestGetResponseModel:
    def test_ccnl_model(self):
        assert _get_response_model("0B") is CcnlRealResponse

    def test_order_notice_model(self):
        assert _get_response_model("00") is OrderNoticeRealResponse

    def test_unknown_returns_none(self):
        assert _get_response_model("__unknown__") is None


# ──────────────────────────── 구독 관리 ────────────────────────────


class TestSubscriptionManagement:
    def test_add_keys_tracks_subscription(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "0B")
        assert base.get_subscribed_keys() == {"0B": ["005930", "000660"]}
        assert base.get_subscription_count() == 2

    def test_duplicate_keys_not_added(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_keys(["005930"], "0B")
            base._add_keys(["005930"], "0B")
        assert base.get_subscription_count() == 1

    def test_cap_enforced(self):
        base = _make_connected_base(max_subscribe_keys=2)
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "0B")
            with pytest.raises(KiwoomSubscriptionLimitExceeded):
                base._add_keys(["035720"], "0B")

    def test_remove_keys(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "0B")
            base._remove_keys(["005930"], "0B")
        assert base.get_subscribed_keys() == {"0B": ["000660"]}

    def test_not_connected_raises(self):
        base = KiwoomRealBase(token_manager=_make_token_manager())
        with pytest.raises(RuntimeError):
            base._add_keys(["005930"], "0B")

    def test_capacity_reflects_usage(self):
        base = _make_connected_base(max_subscribe_keys=5)
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "0B")
        assert base.get_subscription_capacity() == 3


# ──────────────────────────── 디스패치 ────────────────────────────


class TestDispatchLogin:
    def test_login_ack_sets_logged_in_event(self):
        base = _make_connected_base()
        ack = json.dumps({"trnm": "LOGIN", "return_code": 0, "return_msg": "정상"})
        _run_dispatch(base, [ack])
        assert base._logged_in_event.is_set()

    def test_login_ack_failure_does_not_raise(self):
        base = _make_connected_base()
        ack = json.dumps({"trnm": "LOGIN", "return_code": 9, "return_msg": "인증 실패"})
        _run_dispatch(base, [ack])  # 예외 없이 경고 로그만
        assert not base._logged_in_event.is_set()


class TestDispatchCcnl:
    def test_ccnl_frame_reaches_listener(self):
        base = _make_connected_base()
        received: List[CcnlRealResponse] = []
        base._on_message("0B", received.append)

        frame = json.dumps({"trnm": "REAL", "type": "0B", "data": [CCNL_DATA]})
        _run_dispatch(base, [frame])

        assert len(received) == 1
        assert received[0].cur_prc == "71900"
        assert received[0].item == "005930"

    def test_multi_record_frame(self):
        base = _make_connected_base()
        received: List[CcnlRealResponse] = []
        base._on_message("0B", received.append)

        frame = json.dumps({"trnm": "REAL", "type": "0B", "data": [CCNL_DATA, CCNL_DATA]})
        _run_dispatch(base, [frame])

        assert len(received) == 2

    def test_no_listener_no_error(self):
        base = _make_connected_base()
        frame = json.dumps({"trnm": "REAL", "type": "0B", "data": [CCNL_DATA]})
        _run_dispatch(base, [frame])  # 리스너 없음 — 예외 없이 무시

    def test_single_dict_data_not_list(self):
        """data가 리스트가 아닌 단일 dict로 오는 경우도 처리해야 합니다."""
        base = _make_connected_base()
        received: List[CcnlRealResponse] = []
        base._on_message("0B", received.append)

        frame = json.dumps({"trnm": "REAL", "type": "0B", "data": CCNL_DATA})
        _run_dispatch(base, [frame])

        assert len(received) == 1
        assert received[0].item == "005930"


class TestDispatchOrderNotice:
    def test_order_notice_frame_reaches_listener(self):
        base = _make_connected_base()
        received: List[OrderNoticeRealResponse] = []
        base._on_message("00", received.append)

        frame = json.dumps({"trnm": "REAL", "type": "00", "data": [ORDER_NOTICE_DATA]})
        _run_dispatch(base, [frame])

        assert len(received) == 1
        assert received[0].ord_no == "0000117057"
        assert received[0].stk_cd == "005930"
        assert received[0].ord_stt == "체결"


class TestPing:
    def test_ping_echoed_verbatim(self):
        base = _make_connected_base()
        raw = json.dumps({"trnm": "PING"})
        _run_dispatch(base, [raw])
        base._ws.send.assert_called_once_with(raw)


class TestSubscribeAckLogged:
    def test_reg_error_ack_does_not_raise(self):
        base = _make_connected_base()
        error_ack = json.dumps({"trnm": "REG", "return_code": 9, "return_msg": "REGISTER ERROR"})
        _run_dispatch(base, [error_ack])  # 예외 없이 경고 로그만

    def test_reg_success_ack_does_not_raise(self):
        base = _make_connected_base()
        ok_ack = json.dumps({"trnm": "REG", "return_code": 0, "return_msg": "OK"})
        _run_dispatch(base, [ok_ack])

    def test_non_json_frame_ignored(self):
        base = _make_connected_base()
        _run_dispatch(base, ["not-json-at-all"])  # 예외 없이 무시

    def test_unknown_shape_ignored(self):
        base = _make_connected_base()
        _run_dispatch(base, [json.dumps({"foo": "bar"})])  # trnm도 type도 없음 — 무시


# ──────────────────────────── 클라이언트 래퍼 ────────────────────────────


class TestRealClients:
    def test_ccnl_client_delegates(self):
        from programgarden_finance.kiwoom.real import KiwoomReal

        real = KiwoomReal(token_manager=_make_token_manager())
        real._connected_event.set()
        real._ws = AsyncMock()

        ccnl = real.ccnl()
        with patch("asyncio.create_task"):
            ccnl.add_ccnl_symbols(["005930"])
        assert real.get_subscribed_keys() == {"0B": ["005930"]}

    def test_order_notice_client_delegates(self):
        from programgarden_finance.kiwoom.real import KiwoomReal

        real = KiwoomReal(token_manager=_make_token_manager())
        real._connected_event.set()
        real._ws = AsyncMock()

        notice = real.order_notice()
        assert notice.type_code == "00"
        with patch("asyncio.create_task"):
            notice.subscribe("12345678")
        assert real.get_subscribed_keys() == {"00": ["12345678"]}

    def test_korean_aliases(self):
        from programgarden_finance.kiwoom.real import KiwoomReal

        real = KiwoomReal(token_manager=_make_token_manager())
        real._connected_event.set()
        real._ws = AsyncMock()

        assert real.체결가 is not None
        assert real.체결통보 is not None
