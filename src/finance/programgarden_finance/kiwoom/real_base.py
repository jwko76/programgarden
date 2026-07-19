"""키움증권(Kiwoom Securities) 실시간 WebSocket 기반 클래스입니다.

KIS ``KisRealBase`` 의 생명주기(connect/close, ref-count, 재연결 + 자동
재구독) 구조를 따르되 키움 프로토콜 특성을 반영합니다:

- 접속 인증은 별도 approval_key 없이 REST 접근토큰을 그대로 사용합니다.
  접속 직후 ``{"trnm": "LOGIN", "token": "<접근토큰>"}`` 프레임을 전송합니다.
- 구독/해제는 KIS의 파이프 구분 텍스트가 아닌 JSON 메시지입니다:
  등록 ``{"trnm": "REG", "grp_no": ..., "refresh": "1", "data": [{"item": [...], "type": [...]}]}``
  / 해제는 동일 shape에 ``"trnm": "REMOVE"``.
  TODO(실계좌 검증): REG/REMOVE 정확한 필드 구조(grp_no 운용 방식, 여러
  종목을 한 프레임에 묶어 보내는 배치 방식 등) 확인. 현재는 KIS의
  키 단위 개별 구독 프레임 전송 방식을 그대로 따릅니다.
- 데이터 프레임도 JSON이며 ``type`` 필드로 스트림을 구분합니다
  (``"0B"``=주식체결, ``"00"``=주문체결통보). 파이프 프레임 파싱이나
  AES 복호화가 필요 없어 KIS보다 파싱 계층이 단순합니다.
- PING 프레임은 수신한 원문 그대로 에코해야 연결이 유지된다고 가정합니다
  (KIS의 PINGPONG 처리와 동일 패턴). TODO(실계좌 검증): 정확한 PING/PONG
  메시지 shape 확인.
"""

import asyncio
import importlib
import inspect
import json
import logging
import random
import time
from typing import Any, Callable, Dict, List, Optional

from websockets import connect
from websockets.exceptions import WebSocketException

_logger = logging.getLogger("programgarden_finance.kiwoom.real")

DEFAULT_MAX_SUBSCRIBE_KEYS = 40  # 세션당 등록 가능 건수 보수적 기본값 (KIS와 동일 기본치 적용)

# type -> parsed response model class (lazy-loaded, None = import failed)
_MODEL_CACHE: Dict[str, Optional[type]] = {}

_TYPE_MODEL_MAP: Dict[str, tuple] = {
    "0B": (
        "programgarden_finance.kiwoom.real.ccnl.blocks",
        "CcnlRealResponse",
    ),
    "00": (
        "programgarden_finance.kiwoom.real.order_notice.blocks",
        "OrderNoticeRealResponse",
    ),
}


def _get_response_model(type_code: str) -> Optional[type]:
    """type 코드에 해당하는 응답 모델 클래스를 반환합니다 (lazy import)."""
    if type_code in _MODEL_CACHE:
        return _MODEL_CACHE[type_code]
    if type_code not in _TYPE_MODEL_MAP:
        _MODEL_CACHE[type_code] = None
        return None
    mod_path, cls_name = _TYPE_MODEL_MAP[type_code]
    try:
        m = importlib.import_module(mod_path)
        _MODEL_CACHE[type_code] = getattr(m, cls_name)
    except Exception:
        _MODEL_CACHE[type_code] = None
    return _MODEL_CACHE[type_code]


class KiwoomSubscriptionLimitExceeded(RuntimeError):
    """세션당 실시간 구독 건수가 상한을 초과할 때 발생합니다."""


class KiwoomRealBase:
    """키움증권 실시간 WebSocket 재연결 지원 기반 클래스.

    REST 접근토큰으로 LOGIN 프레임 인증 후 ``type`` 단위로 구독합니다.
    재연결 시 자동으로 이전 구독을 복원하고, PING을 에코합니다.
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
        self._logged_in_event = asyncio.Event()
        self._ws = None
        self._listen_task: Optional[asyncio.Task] = None
        self._stop = False

        self._ref_count = 0
        self._ref_lock = asyncio.Lock()

        # type -> listener
        self._on_message_listeners: Dict[str, Callable[[Any], Any]] = {}
        # type -> [item] (재연결 시 자동 재구독용)
        self._subscribed_keys: Dict[str, List[str]] = {}
        self._last_message_time: float = 0.0

        # TODO(실계좌 검증): 그룹 번호 운용 방식(고정 vs 스트림별 분리) 확인
        self._grp_no = "1"

    # ──────────────────────────────────────────── 상태 조회 ──

    @property
    def ws_url(self) -> str:
        return self._token_manager.ws_url

    async def is_connected(self) -> bool:
        return self._connected_event.is_set()

    def get_subscribed_keys(self) -> Dict[str, List[str]]:
        """현재 구독 중인 키 목록 (type → item 목록)."""
        return {k: list(v) for k, v in self._subscribed_keys.items()}

    def get_subscription_count(self) -> int:
        """전체 구독 건수 (type × item 조합 수)."""
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

    def _build_login_frame(self) -> str:
        bearer = self._token_manager.get_bearer_token()
        token = bearer[len("Bearer "):] if bearer.startswith("Bearer ") else bearer
        return json.dumps({"trnm": "LOGIN", "token": token})

    def _build_subscribe_frame(self, type_code: str, item: str, register: bool) -> str:
        # TODO(실계좌 검증): 정확한 REG/REMOVE 메시지 필드 구조 확인
        return json.dumps({
            "trnm": "REG" if register else "REMOVE",
            "grp_no": self._grp_no,
            "refresh": "1",
            "data": [
                {"item": [item], "type": [type_code]},
            ],
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
                    raise RuntimeError("Kiwoom WebSocket 연결 대기 시간 초과")
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
                            await ws.send(self._build_login_frame())
                        except Exception as exc:
                            _logger.error("Kiwoom WebSocket LOGIN 프레임 전송 실패: %s", exc)

                        try:
                            self._connected_event.set()
                        except Exception:
                            pass

                        # 재연결 후 이전 구독 자동 복원
                        if backoff > 1.0 and self._subscribed_keys:
                            for type_code, items in list(self._subscribed_keys.items()):
                                for item in items:
                                    try:
                                        await ws.send(
                                            self._build_subscribe_frame(type_code, item, register=True)
                                        )
                                    except Exception as exc:
                                        _logger.error(
                                            "Kiwoom 재구독 실패 (%s/%s): %s", type_code, item, exc
                                        )
                            _logger.info(
                                "Kiwoom WebSocket 재연결 후 자동 재구독: %d건",
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
                                        "Kiwoom WebSocket 무 데이터 경고: "
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
                    "Kiwoom WebSocket 연결 끊김 — 재연결 시도 중 (backoff=%.1fs). "
                    "이 기간 동안 시세 데이터가 누락될 수 있습니다.", backoff
                )
                jitter = random.uniform(0, backoff * 0.1)
                await asyncio.sleep(backoff + jitter)
                backoff = min(self._max_backoff, backoff * 2)
                try:
                    self._connected_event.clear()
                    self._logged_in_event.clear()
                except Exception:
                    pass

        self._listen_task = asyncio.create_task(_connection_loop())
        if wait:
            try:
                await asyncio.wait_for(self._connected_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                raise RuntimeError("Kiwoom WebSocket 연결 대기 시간 초과")
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
                    "Kiwoom WebSocket force close: ref_count=%d. "
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
        self._logged_in_event.clear()
        self._cleanup_singleton_cache()

    def _cleanup_singleton_cache(self) -> None:
        """``Kiwoom._real_instances`` 싱글톤 캐시에서 이 인스턴스를 제거합니다."""
        try:
            from programgarden_finance.kiwoom.client import Kiwoom
            for key, inst in list(Kiwoom._real_instances.items()):
                if inst is self:
                    del Kiwoom._real_instances[key]
                    break
        except Exception:
            pass

    # ──────────────────────────────────────────── 디스패치 ──

    async def _dispatch(self, raw: str) -> None:
        """수신 프레임을 파싱해 제어/데이터 메시지로 분류 처리합니다."""
        if not raw:
            return

        try:
            msg = json.loads(raw)
        except Exception:
            _logger.debug("Kiwoom WebSocket 비-JSON 프레임 무시: %r", raw[:100])
            return

        trnm = msg.get("trnm")

        # PING은 수신한 원문 그대로 에코해야 연결이 유지된다고 가정합니다.
        # TODO(실계좌 검증): 정확한 PING/PONG 메시지 shape 확인.
        if trnm == "PING":
            try:
                await self._ws.send(raw)
            except Exception:
                pass
            return

        if trnm == "LOGIN":
            return_code = msg.get("return_code")
            if return_code not in (None, 0):
                _logger.warning("Kiwoom WebSocket LOGIN 실패: %s", msg.get("return_msg"))
            else:
                _logger.info("Kiwoom WebSocket LOGIN 완료 (raw=%r)", msg)
                self._logged_in_event.set()
            return

        if trnm in ("REG", "REMOVE"):
            return_code = msg.get("return_code")
            if return_code not in (None, 0):
                _logger.warning(
                    "Kiwoom WebSocket 구독 오류 (%s): %s", trnm, msg.get("return_msg")
                )
            return

        # 데이터 프레임: type 필드로 스트림 구분
        data = msg.get("data")
        type_code = msg.get("type")
        if data is None or type_code is None:
            _logger.debug("Kiwoom WebSocket 알 수 없는 프레임 형식: %r", msg)
            return

        self._handle_data(type_code, data)

    def _handle_data(self, type_code: str, data: Any) -> None:
        """JSON 데이터 페이로드를 레코드로 분할해 리스너에 전달합니다."""
        listener = self._on_message_listeners.get(type_code)
        if listener is None:
            return

        model_cls = _get_response_model(type_code)
        records = data if isinstance(data, list) else [data]

        for record in records:
            if not isinstance(record, dict):
                continue

            if model_cls is not None:
                try:
                    resp = model_cls.model_validate(record)
                except Exception as exc:
                    _logger.debug("Kiwoom 실시간 필드 파싱 실패 (%s): %s", type_code, exc)
                    continue
            else:
                resp = record

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

    def _on_message(self, type_code: str, listener: Callable[[Any], Any]) -> None:
        """특정 type의 메시지 콜백을 등록합니다 (sync/async 모두 허용)."""
        if not self._connected_event.is_set():
            raise RuntimeError("Kiwoom WebSocket이 연결되지 않았습니다")
        self._on_message_listeners[type_code] = listener

    def _on_remove_message(self, type_code: str) -> None:
        """등록된 리스너를 해제합니다."""
        if not self._connected_event.is_set():
            raise RuntimeError("Kiwoom WebSocket이 연결되지 않았습니다")
        self._on_message_listeners.pop(type_code, None)

    # ──────────────────────────────────────── 구독 추가/제거 ──

    def _add_keys(self, items: List[str], type_code: str) -> None:
        """``type_code`` 구독에 ``items``를 추가합니다 (항목별 개별 구독 프레임 전송)."""
        if not self._connected_event.is_set() or self._ws is None:
            raise RuntimeError("Kiwoom WebSocket이 연결되지 않았습니다")

        existing = self._subscribed_keys.get(type_code, [])
        new_unique = [k for k in dict.fromkeys(items) if k not in existing]

        if self._max_subscribe_keys > 0:
            projected = self.get_subscription_count() + len(new_unique)
            if projected > self._max_subscribe_keys:
                raise KiwoomSubscriptionLimitExceeded(
                    f"Kiwoom 실시간 구독 건수가 상한({self._max_subscribe_keys})을 초과합니다: "
                    f"현재 {self.get_subscription_count()}건 + 신규 {len(new_unique)}건 "
                    f"= {projected}건 요청 (type={type_code}). "
                    f"max_subscribe_keys 를 조정하거나 구독 수를 줄이세요."
                )

        if type_code not in self._subscribed_keys:
            self._subscribed_keys[type_code] = []

        for item in new_unique:
            self._subscribed_keys[type_code].append(item)
            asyncio.create_task(
                self._ws.send(self._build_subscribe_frame(type_code, item, register=True))
            )

    def _remove_keys(self, items: List[str], type_code: str) -> None:
        """``type_code`` 구독에서 ``items``를 제거합니다 (항목별 해제 프레임 전송)."""
        if not self._connected_event.is_set() or self._ws is None:
            raise RuntimeError("Kiwoom WebSocket이 연결되지 않았습니다")

        for item in items:
            if type_code in self._subscribed_keys:
                try:
                    self._subscribed_keys[type_code].remove(item)
                except ValueError:
                    continue
                asyncio.create_task(
                    self._ws.send(self._build_subscribe_frame(type_code, item, register=False))
                )

        if type_code in self._subscribed_keys and not self._subscribed_keys[type_code]:
            del self._subscribed_keys[type_code]
