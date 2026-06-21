from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.t1958")
from .blocks import (
    T1958RequestHeader,
    T1958ResponseHeader,
    T1958InBlock,
    T1958OutBlock,
    T1958OutBlock1,
    T1958OutBlock2,
    T1958Request,
    T1958Response,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT1958(TRRequestAbstract):
    """LS증권 OpenAPI t1958 — ELW종목비교(t1958)"""

    def __init__(self, request_data: T1958Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T1958Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T1958Response] = GenericTR[T1958Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_ELW_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T1958Response:
        resp_json = resp_json or {}
        block_data = resp_json.get("t1958OutBlock")
        block1_data = resp_json.get("t1958OutBlock1")
        block2_data = resp_json.get("t1958OutBlock2")

        status = getattr(resp, 'status', getattr(resp, 'status_code', None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T1958ResponseHeader.model_validate(resp_headers)

        block: Optional[T1958OutBlock] = None
        block1: Optional[T1958OutBlock1] = None
        block2: Optional[T1958OutBlock2] = None

        if exc is None and not is_error:
            block = T1958OutBlock.model_validate(block_data) if block_data is not None else None
            block1 = T1958OutBlock1.model_validate(block1_data) if block1_data is not None else None
            block2 = T1958OutBlock2.model_validate(block2_data) if block2_data is not None else None

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t1958 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get('rsp_msg'):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t1958 request failed: {error_msg}")

        result = T1958Response(
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

    def req(self) -> T1958Response:
        return self._generic.req()

    async def req_async(self) -> T1958Response:
        return await self._generic.req_async()