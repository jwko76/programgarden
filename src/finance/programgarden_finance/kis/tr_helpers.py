"""한국투자증권(KIS) TR 요청을 위한 범용 핸들러입니다.

TR별로 ``response_builder``만 구현하면 요청 실행(rate-limit, 인증 헤더,
tr_id 실전/모의 분기, 동기/비동기 실행, 토큰 만료 재시도)은
:class:`GenericKisTR`가 공통으로 처리합니다.

KIS 헤더 규격:
- ``authorization``: ``Bearer <접근토큰>``
- ``appkey`` / ``appsecret``: 앱 키/시크릿
- ``tr_id``: TR 식별자 — 주문·계좌 TR은 실전(TTTC…)/모의(VTTC…)가 다름
- ``custtype``: ``P`` (개인)
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Generic, Literal, Optional, Tuple, TypeVar, Union

import aiohttp

from programgarden_core.exceptions import AppKeyException

from .config import URLS
from .models import SetupOptions
from .status import RequestStatus
from .token_manager import KisTokenManager
from .tr_base import KisTRRequestAbstract, RetryReqAbstract

logger = logging.getLogger("programgarden.kis.tr_helpers")


R = TypeVar("R")

ResponseBuilder = Callable[[Optional[object], Optional[Any], Optional[dict], Optional[Exception]], R]

# 토큰 만료를 나타내는 KIS 메시지 코드 (강제 재발급 + 1회 재시도 대상)
_EXPIRED_TOKEN_MSG_CODES = {"EGW00123", "EGW00121"}


def set_tr_options(
    token_manager: KisTokenManager,
    options: Optional[SetupOptions],
    request_data: Any,
) -> None:
    """TR 요청에 클라이언트의 토큰 관리자를 주입하고, 사용자가 전달한 옵션을 적용합니다."""
    if options is not None:
        request_data.options = options

    if getattr(request_data, "options", None) is None:
        request_data.options = SetupOptions.for_mode(
            token_manager.paper_trading, token_manager.appkey
        )

    request_data.options.token_manager = token_manager


def parse_kis_envelope(
    resp: Optional[object], resp_json: Optional[Any]
) -> Tuple[Optional[int], Optional[str], Optional[str], Optional[str], Dict[str, Any]]:
    """KIS 응답을 ``(status, rt_cd, msg_cd, msg1, outputs)``로 분해합니다.

    - ``rt_cd != "0"`` 또는 HTTP 상태코드 400 이상이면 에러입니다.
    - ``outputs`` 는 ``{"output": ..., "output1": ..., "output2": ...}`` 중
      존재하는 키만 담은 dict입니다.
    """
    status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None

    if not isinstance(resp_json, dict):
        return status, None, None, None, {}

    rt_cd = resp_json.get("rt_cd")
    msg_cd = resp_json.get("msg_cd")
    msg1 = resp_json.get("msg1")
    if isinstance(msg1, str):
        msg1 = msg1.strip()

    outputs = {
        key: resp_json[key]
        for key in ("output", "output1", "output2")
        if key in resp_json
    }
    return status, rt_cd, msg_cd, msg1, outputs


def is_kis_error(status: Optional[int], rt_cd: Optional[str]) -> bool:
    """HTTP 상태코드와 rt_cd로 에러 여부를 판정합니다."""
    if status is not None and status >= 400:
        return True
    return rt_cd is not None and rt_cd != "0"


class GenericKisTR(KisTRRequestAbstract, RetryReqAbstract, Generic[R]):
    """범용 KIS TR 핸들러입니다. TR별로 ``response_builder``만 구현하면 됩니다.

    Parameters:
        request_data: ``params``/``body``/``options`` 를 가진 요청 모델.
        response_builder: ``(resp, resp_json, resp_headers, exc) -> R`` 응답 빌더.
        method: HTTP 메서드 (시세·계좌 GET, 주문 POST).
        url_path: 엔드포인트 경로 — 실전/모의 도메인은 token_manager가 결정.
        tr_id: TR 식별자. ``(실전, 모의)`` 튜플이면 paper_trading으로 자동 선택.
    """

    def __init__(
        self,
        request_data: Any,
        response_builder: ResponseBuilder,
        *,
        method: Literal["GET", "POST"],
        url_path: str,
        tr_id: Union[str, Tuple[str, str]],
    ):
        options: SetupOptions = request_data.options
        super().__init__(
            rate_limit_count=options.rate_limit_count,
            rate_limit_seconds=options.rate_limit_seconds,
            on_rate_limit=options.on_rate_limit,
            rate_limit_key=options.rate_limit_key,
        )
        self.request_data = request_data
        self._response_builder = response_builder
        self._method = method
        self._url_path = url_path
        self._tr_id = tr_id

    # ─────────────────────────────────────────── 요청 구성 ──

    def _token_manager(self) -> KisTokenManager:
        token_manager: Optional[KisTokenManager] = getattr(
            self.request_data.options, "token_manager", None
        )
        if token_manager is None or not token_manager.appkey or not token_manager.appsecret:
            raise AppKeyException("KIS appkey/appsecret이 설정되지 않았습니다.")
        return token_manager

    def resolve_tr_id(self) -> str:
        """실전/모의 모드에 맞는 tr_id를 반환합니다."""
        if isinstance(self._tr_id, tuple):
            real_id, paper_id = self._tr_id
            return paper_id if self._token_manager().paper_trading else real_id
        return self._tr_id

    def _build_url(self) -> str:
        return f"{self._token_manager().base_url}{self._url_path}"

    def _build_query_params(self) -> Optional[Dict[str, Any]]:
        params = getattr(self.request_data, "params", None)
        if params is None:
            return None
        return params.model_dump(by_alias=True)

    def _build_json_body(self) -> Optional[Dict[str, Any]]:
        body = getattr(self.request_data, "body", None)
        if body is None:
            return None
        return body.model_dump(by_alias=True)

    def _build_headers(self) -> Dict[str, str]:
        token_manager = self._token_manager()
        return {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": token_manager.get_bearer_token(),
            "appkey": token_manager.appkey,
            "appsecret": token_manager.appsecret,
            "tr_id": self.resolve_tr_id(),
            "custtype": "P",
        }

    def _is_expired_token_response(self, resp, resp_json) -> bool:
        status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None
        if status == 401:
            return True
        if isinstance(resp_json, dict):
            return resp_json.get("msg_cd") in _EXPIRED_TOKEN_MSG_CODES
        return False

    # ─────────────────────────────────────────── 요청 실행 ──

    def req(self) -> R:
        try:
            query_params = self._build_query_params()
            json_body = self._build_json_body()
            url = self._build_url()

            resp, resp_json, resp_headers = self.execute_sync(
                method=self._method,
                url=url,
                params=query_params,
                json_body=json_body,
                headers=self._build_headers(),
            )

            # 토큰 만료 → 강제 재발급 후 1회 재시도
            if self._is_expired_token_response(resp, resp_json):
                logger.info("KIS 토큰 만료 응답 감지 — 재발급 후 재시도")
                token_manager = self._token_manager()
                token_manager.invalidate()
                token_manager.ensure_fresh_token(force_refresh=True)
                resp, resp_json, resp_headers = self.execute_sync(
                    method=self._method,
                    url=url,
                    params=query_params,
                    json_body=json_body,
                    headers=self._build_headers(),
                )

            result: R = self._response_builder(resp, resp_json, resp_headers, None)
            if hasattr(result, "raw_data"):
                result.raw_data = resp
            return result

        except Exception as e:
            logger.error(f"GenericKisTR 동기 요청 중 예외: {e}")
            return self._response_builder(None, None, None, e)

    async def req_async(self) -> R:
        try:
            query_params = self._build_query_params()
            json_body = self._build_json_body()
            url = self._build_url()

            async with aiohttp.ClientSession() as session:
                resp, resp_json, resp_headers = await self.execute_async_with_session(
                    session,
                    method=self._method,
                    url=url,
                    params=query_params,
                    json_body=json_body,
                    headers=self._build_headers(),
                )

                if self._is_expired_token_response(resp, resp_json):
                    logger.info("KIS 토큰 만료 응답 감지 — 재발급 후 재시도 (async)")
                    token_manager = self._token_manager()
                    token_manager.invalidate()
                    await asyncio.to_thread(token_manager.ensure_fresh_token, True)
                    resp, resp_json, resp_headers = await self.execute_async_with_session(
                        session,
                        method=self._method,
                        url=url,
                        params=query_params,
                        json_body=json_body,
                        headers=self._build_headers(),
                    )

                result: R = self._response_builder(resp, resp_json, resp_headers, None)
                if hasattr(result, "raw_data"):
                    result.raw_data = resp
                return result

        except Exception as e:
            logger.error(f"GenericKisTR 비동기 요청 중 예외: {e}")
            return self._response_builder(None, None, None, e)

    def retry_req(self, callback: Callable[[Optional[R], RequestStatus], None], max_retries: int = 3, delay: int = 2) -> R:
        response: Optional[R] = None
        for attempt in range(max_retries):
            callback(None, RequestStatus.REQUEST)
            response = self.req()

            if getattr(response, "error_msg", None) is not None:
                callback(response, RequestStatus.FAIL)
            else:
                callback(response, RequestStatus.RESPONSE)

            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                callback(None, RequestStatus.COMPLETE)

        callback(None, RequestStatus.CLOSE)
        return response

    async def retry_req_async(self, callback: Callable[[Optional[R], RequestStatus], None], max_retries: int = 3, delay: int = 2) -> R:
        response: Optional[R] = None
        for attempt in range(max_retries):
            callback(None, RequestStatus.REQUEST)
            response = await self.req_async()

            if getattr(response, "error_msg", None) is not None:
                callback(response, RequestStatus.FAIL)
            else:
                callback(response, RequestStatus.RESPONSE)

            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
            else:
                callback(None, RequestStatus.COMPLETE)

        callback(None, RequestStatus.CLOSE)
        return response
