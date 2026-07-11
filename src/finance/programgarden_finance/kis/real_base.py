"""한국투자증권(KIS) 실시간 WebSocket 기반 클래스입니다.

빗썸 ``BithumbRealBase``의 생명주기(connect/close, ref-count, 재연결 + 자동
재구독)를 따르되 KIS 프로토콜 특성을 반영합니다:

- 접속에 ``approval_key`` 필요 (``/oauth2/Approval`` 발급, TokenManager가 관리)
- 구독 프레임: ``{"header": {approval_key, custtype, tr_type, content-type},
  "body": {"input": {"tr_id", "tr_key"}}}`` (tr_type "1"=등록, "2"=해제)
- 데이터 프레임은 JSON이 아닌 **파이프 구분 텍스트**:
  ``암호화플래그|tr_id|건수|필드1^필드2^…`` (첫 문자 '0'=평문, '1'=AES 암호문)
- 체결통보(H0STCNI0/H0STCNI9)는 AES-256-CBC 암호화 — 구독 응답의
  ``body.output.iv/key`` 로 복호화 (pycryptodome)
- ``PINGPONG`` 제어 프레임은 수신 즉시 그대로 에코해야 연결이 유지됨
"""

import asyncio
import base64
import importlib
import inspect
import json
import logging
import random
import time
from typing import Any, Callable, Dict, List, Optional, Tuple

from websockets import connect
from websockets.exceptions import WebSocketException

_logger = logging.getLogger("programgarden_finance.kis.real")

DEFAULT_MAX_SUBSCRIBE_KEYS = 40  # KIS 세션당 등록 가능 건수(41건) 이내 보수적 기본값

# tr_id -> parsed response model class (lazy-loaded, None = import failed)
_MODEL_CACHE: Dict[str, Optional[type]] = {}

_TR_MODEL_MAP: Dict[str, tuple] = {
    "H0STCNT0": (
        "programgarden_finance.kis.real.ccnl.blocks",
        "CcnlRealResponse",
    ),
    "H0STCNI0": (
        "programgarden_finance.kis.real.order_notice.blocks",
        "OrderNoticeRealResponse",
    ),
    "H0STCNI9": (
        "programgarden_finance.kis.real.order_notice.blocks",
        "OrderNoticeRealResponse",
    ),
}


def _get_response_model(tr_id: str) -> Optional[type]:
    """tr_id에 해당하는 응답 모델 클래스를 반환합니다 (lazy import)."""
    if tr_id in _MODEL_CACHE:
        return _MODEL_CACHE[tr_id]
    if tr_id not in _TR_MODEL_MAP:
        _MODEL_CACHE[tr_id] = None
        return None
    mod_path, cls_name = _TR_MODEL_MAP[tr_id]
    try:
        m = importlib.import_module(mod_path)
        _MODEL_CACHE[tr_id] = getattr(m, cls_name)
    except Exception:
        _MODEL_CACHE[tr_id] = None
    return _MODEL_CACHE[tr_id]


def decrypt_notice(cipher_b64: str, key: str, iv: str) -> str:
    """AES-256-CBC로 암호화된 체결통보 페이로드를 복호화합니다.

    KIS는 구독 응답(body.output)으로 key(32바이트)/iv(16바이트) 문자열을 내려주며,
    데이터는 base64(AES-CBC(평문)) 형태입니다.
    """
    from Crypto.Cipher import AES  # pycryptodome (지연 임포트)

    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    decrypted = cipher.decrypt(base64.b64decode(cipher_b64))
    # PKCS7 언패딩
    pad_len = decrypted[-1]
    if 1 <= pad_len <= AES.block_size:
        decrypted = decrypted[:-pad_len]
    return decrypted.decode("utf-8")


def parse_pipe_frame(raw: str) -> Optional[Tuple[str, str, int, str]]:
    """파이프 구분 데이터 프레임을 ``(암호화플래그, tr_id, 건수, 페이로드)``로 분해합니다.

    형식이 아니면 None을 반환합니다.
    """
    parts = raw.split("|", 3)
    if len(parts) != 4:
        return None
    flag, tr_id, count_str, payload = parts
    if flag not in ("0", "1"):
        return None
    try:
        count = int(count_str)
    except ValueError:
        return None
    return flag, tr_id, max(1, count), payload


def split_records(payload: str, count: int) -> List[List[str]]:
    """``^`` 구분 페이로드를 건수만큼의 레코드로 분할합니다.

    KIS는 여러 건을 한 프레임에 이어붙여 보냅니다. 전체 필드 수를 건수로
    나눠 레코드당 필드 수를 계산합니다.
    """
    fields = payload.split("^")
    if count <= 1:
        return [fields]
    per_record = len(fields) // count
    if per_record <= 0:
        return [fields]
    return [fields[i * per_record:(i + 1) * per_record] for i in range(count)]


class KisSubscriptionLimitExceeded(RuntimeError):
    """세션당 실시간 구독 건수가 상한을 초과할 때 발생합니다."""


class KisRealBase:
    """KIS 실시간 WebSocket 재연결 지원 기반 클래스.

    ``approval_key`` 인증으로 접속하며 tr_id + tr_key 단위로 구독합니다.
    재연결 시 자동으로 이전 구독을 복원하고, PINGPONG을 에코하며,
    체결통보 암호문은 key/iv 수신 전이면 버퍼링합니다.
    """

    def __init__(
        self,
        token_manager,
        reconnect: bool = True,
        max_backoff: float = 60.0,
        max_subscribe_keys: int = DEFAULT_MAX_SUBSCRIBE_KEYS,
    ):
        self._token_manager = token_manager
        self._reconnect = reconnect
        self._max_backoff = max_backoff
        self._max_subscribe_keys = max_subscribe_keys

        self._connected_event = asyncio.Event()
        self._ws = None
        self._listen_task: Optional[asyncio.Task] = None
        self._stop = False

        self._ref_count = 0
        self._ref_lock = asyncio.Lock()

        # tr_id → listener
        self._on_message_listeners: Dict[str, Callable[[Any], Any]] = {}
        # tr_id → [tr_key] (재연결 시 자동 재구독용)
        self._subscribed_keys: Dict[str, List[str]] = {}
        self._last_message_time: float = 0.0

        # 체결통보 AES key/iv (구독 응답으로 수신)
        self._aes_key: Optional[str] = None
        self._aes_iv: Optional[str] = None
        # key/iv 수신 전 도착한 암호 프레임 버퍼 (레이스 대비)
        self._encrypted_buffer: List[str] = []
        self._encrypted_buffer_max = 32

    # ──────────────────────────────────────────── 상태 조회 ──

    @property
    def ws_url(self) -> str:
        return self._token_manager.ws_url

    async def is_connected(self) -> bool:
        return self._connected_event.is_set()

    def get_subscribed_keys(self) -> Dict[str, List[str]]:
        """현재 구독 중인 키 목록 (tr_id → tr_keys)."""
        return {k: list(v) for k, v in self._subscribed_keys.items()}

    def get_subscription_count(self) -> int:
        """전체 구독 건수 (tr_id × tr_key 조합 수)."""
        return sum(len(v) for v in self._subscribed_keys.values())

    def get_subscription_capacity(self) -> Optional[int]:
        """남은 구독 여유분. cap 비활성(``max_subscribe_keys <= 0``) 시 ``None``."""
        if self._max_subscribe_keys <= 0:
            return None
        return max(0, self._max_subscribe_keys - self.get_subscription_count())

    def get_staleness_sec(self) -> float:
        if self._last_message_time <= 0:
            return 0.0
        return time.time() - self._last_message_time

    # ─────────────────────────────────────────── 프레임 구성 ──

    def _build_subscribe_frame(self, tr_id: str, tr_key: str, register: bool) -> str:
        return json.dumps({
            "header": {
                "approval_key": self._token_manager.get_approval_key(),
                "custtype": "P",
                "tr_type": "1" if register else "2",
                "content-type": "utf-8",
            },
            "body": {
                "input": {
                    "tr_id": tr_id,
                    "tr_key": tr_key,
                }
            },
        })

    # ─────────────────────────────────────────── connect/close ──

    async def connect(self, wait: bool = True, timeout: float = 5.0):
        """WebSocket을 열고 리스너 루프를 시작합니다.

        이미 연결된 경우 참조 카운트만 증가시키고 즉시 반환합니다(싱글톤 안전).
        """
        need_connect = False
        async with self._ref_lock:
            self._ref_count += 1
            if self._connected_event.is_set():
                return
            if self._listen_task is not None and not self._listen_task.done():
                need_connect = False
            else:
                self._stop = False
                need_connect = True

        if not need_connect:
            if wait:
                try:
                    await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
                except asyncio.TimeoutError:
                    raise RuntimeError("KIS WebSocket 연결 대기 시간 초과")
            return

        async def _connection_loop():
            backoff = 1.0
            while not self._stop:
                try:
                    async with connect(
                        uri=self.ws_url,
                        ping_interval=None,
                        ping_timeout=None,
                    ) as ws:
                        self._ws = ws
                        try:
                            self._connected_event.set()
                        except Exception:
                            pass

                        # 재연결 후 이전 구독 자동 복원
                        if backoff > 1.0 and self._subscribed_keys:
                            for tr_id, keys in list(self._subscribed_keys.items()):
                                for tr_key in keys:
                                    try:
                                        await ws.send(
                                            self._build_subscribe_frame(tr_id, tr_key, register=True)
                                        )
                                    except Exception as exc:
                                        _logger.error(
                                            "KIS 재구독 실패 (%s/%s): %s", tr_id, tr_key, exc
                                        )
                            _logger.info(
                                "KIS WebSocket 재연결 후 자동 재구독: %d건",
                                self.get_subscription_count(),
                            )

                        backoff = 1.0
                        self._last_message_time = time.time()
                        _staleness_warned = False

                        while not self._stop:
                            try:
                                raw = await ws.recv()
                            except asyncio.CancelledError:
                                raise
                            except (WebSocketException, ConnectionError):
                                break
                            except Exception:
                                staleness = self.get_staleness_sec()
                                if staleness > 120 and not _staleness_warned:
                                    _staleness_warned = True
                                    _logger.warning(
                                        "KIS WebSocket 무 데이터 경고: "
                                        "%.0f초 동안 메시지 수신 없음.", staleness
                                    )
                                continue

                            self._last_message_time = time.time()
                            _staleness_warned = False

                            if isinstance(raw, bytes):
                                try:
                                    raw = raw.decode("utf-8")
                                except Exception:
                                    continue

                            await self._dispatch(raw)

                except asyncio.CancelledError:
                    break
                except Exception:
                    if not self._reconnect:
                        break

                if not self._reconnect or self._stop:
                    break

                _logger.warning(
                    "KIS WebSocket 연결 끊김 — 재연결 시도 중 (backoff=%.1fs). "
                    "이 기간 동안 시세 데이터가 누락될 수 있습니다.", backoff
                )
                jitter = random.uniform(0, backoff * 0.1)
                await asyncio.sleep(backoff + jitter)
                backoff = min(self._max_backoff, backoff * 2)
                try:
                    self._connected_event.clear()
                except Exception:
                    pass

        self._listen_task = asyncio.create_task(_connection_loop())
        if wait:
            try:
                await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                raise RuntimeError("KIS WebSocket 연결 대기 시간 초과")
        else:
            await asyncio.sleep(0)

    async def close(self, force: bool = False):
        """WebSocket 연결을 닫습니다 (ref-count 기반, ``force=True`` 즉시 종료)."""
        async with self._ref_lock:
            if not force:
                self._ref_count = max(0, self._ref_count - 1)
                if self._ref_count > 0:
                    return
            elif self._ref_count > 1:
                _logger.warning(
                    "KIS WebSocket force close: ref_count=%d. "
                    "다른 %d개 구독이 끊어집니다.",
                    self._ref_count,
                    self._ref_count - 1,
                )
            self._ref_count = 0

        self._stop = True
        if self._listen_task is not None:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._ws is not None:
            try:
                await self._ws.close()
            except Exception:
                pass

        self._connected_event.clear()
        self._cleanup_singleton_cache()

    def _cleanup_singleton_cache(self) -> None:
        """``Kis._real_instances`` 싱글톤 캐시에서 이 인스턴스를 제거합니다."""
        try:
            from programgarden_finance.kis.client import Kis
            for key, inst in list(Kis._real_instances.items()):
                if inst is self:
                    del Kis._real_instances[key]
                    break
        except Exception:
            pass

    # ──────────────────────────────────────────── 디스패치 ──

    async def _dispatch(self, raw: str) -> None:
        """수신 프레임을 데이터/제어로 분류해 처리합니다."""
        if not raw:
            return

        # 데이터 프레임: '0'(평문) 또는 '1'(암호문)로 시작하는 파이프 구분 텍스트
        if raw[0] in ("0", "1"):
            parsed = parse_pipe_frame(raw)
            if parsed is None:
                return
            flag, tr_id, count, payload = parsed

            if flag == "1":
                if not self._aes_key or not self._aes_iv:
                    # key/iv 수신 전 도착한 암호 프레임 — 버퍼링 (레이스 대비)
                    if len(self._encrypted_buffer) < self._encrypted_buffer_max:
                        self._encrypted_buffer.append(raw)
                    else:
                        _logger.warning("KIS 암호 프레임 버퍼 초과 — 프레임 폐기 (key/iv 미수신)")
                    return
                try:
                    payload = decrypt_notice(payload, self._aes_key, self._aes_iv)
                except Exception as exc:
                    _logger.error("KIS 체결통보 복호화 실패: %s", exc)
                    return

            self._handle_data(tr_id, count, payload)
            return

        # 제어 프레임: JSON
        try:
            msg = json.loads(raw)
        except Exception:
            return

        header = msg.get("header") or {}
        tr_id = header.get("tr_id")

        # PINGPONG은 수신한 원문 그대로 에코해야 연결이 유지됨
        if tr_id == "PINGPONG":
            try:
                await self._ws.send(raw)
            except Exception:
                pass
            return

        body = msg.get("body") or {}
        output = body.get("output") or {}

        # 체결통보 구독 응답: AES key/iv 저장 후 버퍼된 암호 프레임 처리
        if output.get("iv") and output.get("key"):
            self._aes_iv = output["iv"]
            self._aes_key = output["key"]
            _logger.info("KIS 체결통보 AES key/iv 수신 완료")
            buffered, self._encrypted_buffer = self._encrypted_buffer, []
            for frame in buffered:
                await self._dispatch(frame)
            return

        rt_cd = body.get("rt_cd")
        if rt_cd is not None and rt_cd != "0":
            _logger.warning(
                "KIS WebSocket 구독 오류 (%s): %s", tr_id, body.get("msg1")
            )

    def _handle_data(self, tr_id: str, count: int, payload: str) -> None:
        """평문 데이터 페이로드를 레코드로 분할해 리스너에 전달합니다."""
        listener = self._on_message_listeners.get(tr_id)
        if listener is None:
            return

        model_cls = _get_response_model(tr_id)

        for fields in split_records(payload, count):
            if model_cls is not None:
                try:
                    resp = model_cls.from_pipe_fields(tr_id, fields)
                except Exception as exc:
                    _logger.debug("KIS 실시간 필드 파싱 실패 (%s): %s", tr_id, exc)
                    continue
            else:
                resp = fields

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                listener(resp)
                continue

            if inspect.iscoroutinefunction(listener):
                try:
                    task = asyncio.create_task(listener(resp))

                    def _on_done(t: asyncio.Task) -> None:
                        try:
                            t.exception()
                        except asyncio.CancelledError:
                            pass

                    task.add_done_callback(_on_done)
                except Exception:
                    continue
            else:
                try:
                    loop.run_in_executor(None, listener, resp)
                except Exception:
                    continue

    # ──────────────────────────────────────── 리스너 등록/해제 ──

    def _on_message(self, tr_id: str, listener: Callable[[Any], Any]) -> None:
        """특정 tr_id의 메시지 콜백을 등록합니다 (sync/async 모두 허용)."""
        if not self._connected_event.is_set():
            raise RuntimeError("KIS WebSocket이 연결되지 않았습니다")
        self._on_message_listeners[tr_id] = listener

    def _on_remove_message(self, tr_id: str) -> None:
        """등록된 리스너를 해제합니다."""
        if not self._connected_event.is_set():
            raise RuntimeError("KIS WebSocket이 연결되지 않았습니다")
        self._on_message_listeners.pop(tr_id, None)

    # ──────────────────────────────────────── 구독 추가/제거 ──

    def _add_keys(self, tr_keys: List[str], tr_id: str) -> None:
        """``tr_id`` 구독에 ``tr_keys``를 추가합니다 (키별 개별 구독 프레임 전송)."""
        if not self._connected_event.is_set() or self._ws is None:
            raise RuntimeError("KIS WebSocket이 연결되지 않았습니다")

        existing = self._subscribed_keys.get(tr_id, [])
        new_unique = [k for k in dict.fromkeys(tr_keys) if k not in existing]

        if self._max_subscribe_keys > 0:
            projected = self.get_subscription_count() + len(new_unique)
            if projected > self._max_subscribe_keys:
                raise KisSubscriptionLimitExceeded(
                    f"KIS 실시간 구독 건수가 상한({self._max_subscribe_keys})을 초과합니다: "
                    f"현재 {self.get_subscription_count()}건 + 신규 {len(new_unique)}건 "
                    f"= {projected}건 요청 (tr_id={tr_id}). "
                    f"max_subscribe_keys 를 조정하거나 구독 수를 줄이세요."
                )

        if tr_id not in self._subscribed_keys:
            self._subscribed_keys[tr_id] = []

        for tr_key in new_unique:
            self._subscribed_keys[tr_id].append(tr_key)
            asyncio.create_task(
                self._ws.send(self._build_subscribe_frame(tr_id, tr_key, register=True))
            )

    def _remove_keys(self, tr_keys: List[str], tr_id: str) -> None:
        """``tr_id`` 구독에서 ``tr_keys``를 제거합니다 (키별 해제 프레임 전송)."""
        if not self._connected_event.is_set() or self._ws is None:
            raise RuntimeError("KIS WebSocket이 연결되지 않았습니다")

        for tr_key in tr_keys:
            if tr_id in self._subscribed_keys:
                try:
                    self._subscribed_keys[tr_id].remove(tr_key)
                except ValueError:
                    continue
                asyncio.create_task(
                    self._ws.send(self._build_subscribe_frame(tr_id, tr_key, register=False))
                )

        if tr_id in self._subscribed_keys and not self._subscribed_keys[tr_id]:
            del self._subscribed_keys[tr_id]
