from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t8405")
from .blocks import (
    T8405RequestHeader,
    T8405ResponseHeader,
    T8405InBlock,
    T8405OutBlock,
    T8405OutBlock1,
    T8405Request,
    T8405Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8405(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t8405 — 주식선물기간별주가(API용)(t8405)"""

    def __init__(self, request_data: T8405Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8405Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8405Response] = GenericTR[T8405Response](
            self.request_data, self._build_response, url=URLS.DOMESTIC_FO_MARKET_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8405Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t8405OutBlock")
        block1_data = resp_json.get("t8405OutBlock1", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8405ResponseHeader.model_validate(resp_headers)

        block: Optional[T8405OutBlock] = None
        block1: list = []

        if exc is None and not is_error:
            block = T8405OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = [T8405OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8405 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8405 request failed: {error_msg}")

        result = T8405Response(
            header=header,
            block=block, block1=block1,
            rsp_cd=resp_json.get('rsp_cd', ''),
            rsp_msg=resp_json.get('rsp_msg', ''),
            status_code=status,
            error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T8405Response:
        return self._generic.req()

    async def req_async(self) -> T8405Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T8405Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)