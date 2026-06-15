"""빗썸 주문 리스트 조회 (GET /v1/orders) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    OrdersInBlock,
    OrdersOutBlock,
    OrdersRequest,
    OrdersResponse,
    OrderState,
)


class TrOrders(GenericBithumbTR[OrdersResponse]):
    """빗썸 주문 리스트 조회 TR 클래스입니다."""

    def __init__(self, request_data: OrdersRequest):
        if not isinstance(request_data, OrdersRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.ORDERS_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrdersResponse:
        if exc is not None:
            return OrdersResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrdersResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [OrdersOutBlock.model_validate(item) for item in (data or [])]
        return OrdersResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrOrders,
    OrdersInBlock,
    OrdersOutBlock,
    OrdersRequest,
    OrdersResponse,
    OrderState,
]
