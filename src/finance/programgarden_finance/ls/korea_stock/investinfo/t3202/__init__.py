from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t3202")
from .blocks import (
    T3202RequestHeader,
    T3202ResponseHeader,
    T3202InBlock,
    T3202OutBlock,
    T3202Request,
    T3202Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT3202(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t3202 — 종목별증시일정(t3202)"""

    def __init__(self, request_data: T3202Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T3202Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T3202Response] = GenericTR[T3202Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_INVESTINFO_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T3202Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t3202OutBlock", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T3202ResponseHeader.model_validate(resp_headers)

        block: list = []

        if exc is None and not is_error:
            block = [T3202OutBlock.model_validate(r) for r in block_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t3202 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t3202 request failed: {error_msg}")

        result = T3202Response(
            header=header,
            block=block,
            rsp_cd=resp_json.get('rsp_cd', ''),
            rsp_msg=resp_json.get('rsp_msg', ''),
            status_code=status,
            error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T3202Response:
        return self._generic.req()

    async def req_async(self) -> T3202Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T3202Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)