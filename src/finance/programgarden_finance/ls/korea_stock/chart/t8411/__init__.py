from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t8411")
from .blocks import (
    T8411RequestHeader,
    T8411ResponseHeader,
    T8411InBlock,
    T8411OutBlock,
    T8411OutBlock1,
    T8411Request,
    T8411Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8411(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t8411 — 주식챠트(틱/n틱)(t8411)"""

    def __init__(self, request_data: T8411Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8411Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8411Response] = GenericTR[T8411Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_CHART_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8411Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t8411OutBlock")
        block1_data = resp_json.get("t8411OutBlock1", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8411ResponseHeader.model_validate(resp_headers)

        block: Optional[T8411OutBlock] = None
        block1: list = []

        if exc is None and not is_error:
            block = T8411OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = [T8411OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8411 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8411 request failed: {error_msg}")

        result = T8411Response(
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

    def req(self) -> T8411Response:
        return self._generic.req()

    async def req_async(self) -> T8411Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T8411Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)