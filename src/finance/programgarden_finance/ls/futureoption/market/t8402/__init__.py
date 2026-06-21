from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t8402")
from .blocks import (
    T8402RequestHeader,
    T8402ResponseHeader,
    T8402InBlock,
    T8402OutBlock,
    T8402Request,
    T8402Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8402(TRRequestAbstract):
    """LS증권 OpenAPI t8402 — 주식선물현재가조회(API용)(t8402)"""

    def __init__(self, request_data: T8402Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8402Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8402Response] = GenericTR[T8402Response](
            self.request_data, self._build_response, url=URLS.DOMESTIC_FO_MARKET_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8402Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t8402OutBlock")

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8402ResponseHeader.model_validate(resp_headers)

        block: Optional[T8402OutBlock] = None

        if exc is None and not is_error:
            block = T8402OutBlock.model_validate(block_data) if block_data is not None else None

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8402 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8402 request failed: {error_msg}")

        result = T8402Response(
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

    def req(self) -> T8402Response:
        return self._generic.req()

    async def req_async(self) -> T8402Response:
        return await self._generic.req_async()