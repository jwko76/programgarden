from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t2210")
from .blocks import (
    T2210RequestHeader,
    T2210ResponseHeader,
    T2210InBlock,
    T2210OutBlock,
    T2210Request,
    T2210Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT2210(TRRequestAbstract):
    """LS증권 OpenAPI t2210 — 선물옵션시간대별체결조회(단일출력용)"""

    def __init__(self, request_data: T2210Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T2210Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T2210Response] = GenericTR[T2210Response](
            self.request_data, self._build_response, url=URLS.DOMESTIC_FO_MARKET_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T2210Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t2210OutBlock")

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T2210ResponseHeader.model_validate(resp_headers)

        block: Optional[T2210OutBlock] = None

        if exc is None and not is_error:
            block = T2210OutBlock.model_validate(block_data) if block_data is not None else None

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t2210 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t2210 request failed: {error_msg}")

        result = T2210Response(
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

    def req(self) -> T2210Response:
        return self._generic.req()

    async def req_async(self) -> T2210Response:
        return await self._generic.req_async()