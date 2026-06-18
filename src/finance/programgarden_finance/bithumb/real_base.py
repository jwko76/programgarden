"""빗썸(Bithumb) 실시간 WebSocket 기반 클래스입니다.

빗썸 공개 WebSocket(``wss://pubwss.bithumb.com/pub/ws``)을 위한
재연결 지원 기반 구조를 제공합니다. LS증권의 ``RealRequestAbstract``와
동일한 생명주기(connect/close, ref-count, 재연결 + 자동 재구독)를 따르되
인증이 불필요하고 구독 방식이 다릅니다 — ``{"type": "ticker", "codes": [...]}``
형식의 단일 JSON 메시지로 전체 코드 목록을 전송합니다.
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

_logger = logging.getLogger("programgarden_finance.bithumb.real")

DEFAULT_MAX_SUBSCRIBE_CODES = 15

# stream_type -> parsed response model class (lazy-loaded, None = import failed)
_MODEL_CACHE: Dict[str, Optional[type]] = {}

_STREAM_MODEL_MAP: Dict[str, tuple] = {
    "ticker": (
        "programgarden_finance.bithumb.real.ticker.blocks",
        "TickerRealResponse",
    ),
    "trade": (
        "programgarden_finance.bithumb.real.trade.blocks",
        "TradeRealResponse",
    ),
    "orderbook": (
        "programgarden_finance.bithumb.real.orderbook.blocks",
        "OrderbookRealResponse",
    ),
}


def _get_response_model(stream_type: str) -> Optional[type]:
    """stream_type에 해당하는 Pydantic 응답 모델 클래스를 반환합니다 (lazy import)."""
    if stream_type in _MODEL_CACHE:
        return _MODEL_CACHE[stream_type]
    if stream_type not in _STREAM_MODEL_MAP:
        _MODEL_CACHE[stream_type] = None
        return None
    mod_path, cls_name = _STREAM_MODEL_MAP[stream_type]
    try:
        m = importlib.import_module(mod_path)
        _MODEL_CACHE[stream_type] = getattr(m, cls_name)
    except Exception:
        _MODEL_CACHE[stream_type] = None
    return _MODEL_CACHE[stream_type]


class BithumbSubscriptionLimitExceeded(RuntimeError):
    """연결당 실시간 구독 코드 수가 상한을 초과할 때 발생합니다.

    LS증권의 ``SubscriptionLimitExceeded``에 대응합니다. ``max_subscribe_codes``
    매개변수로 상한을 조정하거나 ``<=0`` 으로 설정해 비활성화할 수 있습니다.
    """


class BithumbRealBase:
    """빗썸 공개 WebSocket 재연결 지원 기반 클래스.

    인증 없이 사용할 수 있는 빗썸 공개 WebSocket에 연결하여
    ``ticker`` / ``trade`` / ``orderbook`` 스트림을 구독합니다.
    재연결 시 자동으로 이전 구독을 복원합니다.

    **구독 프로토콜** — LS증권과 달리 종목별로 별도 메시지를 보내지 않고,
    스트림 타입별로 전체 코드 목록을 담은 단일 메시지를 전송합니다:

        ``{"type": "ticker", "codes": ["KRW-BTC", "KRW-ETH"]}``

    코드 추가/제거 시마다 해당 스트림 타입의 전체 코드 목록을 재전송합니다.
    """

    WSS_URL = "wss://pubwss.bithumb.com/pub/ws"

    def __init__(
        self,
        reconnect: bool = True,
        max_backoff: float = 60.0,
        max_subscribe_codes: int = DEFAULT_MAX_SUBSCRIBE_CODES,
    ):
        self._reconnect = reconnect
        self._max_backoff = max_backoff
        self._max_subscribe_codes = max_subscribe_codes

        self._connected_event = asyncio.Event()
        self._ws = None
        self._listen_task: Optional[asyncio.Task] = None
        self._stop = False

        self._ref_count = 0
        self._ref_lock = asyncio.Lock()

        # stream_type → listener (receives parsed Pydantic model or raw dict)
        self._on_message_listeners: Dict[str, Callable[[Any], Any]] = {}
        # stream_type → [codes]  (재연결 시 자동 재구독용)
        self._subscribed_codes: Dict[str, List[str]] = {}
        self._last_message_time: float = 0.0

    # ──────────────────────────────────────────── 상태 조회 ──

    async def is_connected(self) -> bool:
        """WebSocket 핸드셰이크가 완료되었는지 확인합니다."""
        return self._connected_event.is_set()

    def get_subscribed_codes(self) -> Dict[str, List[str]]:
        """현재 구독 중인 코드 목록 (stream_type → codes)."""
        return {k: list(v) for k, v in self._subscribed_codes.items()}

    def get_subscription_count(self) -> int:
        """가장 많은 코드가 구독된 스트림 타입의 코드 수.

        빗썸 스트림 타입은 서로 독립적이므로 max 값을 반환합니다.
        """
        if not self._subscribed_codes:
            return 0
        return max(len(v) for v in self._subscribed_codes.values())

    def get_subscription_capacity(self) -> Optional[int]:
        """남은 구독 여유분. cap 비활성(``max_subscribe_codes <= 0``) 시 ``None``."""
        if self._max_subscribe_codes <= 0:
            return None
        return max(0, self._max_subscribe_codes - self.get_subscription_count())

    def get_staleness_sec(self) -> float:
        """마지막 메시지 수신 이후 경과 시간(초). 아직 메시지가 없으면 0."""
        if self._last_message_time <= 0:
            return 0.0
        return time.time() - self._last_message_time

    # ─────────────────────────────────────────── connect/close ──

    async def connect(self, wait: bool = True, timeout: float = 5.0):
        """WebSocket을 열고 리스너 루프를 시작합니다.

        이미 연결된 경우 참조 카운트만 증가시키고 즉시 반환합니다(싱글톤 안전).
        ``reconnect=True`` 설정 시 지수 백오프로 자동 재연결합니다.

        Parameters:
            wait: True면 연결이 완료될 때까지 대기합니다.
            timeout: ``wait=True`` 일 때 최대 대기 시간(초).
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
                    raise RuntimeError("빗썸 WebSocket 연결 대기 시간 초과")
            return

        async def _connection_loop():
            backoff = 1.0
            while not self._stop:
                try:
                    async with connect(
                        uri=self.WSS_URL,
                        ping_interval=None,
                        ping_timeout=None,
                    ) as ws:
                        self._ws = ws
                        try:
                            self._connected_event.set()
                        except Exception:
                            pass

                        # 재연결 후 이전 구독 자동 복원
                        if backoff > 1.0 and self._subscribed_codes:
                            for stype, codes in list(self._subscribed_codes.items()):
                                if codes:
                                    try:
                                        await ws.send(json.dumps({
                                            "type": stype,
                                            "codes": codes,
                                        }))
                                        _logger.info(
                                            "빗썸 WebSocket 재연결 후 자동 재구독: "
                                            "%s %d개 코드", stype, len(codes)
                                        )
                                    except Exception as exc:
                                        _logger.error(
                                            "빗썸 재구독 실패 (%s): %s", stype, exc
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
                                        "빗썸 WebSocket 무 데이터 경고: "
                                        "%.0f초 동안 메시지 수신 없음.", staleness
                                    )
                                continue

                            self._last_message_time = time.time()
                            _staleness_warned = False

                            try:
                                msg = json.loads(raw)
                            except Exception:
                                continue

                            # 연결 성공 메시지 {"status": "0000", "resmsg": "..."}
                            if "status" in msg:
                                continue

                            stream_type = msg.get("type")
                            if not stream_type:
                                continue

                            listener = self._on_message_listeners.get(stream_type)
                            if listener is None:
                                continue

                            # 모델 파싱
                            model_cls = _get_response_model(stream_type)
                            if model_cls is not None:
                                try:
                                    resp = model_cls.model_validate(msg)
                                except Exception as exc:
                                    try:
                                        resp = model_cls.model_construct(
                                            error_msg=str(exc)
                                        )
                                    except Exception:
                                        continue
                            else:
                                resp = msg

                            loop = asyncio.get_running_loop()
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

                except asyncio.CancelledError:
                    break
                except Exception:
                    if not self._reconnect:
                        break

                if not self._reconnect or self._stop:
                    break

                _logger.warning(
                    "빗썸 WebSocket 연결 끊김 — 재연결 시도 중 (backoff=%.1fs). "
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
                raise RuntimeError("빗썸 WebSocket 연결 대기 시간 초과")
        else:
            await asyncio.sleep(0)

    async def close(self, force: bool = False):
        """WebSocket 연결을 닫습니다.

        참조 카운트를 감소시키고 0이 되었을 때만 실제 종료를 수행합니다.
        ``force=True`` 는 참조 카운트를 무시하고 즉시 종료합니다.

        Parameters:
            force: True면 ref-count 를 무시하고 즉시 종료합니다.
        """
        async with self._ref_lock:
            if not force:
                self._ref_count = max(0, self._ref_count - 1)
                if self._ref_count > 0:
                    return
            elif self._ref_count > 1:
                _logger.warning(
                    "빗썸 WebSocket force close: ref_count=%d. "
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
        """``Bithumb._real_instances`` 싱글톤 캐시에서 이 인스턴스를 제거합니다."""
        try:
            from programgarden_finance.bithumb.client import Bithumb
            for key, inst in list(Bithumb._real_instances.items()):
                if inst is self:
                    del Bithumb._real_instances[key]
                    break
        except Exception:
            pass

    # ──────────────────────────────────────── 리스너 등록/해제 ──

    def _on_message(self, stream_type: str, listener: Callable[[Any], Any]) -> None:
        """특정 스트림 타입의 메시지 콜백을 등록합니다.

        ``listener`` 는 sync 또는 async 함수 모두 허용합니다.
        """
        if not self._connected_event.is_set():
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        self._on_message_listeners[stream_type] = listener

    def _on_remove_message(self, stream_type: str) -> None:
        """등록된 리스너를 해제합니다."""
        if not self._connected_event.is_set():
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        self._on_message_listeners.pop(stream_type, None)

    # ──────────────────────────────────────── 구독 추가/제거 ──

    def _add_codes(self, codes: List[str], stream_type: str) -> None:
        """``stream_type`` 구독에 ``codes``를 추가하고 전체 구독 메시지를 전송합니다.

        빗썸 WebSocket은 종목별 개별 메시지가 아닌 타입별 전체 코드 목록을
        재전송하는 방식으로 구독을 업데이트합니다.

        Parameters:
            codes: 추가할 마켓 코드 목록 (ex. ``["KRW-BTC", "KRW-ETH"]``).
            stream_type: ``"ticker"`` / ``"trade"`` / ``"orderbook"``.
        """
        if not self._connected_event.is_set():
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        if self._ws is None:
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")

        if self._max_subscribe_codes > 0:
            existing = self._subscribed_codes.get(stream_type, [])
            new_unique = [c for c in dict.fromkeys(codes) if c not in existing]
            projected = len(existing) + len(new_unique)
            if projected > self._max_subscribe_codes:
                raise BithumbSubscriptionLimitExceeded(
                    f"빗썸 실시간 구독 코드 수가 상한({self._max_subscribe_codes})을 초과합니다: "
                    f"현재 {len(existing)}개 + 신규 {len(new_unique)}개 "
                    f"= {projected}개 요청 (stream_type={stream_type}). "
                    f"max_subscribe_codes 를 조정하거나 구독 코드 수를 줄이세요."
                )

        if stream_type not in self._subscribed_codes:
            self._subscribed_codes[stream_type] = []
        for code in codes:
            if code not in self._subscribed_codes[stream_type]:
                self._subscribed_codes[stream_type].append(code)

        asyncio.create_task(
            self._ws.send(
                json.dumps({"type": stream_type, "codes": self._subscribed_codes[stream_type]})
            )
        )

    def _remove_codes(self, codes: List[str], stream_type: str) -> None:
        """``stream_type`` 구독에서 ``codes``를 제거하고 전체 구독 메시지를 전송합니다.

        모든 코드가 제거된 경우 빈 코드 목록으로 구독 취소 메시지를 전송합니다.
        """
        if not self._connected_event.is_set():
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        if self._ws is None:
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")

        if stream_type in self._subscribed_codes:
            for code in codes:
                try:
                    self._subscribed_codes[stream_type].remove(code)
                except ValueError:
                    pass
            if not self._subscribed_codes[stream_type]:
                del self._subscribed_codes[stream_type]

        remaining = self._subscribed_codes.get(stream_type, [])
        asyncio.create_task(
            self._ws.send(json.dumps({"type": stream_type, "codes": remaining}))
        )
