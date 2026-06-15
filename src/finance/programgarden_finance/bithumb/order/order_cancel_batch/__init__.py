"""빗썸 다건 주문 취소 (POST /v2/orders/cancel) TR 모듈입니다."""

from typing import Any, Dict, Optional

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    CancelFailError,
    CancelFailItem,
    CancelSuccessItem,
    OrderCancelBatchInBlock,
    OrderCancelBatchOutBlock,
    OrderCancelBatchRequest,
    OrderCancelBatchResponse,
)


def _build_cancel_batch_query_string(
    query_params: Optional[Dict[str, Any]],
    json_body: Optional[Dict[str, Any]],
) -> str:
    """``order_ids[]=value&client_order_ids[]=value`` 형식의 query_hash 원문을 생성합니다.

    빗썸 다건 주문 취소는 ``urlencode(doseq=True)``가 만드는 ``order_ids=a&order_ids=b``
    형식이 아니라, 배열임을 ``[]``로 명시한 문자열을 SHA512 해싱한다.
    """
    json_body = json_body or {}
    parts = []
    for order_id in json_body.get("order_ids", []) or []:
        parts.append(f"order_ids[]={order_id}")
    for client_order_id in json_body.get("client_order_ids", []) or []:
        parts.append(f"client_order_ids[]={client_order_id}")
    return "&".join(parts)


class TrOrderCancelBatch(GenericBithumbTR[OrderCancelBatchResponse]):
    """빗썸 다건 주문 취소 TR 클래스입니다."""

    def __init__(self, request_data: OrderCancelBatchRequest):
        if not isinstance(request_data, OrderCancelBatchRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.ORDER_CANCEL_BATCH_URL,
            requires_auth=True,
            auth_query_string_builder=_build_cancel_batch_query_string,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderCancelBatchResponse:
        if exc is not None:
            return OrderCancelBatchResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrderCancelBatchResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = OrderCancelBatchOutBlock.model_validate(data) if data else None
        return OrderCancelBatchResponse(status_code=status_code, block=block)


__all__ = [
    TrOrderCancelBatch,
    CancelFailError,
    CancelFailItem,
    CancelSuccessItem,
    OrderCancelBatchInBlock,
    OrderCancelBatchOutBlock,
    OrderCancelBatchRequest,
    OrderCancelBatchResponse,
]
