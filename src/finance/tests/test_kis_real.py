"""KIS 실시간 WebSocket(``kis/real_base.py`` + ``kis/real/``) 단위 테스트입니다.

실제 WebSocket 연결 없이 mock을 사용해 검증합니다:
- 파이프 구분 데이터 프레임 파싱 (H0STCNT0 체결가)
- 구독/해제 프레임 형식 (approval_key, tr_type)
- PINGPONG 에코
- AES-256-CBC 체결통보 복호화 (고정 key/iv 테스트 벡터)
- key/iv 수신 전 암호 프레임 버퍼링 (레이스 대비)
- 구독 cap 강제
"""

import asyncio
import base64
import json
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from programgarden_finance.kis.real_base import (
    KisRealBase,
    KisSubscriptionLimitExceeded,
    decrypt_notice,
    parse_pipe_frame,
    split_records,
    _get_response_model,
)
from programgarden_finance.kis.real.ccnl.blocks import CcnlRealResponse
from programgarden_finance.kis.real.order_notice.blocks import OrderNoticeRealResponse


# ──────────────────────────── 헬퍼 ────────────────────────────

AES_KEY = "0123456789abcdef0123456789abcdef"  # 32바이트
AES_IV = "abcdef0123456789"                   # 16바이트


def _encrypt(plaintext: str, key: str = AES_KEY, iv: str = AES_IV) -> str:
    """테스트용 AES-256-CBC + PKCS7 + base64 암호화 (KIS 서버 동작 재현)."""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad

    cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    return base64.b64encode(cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))).decode()


def _make_token_manager(paper: bool = True) -> MagicMock:
    tm = MagicMock()
    tm.paper_trading = paper
    tm.ws_url = "ws://ops.koreainvestment.com:31000"
    tm.get_approval_key.return_value = "test-approval-key"
    return tm


def _make_connected_base(max_subscribe_keys: int = 5) -> KisRealBase:
    base = KisRealBase(token_manager=_make_token_manager(), max_subscribe_keys=max_subscribe_keys)
    base._connected_event.set()
    base._ws = AsyncMock()
    base._ws.send = AsyncMock()
    return base


def _run_dispatch(base: KisRealBase, frames: List[str]) -> None:
    """비동기 _dispatch를 동기 테스트에서 실행합니다."""
    async def _run():
        for frame in frames:
            await base._dispatch(frame)
        await asyncio.sleep(0.05)  # run_in_executor 리스너 완료 대기

    asyncio.run(_run())


CCNL_PAYLOAD = "005930^093354^71900^5^-100^-0.14^71950.12^72000^72100^71500^72000^71900^15^999999^71999999999"


# ──────────────────────────── 프레임 파서 ────────────────────────────


class TestParsePipeFrame:
    def test_plain_data_frame(self):
        raw = f"0|H0STCNT0|001|{CCNL_PAYLOAD}"
        flag, tr_id, count, payload = parse_pipe_frame(raw)
        assert flag == "0"
        assert tr_id == "H0STCNT0"
        assert count == 1
        assert payload == CCNL_PAYLOAD

    def test_encrypted_flag(self):
        raw = "1|H0STCNI9|001|abc123=="
        flag, tr_id, count, payload = parse_pipe_frame(raw)
        assert flag == "1"
        assert tr_id == "H0STCNI9"

    def test_json_frame_returns_none(self):
        assert parse_pipe_frame('{"header": {"tr_id": "PINGPONG"}}') is None

    def test_malformed_returns_none(self):
        assert parse_pipe_frame("0|H0STCNT0") is None
        assert parse_pipe_frame("") is None

    def test_multi_record_split(self):
        fields_per_record = len(CCNL_PAYLOAD.split("^"))
        payload = "^".join([CCNL_PAYLOAD, CCNL_PAYLOAD])
        records = split_records(payload, 2)
        assert len(records) == 2
        assert all(len(r) == fields_per_record for r in records)
        assert records[0][0] == "005930"


class TestGetResponseModel:
    def test_ccnl_model(self):
        assert _get_response_model("H0STCNT0") is CcnlRealResponse

    def test_order_notice_models(self):
        assert _get_response_model("H0STCNI0") is OrderNoticeRealResponse
        assert _get_response_model("H0STCNI9") is OrderNoticeRealResponse

    def test_unknown_returns_none(self):
        assert _get_response_model("__unknown__") is None


class TestCcnlParsing:
    def test_from_pipe_fields(self):
        resp = CcnlRealResponse.from_pipe_fields("H0STCNT0", CCNL_PAYLOAD.split("^"))
        assert resp.mksc_shrn_iscd == "005930"
        assert resp.stck_cntg_hour == "093354"
        assert resp.stck_prpr == "71900"
        assert resp.prdy_vrss == "-100"
        assert resp.cntg_vol == "15"
        assert resp.raw_fields[0] == "005930"


# ──────────────────────────── 구독 프레임 ────────────────────────────


class TestSubscribeFrame:
    def test_register_frame_shape(self):
        base = _make_connected_base()
        frame = json.loads(base._build_subscribe_frame("H0STCNT0", "005930", register=True))
        assert frame["header"]["approval_key"] == "test-approval-key"
        assert frame["header"]["custtype"] == "P"
        assert frame["header"]["tr_type"] == "1"
        assert frame["header"]["content-type"] == "utf-8"
        assert frame["body"]["input"]["tr_id"] == "H0STCNT0"
        assert frame["body"]["input"]["tr_key"] == "005930"

    def test_unregister_frame_tr_type(self):
        base = _make_connected_base()
        frame = json.loads(base._build_subscribe_frame("H0STCNT0", "005930", register=False))
        assert frame["header"]["tr_type"] == "2"


class TestSubscriptionManagement:
    def test_add_keys_tracks_subscription(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "H0STCNT0")
        assert base.get_subscribed_keys() == {"H0STCNT0": ["005930", "000660"]}
        assert base.get_subscription_count() == 2

    def test_duplicate_keys_not_added(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_keys(["005930"], "H0STCNT0")
            base._add_keys(["005930"], "H0STCNT0")
        assert base.get_subscription_count() == 1

    def test_cap_enforced(self):
        base = _make_connected_base(max_subscribe_keys=2)
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "H0STCNT0")
            with pytest.raises(KisSubscriptionLimitExceeded):
                base._add_keys(["035720"], "H0STCNT0")

    def test_remove_keys(self):
        base = _make_connected_base()
        with patch("asyncio.create_task"):
            base._add_keys(["005930", "000660"], "H0STCNT0")
            base._remove_keys(["005930"], "H0STCNT0")
        assert base.get_subscribed_keys() == {"H0STCNT0": ["000660"]}

    def test_not_connected_raises(self):
        base = KisRealBase(token_manager=_make_token_manager())
        with pytest.raises(RuntimeError):
            base._add_keys(["005930"], "H0STCNT0")


# ──────────────────────────── 디스패치 ────────────────────────────


class TestDispatchCcnl:
    def test_plain_ccnl_frame_reaches_listener(self):
        base = _make_connected_base()
        received: List[CcnlRealResponse] = []
        base._on_message("H0STCNT0", received.append)

        _run_dispatch(base, [f"0|H0STCNT0|001|{CCNL_PAYLOAD}"])

        assert len(received) == 1
        assert received[0].stck_prpr == "71900"

    def test_multi_record_frame(self):
        base = _make_connected_base()
        received: List[CcnlRealResponse] = []
        base._on_message("H0STCNT0", received.append)

        payload = "^".join([CCNL_PAYLOAD, CCNL_PAYLOAD])
        _run_dispatch(base, [f"0|H0STCNT0|002|{payload}"])

        assert len(received) == 2

    def test_no_listener_no_error(self):
        base = _make_connected_base()
        _run_dispatch(base, [f"0|H0STCNT0|001|{CCNL_PAYLOAD}"])  # 리스너 없음 — 예외 없이 무시


class TestPingPong:
    def test_pingpong_echoed_verbatim(self):
        base = _make_connected_base()
        raw = '{"header":{"tr_id":"PINGPONG","datetime":"20260711120000"}}'
        _run_dispatch(base, [raw])
        base._ws.send.assert_called_once_with(raw)


class TestOrderNoticeAes:
    NOTICE_PLAINTEXT = (
        "myhtsid^12345678^0000117057^^02^0^00^0^005930^10^60000^121052^N^2^Y^00950^10^홍길동^삼성전자"
    )
    SUBSCRIBE_ACK = json.dumps({
        "header": {"tr_id": "H0STCNI9", "encrypt": "N"},
        "body": {
            "rt_cd": "0", "msg_cd": "OPSP0000", "msg1": "SUBSCRIBE SUCCESS",
            "output": {"iv": AES_IV, "key": AES_KEY},
        },
    })

    def test_decrypt_notice_roundtrip(self):
        cipher_b64 = _encrypt(self.NOTICE_PLAINTEXT)
        assert decrypt_notice(cipher_b64, AES_KEY, AES_IV) == self.NOTICE_PLAINTEXT

    def test_encrypted_notice_after_ack(self):
        base = _make_connected_base()
        received: List[OrderNoticeRealResponse] = []
        base._on_message("H0STCNI9", received.append)

        encrypted_frame = f"1|H0STCNI9|001|{_encrypt(self.NOTICE_PLAINTEXT)}"
        _run_dispatch(base, [self.SUBSCRIBE_ACK, encrypted_frame])

        assert len(received) == 1
        notice = received[0]
        assert notice.oder_no == "0000117057"
        assert notice.stck_shrn_iscd == "005930"
        assert notice.cntg_yn == "2"  # 체결
        assert notice.cntg_qty == "10"

    def test_encrypted_frame_before_ack_is_buffered(self):
        """key/iv 도착 전에 온 암호 프레임은 버퍼링됐다가 ack 수신 후 처리됩니다."""
        base = _make_connected_base()
        received: List[OrderNoticeRealResponse] = []
        base._on_message("H0STCNI9", received.append)

        encrypted_frame = f"1|H0STCNI9|001|{_encrypt(self.NOTICE_PLAINTEXT)}"
        # 암호 프레임이 ack보다 먼저 도착 (레이스)
        _run_dispatch(base, [encrypted_frame, self.SUBSCRIBE_ACK])

        assert len(received) == 1
        assert received[0].oder_no == "0000117057"

    def test_parse_order_notice_fields(self):
        resp = OrderNoticeRealResponse.from_pipe_fields(
            "H0STCNI9", self.NOTICE_PLAINTEXT.split("^")
        )
        assert resp.cust_id == "myhtsid"
        assert resp.acnt_no == "12345678"
        assert resp.seln_byov_cls == "02"  # 매수
        assert resp.cntg_unpr == "60000"


class TestSubscribeErrorLogged:
    def test_error_ack_does_not_raise(self):
        base = _make_connected_base()
        error_ack = json.dumps({
            "header": {"tr_id": "H0STCNT0"},
            "body": {"rt_cd": "9", "msg_cd": "OPSP8993", "msg1": "SUBSCRIBE ERROR"},
        })
        _run_dispatch(base, [error_ack])  # 예외 없이 경고 로그만


# ──────────────────────────── 클라이언트 래퍼 ────────────────────────────


class TestRealClients:
    def test_ccnl_client_delegates(self):
        from programgarden_finance.kis.real import KisReal

        real = KisReal(token_manager=_make_token_manager())
        real._connected_event.set()
        real._ws = AsyncMock()

        ccnl = real.ccnl()
        with patch("asyncio.create_task"):
            ccnl.add_ccnl_symbols(["005930"])
        assert real.get_subscribed_keys() == {"H0STCNT0": ["005930"]}

    @pytest.mark.parametrize("paper,expected", [(True, "H0STCNI9"), (False, "H0STCNI0")])
    def test_order_notice_tr_id_by_mode(self, paper, expected):
        from programgarden_finance.kis.real import KisReal

        real = KisReal(token_manager=_make_token_manager(paper=paper))
        notice = real.order_notice()
        assert notice.tr_id == expected
