"""빗썸 주문 가능 정보 조회 (GET /v1/orders/chance) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    OrdersChanceAccount,
    OrdersChanceInBlock,
    OrdersChanceMarketInfo,
    OrdersChanceMarketSide,
    OrdersChanceOutBlock,
    OrdersChanceRequest,
    OrdersChanceResponse,
)


class TrOrdersChance(GenericBithumbTR[OrdersChanceResponse]):
    """빗썸 주문 가능 정보 조회 TR 클래스입니다."""

    def __init__(self, request_data: OrdersChanceRequest):
        if not isinstance(request_data, OrdersChanceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.ORDERS_CHANCE_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrdersChanceResponse:
        if exc is not None:
            return OrdersChanceResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrdersChanceResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = OrdersChanceOutBlock.model_validate(data) if data else None
        return OrdersChanceResponse(status_code=status_code, block=block)


__all__ = [
    TrOrdersChance,
    OrdersChanceAccount,
    OrdersChanceInBlock,
    OrdersChanceMarketInfo,
    OrdersChanceMarketSide,
    OrdersChanceOutBlock,
    OrdersChanceRequest,
    OrdersChanceResponse,
]
