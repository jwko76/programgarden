from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.korea_stock.indtp_chart.t8408")
from .blocks import (
    T8408InBlock, T8408OutBlock, T8408OutBlock1,
    T8408Request, T8408Response, T8408ResponseHeader,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8408(TRRequestAbstract, OccursReqAbstract):
    """LS증권 OpenAPI t8408 (API용)업종차트(틱/n틱) — 업종 지수 틱 차트."""

    def __init__(self, request_data: T8408Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8408Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8408Response] = GenericTR[T8408Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_INDTP_CHART_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8408Response:
        resp_json = resp_json or {}
        block_data  = resp_json.get("t8408OutBlock")
        block1_data = resp_json.get("t8408OutBlock1", [])

        status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8408ResponseHeader.model_validate(resp_headers)

        block: Optional[T8408OutBlock] = None
        block1: list[T8408OutBlock1] = []
        if exc is None and not is_error:
            if block_data is not None:
                block = T8408OutBlock.model_validate(block_data)
            block1 = [T8408OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8408 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get("rsp_msg"):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8408 request failed: {error_msg}")

        result = T8408Response(
            header=header, block=block, block1=block1,
            rsp_cd=resp_json.get("rsp_cd", ""), rsp_msg=resp_json.get("rsp_msg", ""),
            status_code=status, error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T8408Response:
        return self._generic.req()

    async def req_async(self) -> T8408Response:
        return await self._generic.req_async()

    async def _req_async_with_session(self, session: aiohttp.ClientSession) -> T8408Response:
        if hasattr(self._generic, "_req_async_with_session"):
            return await self._generic._req_async_with_session(session)
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback: Optional[Callable[[Optional[T8408Response], RequestStatus], None]] = None,
        delay: int = 1,
    ) -> list[T8408Response]:
        def _updater(req_data, resp: T8408Response):
            if resp.header is None or resp.block is None:
                raise ValueError("t8408 response missing continuation data")
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
            req_data.body["t8408InBlock"]["cts_date"] = resp.block.cts_date
            req_data.body["t8408InBlock"]["cts_time"] = resp.block.cts_time
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)

    async def occurs_req_async(
        self,
        callback: Optional[Callable[[Optional[T8408Response], RequestStatus], None]] = None,
        delay: int = 1,
    ) -> list[T8408Response]:
        def _updater(req_data, resp: T8408Response):
            if resp.header is None or resp.block is None:
                raise ValueError("t8408 response missing continuation data")
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
            req_data.body["t8408InBlock"]["cts_date"] = resp.block.cts_date
            req_data.body["t8408InBlock"]["cts_time"] = resp.block.cts_time
        return await self._generic.occurs_req_async(_updater, callback=callback, delay=delay)
