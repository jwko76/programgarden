from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t8412")
from .blocks import (
    T8412RequestHeader,
    T8412ResponseHeader,
    T8412InBlock,
    T8412OutBlock,
    T8412OutBlock1,
    T8412Request,
    T8412Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8412(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t8412 — 주식챠트(N분)(t8412)"""

    def __init__(self, request_data: T8412Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8412Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8412Response] = GenericTR[T8412Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_CHART_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8412Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t8412OutBlock")
        block1_data = resp_json.get("t8412OutBlock1", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8412ResponseHeader.model_validate(resp_headers)

        block: Optional[T8412OutBlock] = None
        block1: list = []

        if exc is None and not is_error:
            block = T8412OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = [T8412OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8412 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8412 request failed: {error_msg}")

        result = T8412Response(
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

    def req(self) -> T8412Response:
        return self._generic.req()

    async def req_async(self) -> T8412Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T8412Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)