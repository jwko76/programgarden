"""빗썸 다건 주문 (POST /v2/orders/batch) TR 모듈입니다."""

from typing import Any, Dict, Optional

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    BatchOrderItem,
    BatchOrderResultItem,
    OrderNewBatchInBlock,
    OrderNewBatchOutBlock,
    OrderNewBatchRequest,
    OrderNewBatchResponse,
)


def _build_batch_orders_query_string(
    query_params: Optional[Dict[str, Any]],
    json_body: Optional[Dict[str, Any]],
) -> str:
    """``batch_orders[i][key]=value`` 형식의 query_hash 원문을 생성합니다.

    빗썸 다건 주문은 ``urlencode(doseq=True)``로 직렬화한 문자열이 아니라, batch_orders
    배열의 각 주문 객체를 인덱스 기반 bracket 표기로 평탄화한 문자열을 SHA512 해싱한다.
    """
    batch_orders = (json_body or {}).get("batch_orders", [])
    parts = []
    for index, order in enumerate(batch_orders):
        for key, value in order.items():
            parts.append(f"batch_orders[{index}][{key}]={value}")
    return "&".join(parts)


class TrOrderNewBatch(GenericBithumbTR[OrderNewBatchResponse]):
    """빗썸 다건 주문 TR 클래스입니다."""

    def __init__(self, request_data: OrderNewBatchRequest):
        if not isinstance(request_data, OrderNewBatchRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.ORDER_NEW_BATCH_URL,
            requires_auth=True,
            auth_query_string_builder=_build_batch_orders_query_string,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderNewBatchResponse:
        if exc is not None:
            return OrderNewBatchResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return OrderNewBatchResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = OrderNewBatchOutBlock.model_validate(data) if data else None
        return OrderNewBatchResponse(status_code=status_code, block=block)


__all__ = [
    TrOrderNewBatch,
    BatchOrderItem,
    BatchOrderResultItem,
    OrderNewBatchInBlock,
    OrderNewBatchOutBlock,
    OrderNewBatchRequest,
    OrderNewBatchResponse,
]
