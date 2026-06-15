"""빗썸(Bithumb) TR 요청을 위한 범용 핸들러입니다.

TR별로 ``response_builder``만 구현하면 요청 실행(rate-limit, 인증 헤더,
URL/쿼리/바디 구성, 동기/비동기 실행, 재시도)은 :class:`GenericBithumbTR`가
공통으로 처리합니다.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Generic, Iterable, Literal, Optional, Tuple, TypeVar
from urllib.parse import urlencode

import aiohttp

from programgarden_core.exceptions import AppKeyException

from .models import BithumbCredentials, SetupOptions
from .status import RequestStatus
from .tr_base import BithumbTRRequestAbstract, RetryReqAbstract

logger = logging.getLogger("programgarden.bithumb.tr_helpers")


R = TypeVar("R")


ResponseBuilder = Callable[[Optional[object], Optional[Any], Optional[dict], Optional[Exception]], R]


def set_tr_options(
    credentials: BithumbCredentials,
    options: Optional[SetupOptions],
    request_data: Any,
) -> None:
    """TR 요청에 클라이언트의 인증 정보를 주입하고, 사용자가 전달한 옵션을 적용합니다."""
    if options is not None:
        request_data.options = options

    if getattr(request_data, "options", None) is None:
        request_data.options = SetupOptions()

    request_data.options.credentials = credentials


def _serialize_query_value(value: Any) -> Any:
    """bool 값을 빗썸 API가 요구하는 소문자 문자열("true"/"false")로 변환합니다."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return [_serialize_query_value(v) for v in value]
    return value


def _serialize_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    return {key: _serialize_query_value(value) for key, value in params.items()}


def parse_bithumb_envelope(
    resp: Optional[object], resp_json: Optional[Any]
) -> Tuple[Optional[int], Any, Optional[str], Optional[str]]:
    """빗썸 응답을 ``(status_code, data, error_name, error_message)``로 분해합니다.

    - ``{"error": {"name":..., "message":...}}`` 형태면 에러로 처리합니다.
    - HTTP 상태코드가 400 이상이면 에러로 처리합니다.
    - 그 외에는 ``resp_json``을 그대로 ``data``로 반환합니다 (list 또는 dict).
    """
    status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None

    if isinstance(resp_json, dict) and isinstance(resp_json.get("error"), dict):
        err = resp_json["error"]
        return status, None, err.get("name"), err.get("message")

    if status is not None and status >= 400:
        message = resp_json.get("message") if isinstance(resp_json, dict) else None
        return status, None, None, message or f"HTTP {status}"

    return status, resp_json, None, None


class GenericBithumbTR(BithumbTRRequestAbstract, RetryReqAbstract, Generic[R]):
    """범용 빗썸 TR 핸들러입니다. TR별로 ``response_builder``만 구현하면 됩니다."""

    def __init__(
        self,
        request_data: Any,
        response_builder: ResponseBuilder,
        *,
        method: Literal["GET", "POST", "DELETE"],
        url: Optional[str] = None,
        url_builder: Optional[Callable[[Any], str]] = None,
        requires_auth: bool = False,
        exclude_params: Optional[Iterable[str]] = None,
        auth_query_string_builder: Optional[
            Callable[[Optional[Dict[str, Any]], Optional[Dict[str, Any]]], Optional[str]]
        ] = None,
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
        self._url = url
        self._url_builder = url_builder
        self._requires_auth = requires_auth
        self._exclude_params = set(exclude_params or ())
        self._auth_query_string_builder = auth_query_string_builder

    def _resolve_url(self) -> str:
        if self._url_builder is not None:
            return self._url_builder(self.request_data)
        return self._url

    def _build_query_params(self) -> Optional[Dict[str, Any]]:
        params = getattr(self.request_data, "params", None)
        if params is None:
            return None

        data = params.model_dump(exclude_none=True)
        for key in self._exclude_params:
            data.pop(key, None)

        if not data:
            return None

        return _serialize_query_params(data)

    def _build_json_body(self) -> Optional[Dict[str, Any]]:
        body = getattr(self.request_data, "body", None)
        if body is None:
            return None
        return body.model_dump(exclude_none=True)

    def _build_headers(
        self,
        query_params: Optional[Dict[str, Any]],
        json_body: Optional[Dict[str, Any]],
    ) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if json_body is not None:
            headers["Content-Type"] = "application/json"

        if self._requires_auth:
            credentials: Optional[BithumbCredentials] = getattr(self.request_data.options, "credentials", None)
            if credentials is None or not credentials.is_available():
                raise AppKeyException("Bithumb access_key/secret_key가 설정되지 않았습니다.")

            if self._auth_query_string_builder is not None:
                raw_query_string = self._auth_query_string_builder(query_params, json_body)
                headers["Authorization"] = credentials.get_authorization_header(raw_query_string=raw_query_string)
            else:
                auth_payload = query_params if query_params else json_body
                headers["Authorization"] = credentials.get_authorization_header(auth_payload)

        return headers

    def _build_request_url(self, query_params: Optional[Dict[str, Any]]) -> str:
        url = self._resolve_url()
        if query_params:
            return f"{url}?{urlencode(query_params, doseq=True)}"
        return url

    def req(self) -> R:
        try:
            query_params = self._build_query_params()
            json_body = self._build_json_body()
            headers = self._build_headers(query_params, json_body)
            url = self._build_request_url(query_params)

            resp, resp_json, resp_headers = self.execute_sync(
                method=self._method,
                url=url,
                json_body=json_body,
                headers=headers,
            )
            result: R = self._response_builder(resp, resp_json, resp_headers, None)
            if hasattr(result, "raw_data"):
                result.raw_data = resp
            return result

        except Exception as e:
            logger.error(f"GenericBithumbTR 동기 요청 중 예외: {e}")
            return self._response_builder(None, None, None, e)

    async def req_async(self) -> R:
        try:
            query_params = self._build_query_params()
            json_body = self._build_json_body()
            headers = self._build_headers(query_params, json_body)
            url = self._build_request_url(query_params)

            async with aiohttp.ClientSession() as session:
                resp, resp_json, resp_headers = await self.execute_async_with_session(
                    session,
                    method=self._method,
                    url=url,
                    json_body=json_body,
                    headers=headers,
                )
                result: R = self._response_builder(resp, resp_json, resp_headers, None)
                if hasattr(result, "raw_data"):
                    result.raw_data = resp
                return result

        except Exception as e:
            logger.error(f"GenericBithumbTR 비동기 요청 중 예외: {e}")
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
