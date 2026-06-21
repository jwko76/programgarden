from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t2541")
from .blocks import (
    T2541RequestHeader,
    T2541ResponseHeader,
    T2541InBlock,
    T2541OutBlock,
    T2541OutBlock1,
    T2541Request,
    T2541Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT2541(OccursReqAbstract, TRRequestAbstract):
    """LS증권 OpenAPI t2541 — 상품선물투자자매매동향(실시간)(t2541)"""

    def __init__(self, request_data: T2541Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T2541Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T2541Response] = GenericTR[T2541Response](
            self.request_data, self._build_response, url=URLS.DOMESTIC_FO_INVESTOR_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T2541Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t2541OutBlock")
        block1_data = resp_json.get("t2541OutBlock1", [])

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T2541ResponseHeader.model_validate(resp_headers)

        block: Optional[T2541OutBlock] = None
        block1: list = []

        if exc is None and not is_error:
            block = T2541OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = [T2541OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t2541 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t2541 request failed: {error_msg}")

        result = T2541Response(
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

    def req(self) -> T2541Response:
        return self._generic.req()

    async def req_async(self) -> T2541Response:
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback=None,
        delay: int = 1,
    ) -> list[T2541Response]:
        def _updater(req_data, resp):
            if resp.header is None:
                raise ValueError('missing continuation data')
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)