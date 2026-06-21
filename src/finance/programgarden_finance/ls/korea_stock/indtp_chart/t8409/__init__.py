from typing import Callable, Optional, Dict, Any

import aiohttp

from programgarden_core.exceptions import TrRequestDataNotFoundException
import logging

logger = logging.getLogger("programgarden.ls.korea_stock.indtp_chart.t8409")
from .blocks import (
    T8409InBlock, T8409OutBlock, T8409OutBlock1,
    T8409Request, T8409Response, T8409ResponseHeader,
)
from ....tr_base import OccursReqAbstract, TRRequestAbstract
from ....tr_helpers import GenericTR
from programgarden_finance.ls.config import URLS
from programgarden_finance.ls.status import RequestStatus


class TrT8409(TRRequestAbstract, OccursReqAbstract):
    """LS증권 OpenAPI t8409 (API용)업종차트(분) — 업종 지수 분봉 차트."""

    def __init__(self, request_data: T8409Request):
        super().__init__(
            rate_limit_count=request_data.options.rate_limit_count,
            rate_limit_seconds=request_data.options.rate_limit_seconds,
            on_rate_limit=request_data.options.on_rate_limit,
            rate_limit_key=request_data.options.rate_limit_key,
        )
        self.request_data = request_data
        if not isinstance(self.request_data, T8409Request):
            raise TrRequestDataNotFoundException()
        self._generic: GenericTR[T8409Response] = GenericTR[T8409Response](
            self.request_data, self._build_response, url=URLS.KOREA_STOCK_INDTP_CHART_URL
        )

    def _build_response(
        self,
        resp: Optional[object],
        resp_json: Optional[Dict[str, Any]],
        resp_headers: Optional[Dict[str, Any]],
        exc: Optional[Exception],
    ) -> T8409Response:
        resp_json = resp_json or {}
        block_data  = resp_json.get("t8409OutBlock")
        block1_data = resp_json.get("t8409OutBlock1", [])

        status = getattr(resp, "status", getattr(resp, "status_code", None)) if resp is not None else None
        is_error = status is not None and status >= 400

        header = None
        if exc is None and resp_headers and not is_error:
            header = T8409ResponseHeader.model_validate(resp_headers)

        block: Optional[T8409OutBlock] = None
        block1: list[T8409OutBlock1] = []
        if exc is None and not is_error:
            if block_data is not None:
                block = T8409OutBlock.model_validate(block_data)
            block1 = [T8409OutBlock1.model_validate(r) for r in block1_data]

        error_msg: Optional[str] = None
        if exc is not None:
            error_msg = str(exc)
            logger.error(f"t8409 request failed: {exc}")
        elif is_error:
            error_msg = f"HTTP {status}"
            if resp_json.get("rsp_msg"):
                error_msg = f"{error_msg}: {resp_json['rsp_msg']}"
            logger.error(f"t8409 request failed: {error_msg}")

        result = T8409Response(
            header=header, block=block, block1=block1,
            rsp_cd=resp_json.get("rsp_cd", ""), rsp_msg=resp_json.get("rsp_msg", ""),
            status_code=status, error_msg=error_msg,
        )
        if resp is not None:
            result.raw_data = resp
        return result

    def req(self) -> T8409Response:
        return self._generic.req()

    async def req_async(self) -> T8409Response:
        return await self._generic.req_async()

    async def _req_async_with_session(self, session: aiohttp.ClientSession) -> T8409Response:
        if hasattr(self._generic, "_req_async_with_session"):
            return await self._generic._req_async_with_session(session)
        return await self._generic.req_async()

    def occurs_req(
        self,
        callback: Optional[Callable[[Optional[T8409Response], RequestStatus], None]] = None,
        delay: int = 1,
    ) -> list[T8409Response]:
        def _updater(req_data, resp: T8409Response):
            if resp.header is None or resp.block is None:
                raise ValueError("t8409 response missing continuation data")
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
            req_data.body["t8409InBlock"]["cts_date"] = resp.block.cts_date
            req_data.body["t8409InBlock"]["cts_time"] = resp.block.cts_time
        return self._generic.occurs_req(_updater, callback=callback, delay=delay)

    async def occurs_req_async(
        self,
        callback: Optional[Callable[[Optional[T8409Response], RequestStatus], None]] = None,
        delay: int = 1,
    ) -> list[T8409Response]:
        def _updater(req_data, resp: T8409Response):
            if resp.header is None or resp.block is None:
                raise ValueError("t8409 response missing continuation data")
            req_data.header.tr_cont_key = resp.header.tr_cont_key
            req_data.header.tr_cont = resp.header.tr_cont
            req_data.body["t8409InBlock"]["cts_date"] = resp.block.cts_date
            req_data.body["t8409InBlock"]["cts_time"] = resp.block.cts_time
        return await self._generic.occurs_req_async(_updater, callback=callback, delay=delay)
