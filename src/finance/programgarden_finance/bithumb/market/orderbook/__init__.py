"""빗썸 호가 정보 조회 (GET /v1/orderbook) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    OrderbookInBlock,
    OrderbookOutBlock,
    OrderbookRequest,
    OrderbookResponse,
    OrderbookUnit,
)


class TrOrderbook(GenericBithumbTR[OrderbookResponse]):
    """빗썸 호가 정보 조회 TR 클래스입니다."""

    def __init__(self, request_data: OrderbookRequest):
        if not isinstance(request_data, OrderbookRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.ORDERBOOK_URL,
            requires_auth=False,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderbookResponse:
        if exc is not None:
            return OrderbookResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrderbookResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [OrderbookOutBlock.model_validate(item) for item in (data or [])]
        return OrderbookResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrOrderbook,
    OrderbookInBlock,
    OrderbookOutBlock,
    OrderbookRequest,
    OrderbookResponse,
    OrderbookUnit,
]
