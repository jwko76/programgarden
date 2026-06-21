from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t4203")
from .blocks import (
    T4203RequestHeader,
    T4203ResponseHeader,
    T4203InBlock,
    T4203OutBlock,
    T4203OutBlock1,
    T4203Request,
    T4203Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT4203(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t4203 — 업종챠트(종합)(t4203)"""

    def __init__(self, request_data: T4203Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T4203Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T4203Response] = GenericTR[T4203Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_INDTP_CHART_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T4203Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t4203OutBlock")
        block1_data = resp_json.get("t4203OutBlock1", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T4203ResponseHeader.model_validate(resp_headers)

        block: Optional[T4203OutBlock] = None
        block1: list = []

        if exc is None and not is_error:
            block = T4203OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = [T4203OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t4203 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t4203 request failed: {error_msg}")

        result = T4203Response(
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

    def req(self) -> T4203Response:
        return self._generic.req()

    async def req_async(self) -> T4203Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T4203Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)