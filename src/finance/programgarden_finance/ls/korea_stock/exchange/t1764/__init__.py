from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t1764")
from .blocks import (
    T1764RequestHeader,
    T1764ResponseHeader,
    T1764InBlock,
    T1764OutBlock,
    T1764Request,
    T1764Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT1764(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t1764 — 회원사리스트(t1764)"""

    def __init__(self, request_data: T1764Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T1764Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T1764Response] = GenericTR[T1764Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_EXCHANGE_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T1764Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t1764OutBlock", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T1764ResponseHeader.model_validate(resp_headers)

        block: list = []

        if exc is None and not is_error:
            block = [T1764OutBlock.model_validate(r) for r in block_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t1764 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t1764 request failed: {error_msg}")

        result = T1764Response(
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

    def req(self) -> T1764Response:
        return self._generic.req()

    async def req_async(self) -> T1764Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T1764Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)