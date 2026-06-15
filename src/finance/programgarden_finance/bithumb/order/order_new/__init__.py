"""빗썸 주문하기 (POST /v2/orders) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    OrderNewInBlock,
    OrderNewOutBlock,
    OrderNewRequest,
    OrderNewResponse,
)


class TrOrderNew(GenericBithumbTR[OrderNewResponse]):
    """빗썸 주문하기 TR 클래스입니다."""

    def __init__(self, request_data: OrderNewRequest):
        if not isinstance(request_data, OrderNewRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.ORDER_NEW_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderNewResponse:
        if exc is not None:
            return OrderNewResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrderNewResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = OrderNewOutBlock.model_validate(data) if data else None
        return OrderNewResponse(status_code=status_code, block=block)


__all__ = [
    TrOrderNew,
    OrderNewInBlock,
    OrderNewOutBlock,
    OrderNewRequest,
    OrderNewResponse,
]
