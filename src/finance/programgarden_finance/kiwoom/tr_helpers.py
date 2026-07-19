"""키움증권(Kiwoom Securities) TR 요청을 위한 범용 핸들러입니다.

TR별로 ``response_builder``만 구현하면 요청 실행(rate-limit, 인증 헤더,
동기/비동기 실행, 토큰 만료 재시도)은 :class:`GenericKiwoomTR`가 공통으로
처리합니다.

키움 헤더 규격 (KIS와 다름):
- ``authorization``: ``Bearer <접근토큰>``
- ``api-id``: TR 식별자 (KIS의 ``tr_id`` 에 대응, 예: ``ka10001``, ``kt10000``)
- ``cont-yn``/``next-key``: 연속조회용 헤더. MVP에서는 항상 ``N``/``""`` 로
  고정하며 페이지네이션은 구현하지 않습니다.
  TODO(실계좌 검증): 연속조회(``cont-yn: Y``) 흐름 구현 (KIS의 tr_cont
  페이지네이션 처리 참고).
- appkey/secretkey 헤더는 TR 요청에 포함하지 않습니다 (토큰 발급 시에만 사용).
- 모든 TR은 POST이며, 조회/주문 구분 없이 파라미터가 단일 JSON 바디로 전송됩니다
  (KIS처럼 GET 쿼리 파라미터와 POST 바디가 나뉘지 않음).
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Generic, Optional, Tuple, TypeVar

import aiohttp

from programgarden_core.exceptions import AppKeyException

from .models import SetupOptions
from .status import RequestStatus
from .token_manager import KiwoomTokenManager
from .tr_base import KiwoomTRRequestAbstract, RetryReqAbstract

logger = logging.getLogger("programgarden.kiwoom.tr_helpers")


R = TypeVar("R")

ResponseBuilder = Callable[[Optional[object], Optional[Any], Optional[dict], Optional[Exception]], R]


def set_tr_options(
    token_manager: KiwoomTokenManager,
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


def parse_kiwoom_envelope(
    resp: Optional[object], resp_json: Optional[Any]
) -> Tuple[Optional[int], Optional[int], Optional[str], Dict[str, Any]]:
    """키움 응답을 ``(status, return_code, return_msg, data)``로 분해합니다.

    - ``return_code != 0`` 또는 HTTP 상태코드 400 이상이면 에러입니다.
    - KIS와 달리 output/output1/output2 같은 별도 데이터 봉투 키가 없습니다.
      TR 데이터는 최상위 키에 직접 오거나(예: kt00010의 ``ord_alow_amt``),
      이름 있는 리스트 키(예: ka10081의 ``stk_dt_pole``)로 옵니다. 따라서
      ``data`` 는 응답 JSON 전체(dict)를 그대로 반환하며, 각 TR 모듈이
      필요한 키를 직접 꺼내 씁니다.
    """
    status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None

    if not isinstance(resp_json, dict):
        return status, None, None, {}

    return_code = resp_json.get("return_code")
    return_msg = resp_json.get("return_msg")
    if isinstance(return_msg, str):
        return_msg = return_msg.strip()

    return status, return_code, return_msg, resp_json


def is_kiwoom_error(status: Optional[int], return_code: Optional[int]) -> bool:
    """HTTP 상태코드와 return_code로 에러 여부를 판정합니다 (return_code == 0 이 성공)."""
    if status is not None and status >= 400:
        return True
    return return_code is not None and return_code != 0


class GenericKiwoomTR(KiwoomTRRequestAbstract, RetryReqAbstract, Generic[R]):
    """범용 키움 TR 핸들러입니다. TR별로 ``response_builder``만 구현하면 됩니다.

    Parameters:
        request_data: ``body``/``options`` 를 가진 요청 모델.
        response_builder: ``(resp, resp_json, resp_headers, exc) -> R`` 응답 빌더.
        url_path: 엔드포인트 경로 — 실전/모의 도메인은 token_manager가 결정.
        tr_id: TR 식별자(``api-id``). 키움은 실전/모의 분기가 도메인
            단위이므로 KIS의 ``(실전, 모의)`` 튜플과 달리 항상 단일 문자열입니다.
    """

    def __init__(
        self,
        request_data: Any,
        response_builder: ResponseBuilder,
        *,
        url_path: str,
        tr_id: str,
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
        self._url_path = url_path
        self._tr_id = tr_id

    # ─────────────────────────────────────────── 요청 구성 ──

    def _token_manager(self) -> KiwoomTokenManager:
        token_manager: Optional[KiwoomTokenManager] = getattr(
            self.request_data.options, "token_manager", None
        )
        if token_manager is None or not token_manager.appkey or not token_manager.appsecret:
            raise AppKeyException("Kiwoom appkey/secretkey가 설정되지 않았습니다.")
        return token_manager

    def resolve_tr_id(self) -> str:
        """``api-id`` 헤더 값을 반환합니다.

        키움은 실전/모의 분기가 도메인 단위이므로 KIS의 tr_id 튜플 해석과
        달리 항상 저장된 문자열을 그대로 반환합니다.
        """
        return self._tr_id

    def _build_url(self) -> str:
        return f"{self._token_manager().base_url}{self._url_path}"

    def _build_json_body(self) -> Optional[Dict[str, Any]]:
        body = getattr(self.request_data, "body", None)
        if body is None:
            return None
        return body.model_dump(by_alias=True)

    def _build_headers(self) -> Dict[str, str]:
        token_manager = self._token_manager()
        return {
            "Content-Type": "application/json;charset=UTF-8",
            "authorization": token_manager.get_bearer_token(),
            "api-id": self.resolve_tr_id(),
            # 연속조회 미구현 — 항상 최초 조회로 취급합니다.
            # TODO(실계좌 검증): cont-yn/next-key 페이지네이션 구현.
            "cont-yn": "N",
            "next-key": "",
        }

    def _is_expired_token_response(self, resp, resp_json) -> bool:
        """토큰 만료 여부를 판정합니다.

        키움의 토큰 만료 시 return_code/return_msg 값이 문서로 확인되지
        않아, 우선 HTTP 401만 판단 기준으로 삼습니다.
        TODO(실계좌 검증): return_code 기반 만료 코드 확인 후 KIS의
        ``_EXPIRED_TOKEN_MSG_CODES`` 처럼 세분화.
        """
        status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None
        return status == 401

    # ─────────────────────────────────────────── 요청 실행 ──

    def req(self) -> R:
        try:
            json_body = self._build_json_body()
            url = self._build_url()

            resp, resp_json, resp_headers = self.execute_sync(
                method="POST",
                url=url,
                json_body=json_body,
                headers=self._build_headers(),
            )

            # 토큰 만료 → 강제 재발급 후 1회 재시도
            if self._is_expired_token_response(resp, resp_json):
                logger.info("Kiwoom 토큰 만료 응답 감지 — 재발급 후 재시도")
                token_manager = self._token_manager()
                token_manager.invalidate()
                token_manager.ensure_fresh_token(force_refresh=True)
                resp, resp_json, resp_headers = self.execute_sync(
                    method="POST",
                    url=url,
                    json_body=json_body,
                    headers=self._build_headers(),
                )

            result: R = self._response_builder(resp, resp_json, resp_headers, None)
            if hasattr(result, "raw_data"):
                result.raw_data = resp
            return result

        except Exception as e:
            logger.error(f"GenericKiwoomTR 동기 요청 중 예외: {e}")
            return self._response_builder(None, None, None, e)

    async def req_async(self) -> R:
        try:
            json_body = self._build_json_body()
            url = self._build_url()

            async with aiohttp.ClientSession() as session:
                resp, resp_json, resp_headers = await self.execute_async_with_session(
                    session,
                    method="POST",
                    url=url,
                    json_body=json_body,
                    headers=self._build_headers(),
                )

                if self._is_expired_token_response(resp, resp_json):
                    logger.info("Kiwoom 토큰 만료 응답 감지 — 재발급 후 재시도 (async)")
                    token_manager = self._token_manager()
                    token_manager.invalidate()
                    await asyncio.to_thread(token_manager.ensure_fresh_token, True)
                    resp, resp_json, resp_headers = await self.execute_async_with_session(
                        session,
                        method="POST",
                        url=url,
                        json_body=json_body,
                        headers=self._build_headers(),
                    )

                result: R = self._response_builder(resp, resp_json, resp_headers, None)
                if hasattr(result, "raw_data"):
                    result.raw_data = resp
                return result

        except Exception as e:
            logger.error(f"GenericKiwoomTR 비동기 요청 중 예외: {e}")
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
