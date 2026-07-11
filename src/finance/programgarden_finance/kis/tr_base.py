"""한국투자증권(KIS) TR 요청을 위한 추상 클래스입니다.

빗썸 패키지의 ``bithumb/tr_base.py`` 슬라이딩 윈도우 rate-limit 구조를 따릅니다.
KIS rate-limit은 appkey 기준(실전 초당 20건, 모의 초당 2건)이므로
``rate_limit_key="kis:<appkey>"`` 로 같은 계정의 TR들이 버킷을 공유합니다.
"""

from abc import ABC, abstractmethod
import asyncio
import logging
import math
import threading
import time
from typing import Any, Callable, List, Literal, Mapping, Optional, TypeVar

import aiohttp
import requests

logger = logging.getLogger("programgarden.kis.tr_base")


TRresponse = TypeVar("TRresponse")


class KisTRRequestAbstract(ABC):
    """KIS TR 요청 추상 클래스 (슬라이딩 윈도우 rate-limit 포함)."""

    _shared_rate_data: dict[str, dict] = {}

    def __init__(
        self,
        rate_limit_count: int,
        rate_limit_seconds: int,
        on_rate_limit: Literal["stop", "wait"] = "wait",
        rate_limit_key: Optional[str] = None,
    ):
        super().__init__()

        if rate_limit_key:
            shared = KisTRRequestAbstract._shared_rate_data.get(rate_limit_key)
            if shared is None:
                lock = threading.RLock()
                shared = {"lock": lock, "cond": threading.Condition(lock), "timestamps": []}
                KisTRRequestAbstract._shared_rate_data[rate_limit_key] = shared

            self._lock: threading.RLock = shared["lock"]
            self._sync_cond: threading.Condition = shared["cond"]
            self.request_timestamps: List[float] = shared["timestamps"]
        else:
            self._lock = threading.RLock()
            self._sync_cond = threading.Condition(self._lock)
            self.request_timestamps = []

        self.rate_limit_count = rate_limit_count
        self.rate_limit_seconds = rate_limit_seconds

        if on_rate_limit not in ("stop", "wait"):
            raise ValueError("on_rate_limit must be 'stop' or 'wait'")
        self.on_rate_limit = on_rate_limit

    def cleanup_timestamps(self) -> None:
        """rate_limit_seconds 윈도우를 벗어난 오래된 타임스탬프를 제거합니다."""
        now = time.time()
        with self._lock:
            self.request_timestamps[:] = [
                ts for ts in self.request_timestamps
                if math.ceil((now - ts) * 100) / 100 < self.rate_limit_seconds
            ]
            self._sync_cond.notify_all()

    def is_rate_limited(self) -> bool:
        with self._lock:
            self.cleanup_timestamps()
            return len(self.request_timestamps) >= self.rate_limit_count

    def record_request(self) -> None:
        with self._lock:
            self.cleanup_timestamps()
            self.request_timestamps.append(time.time())
            self._sync_cond.notify_all()

    async def record_request_async(self) -> None:
        await asyncio.to_thread(self.record_request)

    def wait_until_available(self) -> None:
        """rate-limit 윈도우에 여유가 생길 때까지 대기한 뒤 요청 1건을 기록합니다."""
        with self._sync_cond:
            while True:
                self.cleanup_timestamps()
                if len(self.request_timestamps) < self.rate_limit_count:
                    self.request_timestamps.append(time.time())
                    self._sync_cond.notify_all()
                    return

                oldest = min(self.request_timestamps)
                wait_time = self.rate_limit_seconds - (time.time() - oldest)
                if wait_time <= 0:
                    continue
                self._sync_cond.wait(wait_time)

    async def wait_until_available_async(self) -> None:
        while True:
            await asyncio.to_thread(self.cleanup_timestamps)
            with self._lock:
                if len(self.request_timestamps) < self.rate_limit_count:
                    self.request_timestamps.append(time.time())
                    self._sync_cond.notify_all()
                    return

                oldest = min(self.request_timestamps)
                wait_time = self.rate_limit_seconds - (time.time() - oldest)

            if wait_time <= 0:
                continue
            await asyncio.sleep(wait_time)

    def execute_sync(
        self,
        method: str,
        url: str,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: int = 10,
    ):
        """동기 HTTP 요청을 실행합니다. rate-limit 정책에 따라 대기 또는 즉시 예외 처리합니다."""
        try:
            if self.on_rate_limit == "stop":
                if self.is_rate_limited():
                    raise ValueError("KIS rate limit exceeded")
                self.record_request()
            else:
                self.wait_until_available()

            resp = requests.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=timeout,
            )

            try:
                resp_json = resp.json()
            except ValueError:
                resp_json = None

            return resp, resp_json, dict(resp.headers)

        except requests.RequestException as e:
            logger.error(f"KIS 동기 요청 실패: {e}")
            raise

    async def execute_async_with_session(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        params: Optional[Mapping[str, Any]] = None,
        json_body: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        timeout: int = 10,
    ):
        """비동기 HTTP 요청을 실행합니다. rate-limit 정책에 따라 대기 또는 즉시 예외 처리합니다."""
        try:
            if self.on_rate_limit == "stop":
                if self.is_rate_limited():
                    raise ValueError("KIS rate limit exceeded")
                await self.record_request_async()
            else:
                await self.wait_until_available_async()

            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as resp:
                try:
                    resp_json = await resp.json()
                except aiohttp.ContentTypeError:
                    resp_json = None

                return resp, resp_json, dict(resp.headers)

        except aiohttp.ClientError as e:
            logger.error(f"KIS 비동기 요청 실패: {e}")
            raise

    @abstractmethod
    def req(self, *args, **kwargs) -> TRresponse:
        ...

    @abstractmethod
    async def req_async(self, *args, **kwargs) -> TRresponse:
        ...


class RetryReqAbstract(ABC):
    """요청을 반복적으로 시도하는 추상 클래스입니다."""

    @abstractmethod
    def retry_req(self, callback: Callable, max_retries: int = 3, delay: int = 2) -> TRresponse:
        ...

    @abstractmethod
    async def retry_req_async(self, callback: Callable, max_retries: int = 3, delay: int = 2) -> TRresponse:
        ...
