"""빗썸 최근 체결 내역 조회 (GET /v1/trades/ticks) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    TradesTicksInBlock,
    TradesTicksOutBlock,
    TradesTicksRequest,
    TradesTicksResponse,
)


class TrTradesTicks(GenericBithumbTR[TradesTicksResponse]):
    """빗썸 최근 체결 내역 조회 TR 클래스입니다."""

    def __init__(self, request_data: TradesTicksRequest):
        if not isinstance(request_data, TradesTicksRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.TRADES_TICKS_URL,
            requires_auth=False,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> TradesTicksResponse:
        if exc is not None:
            return TradesTicksResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return TradesTicksResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [TradesTicksOutBlock.model_validate(item) for item in (data or [])]
        return TradesTicksResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrTradesTicks,
    TradesTicksInBlock,
    TradesTicksOutBlock,
    TradesTicksRequest,
    TradesTicksResponse,
]
