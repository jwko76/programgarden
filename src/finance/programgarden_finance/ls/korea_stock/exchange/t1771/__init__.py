from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t1771")
from .blocks import (
    T1771RequestHeader,
    T1771ResponseHeader,
    T1771InBlock,
    T1771OutBlock,
    T1771OutBlock2,
    T1771Request,
    T1771Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT1771(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t1771 — 종목별회원사추이(t1771)"""

    def __init__(self, request_data: T1771Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T1771Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T1771Response] = GenericTR[T1771Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_EXCHANGE_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T1771Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t1771OutBlock")
        block2_data = resp_json.get("t1771OutBlock2", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T1771ResponseHeader.model_validate(resp_headers)

        block: Optional[T1771OutBlock] = None
        block2: list = []

        if exc is None and not is_error:
            block = T1771OutBlock.model_validate(block_data) if block_data is not None else None
            block2 = [T1771OutBlock2.model_validate(r) for r in block2_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t1771 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t1771 request failed: {error_msg}")

        result = T1771Response(
            header=header,
            block=block, block2=block2,
            rsp_cd=resp_json.get('rsp_cd', ''),
            rsp_msg=resp_json.get('rsp_msg', ''),
            status_code=status,
            error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T1771Response:
        return self._generic.req()

    async def req_async(self) -> T1771Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T1771Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)