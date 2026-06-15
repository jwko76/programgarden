"""빗썸 개별 주문 조회 (GET /v1/order) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    OrderDetailInBlock,
    OrderDetailOutBlock,
    OrderDetailRequest,
    OrderDetailResponse,
)


class TrOrderDetail(GenericBithumbTR[OrderDetailResponse]):
    """빗썸 개별 주문 조회 TR 클래스입니다."""

    def __init__(self, request_data: OrderDetailRequest):
        if not isinstance(request_data, OrderDetailRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.ORDER_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderDetailResponse:
        if exc is not None:
            return OrderDetailResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrderDetailResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = OrderDetailOutBlock.model_validate(data) if data else None
        return OrderDetailResponse(status_code=status_code, block=block)


__all__ = [
    TrOrderDetail,
    OrderDetailInBlock,
    OrderDetailOutBlock,
    OrderDetailRequest,
    OrderDetailResponse,
]
