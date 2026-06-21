from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t2301")
from .blocks import (
    T2301RequestHeader,
    T2301ResponseHeader,
    T2301InBlock,
    T2301OutBlock,
    T2301OutBlock1,
    T2301OutBlock2,
    T2301Request,
    T2301Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT2301(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t2301 — 옵션전광판(t2301)"""

    def __init__(self, request_data: T2301Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T2301Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T2301Response] = GenericTR[T2301Response](
            self.request_data, self._build_response, url=URLS.DOMESTIC_FO_MARKET_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T2301Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t2301OutBlock")
        block1_data = resp_json.get("t2301OutBlock1", [])
        block2_data = resp_json.get("t2301OutBlock2", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T2301ResponseHeader.model_validate(resp_headers)

        block: Optional[T2301OutBlock] = None
        block1: list = []
        block2: list = []

        if exc is None and not is_error:
            block = T2301OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = [T2301OutBlock1.model_validate(r) for r in block1_data]
            block2 = [T2301OutBlock2.model_validate(r) for r in block2_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t2301 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t2301 request failed: {error_msg}")

        result = T2301Response(
            header=header,
            block=block, block1=block1, block2=block2,
            rsp_cd=resp_json.get('rsp_cd', ''),
            rsp_msg=resp_json.get('rsp_msg', ''),
            status_code=status,
            error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T2301Response:
        return self._generic.req()

    async def req_async(self) -> T2301Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T2301Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)