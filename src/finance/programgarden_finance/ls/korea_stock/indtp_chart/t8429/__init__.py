from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.korea_stock.indtp_chart.t8429")
from .blocks import (
    T8429InBlock, T8429OutBlock, T8429OutBlock1,
    T8429Request, T8429Response, T8429ResponseHeader,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8429(TRRequestAbstract, OccursReqAbstract):
    """LS증권 OpenAPI t8429 (API용)업종차트(일/주/월) — 업종 지수 일/주/월봉 차트."""

    def __init__(self, request_data: T8429Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8429Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8429Response] = GenericTR[T8429Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_INDTP_CHART_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8429Response:
        resp_json = resp_json or {}
        block_data  = resp_json.get("t8429OutBlock")
        block1_data = resp_json.get("t8429OutBlock1", [])

        status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8429ResponseHeader.model_validate(resp_headers)

        block: Optional[T8429OutBlock] = None
        block1: list[T8429OutBlock1] = []
        if exc is None and not is_error:
            if block_data is not None:
                block = T8429OutBlock.model_validate(block_data)
            block1 = [T8429OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8429 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get("rsp_msg"):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8429 request failed: {error_msg}")

        result = T8429Response(
            header=header, block=block, block1=block1,
            rsp_cd=resp_json.get("rsp_cd", ""), rsp_msg=resp_json.get("rsp_msg", ""),
            status_code=status, error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T8429Response:
        return self._generic.req()

    async def req_async(self) -> T8429Response:
        return await self._generic.req_async()

    async def _req_async_with_session(self, session: aiohttp.ClientSession) -> T8429Response:
        if hasattr(self._generic, "_req_async_with_session"):
            return await self._generic._req_async_with_session(session)
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback: Optional[Callable[[Optional[T8429Response], RequestStatus], None]] = None,
        delay: int = 1,
    ) -> list[T8429Response]:
        def _updater(req_data, resp: T8429Response):
            if resp.header is None or resp.block is None:
                raise ValueError("t8429 response missing continuation data")
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
            req_data.body["t8429InBlock"]["cts_date"] = resp.block.cts_date
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)

    async def occurs_req_async(
        self,
        callback: Optional[Callable[[Optional[T8429Response], RequestStatus], None]] = None,
        delay: int = 1,
    ) -> list[T8429Response]:
        def _updater(req_data, resp: T8429Response):
            if resp.header is None or resp.block is None:
                raise ValueError("t8429 response missing continuation data")
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
            req_data.body["t8429InBlock"]["cts_date"] = resp.block.cts_date
        return await self._generic.occurs_req_async(_updater, callback=callback, delay=delay)
