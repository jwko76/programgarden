"""빗썸 주문 취소 (DELETE /v2/order) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    OrderCancelInBlock,
    OrderCancelOutBlock,
    OrderCancelRequest,
    OrderCancelResponse,
)


class TrOrderCancel(GenericBithumbTR[OrderCancelResponse]):
    """빗썸 주문 취소 TR 클래스입니다."""

    def __init__(self, request_data: OrderCancelRequest):
        if not isinstance(request_data, OrderCancelRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="DELETE",
            url=URLS.ORDER_CANCEL_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderCancelResponse:
        if exc is not None:
            return OrderCancelResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrderCancelResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = OrderCancelOutBlock.model_validate(data) if data else None
        return OrderCancelResponse(status_code=status_code, block=block)


__all__ = [
    TrOrderCancel,
    OrderCancelInBlock,
    OrderCancelOutBlock,
    OrderCancelRequest,
    OrderCancelResponse,
]
