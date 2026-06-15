"""빗썸 현재가 조회 (GET /v1/ticker) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    TickerInBlock,
    TickerOutBlock,
    TickerRequest,
    TickerResponse,
)


class TrTicker(GenericBithumbTR[TickerResponse]):
    """빗썸 현재가 조회 TR 클래스입니다."""

    def __init__(self, request_data: TickerRequest):
        if not isinstance(request_data, TickerRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.TICKER_URL,
            requires_auth=False,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> TickerResponse:
        if exc is not None:
            return TickerResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return TickerResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [TickerOutBlock.model_validate(item) for item in (data or [])]
        return TickerResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrTicker,
    TickerInBlock,
    TickerOutBlock,
    TickerRequest,
    TickerResponse,
]
