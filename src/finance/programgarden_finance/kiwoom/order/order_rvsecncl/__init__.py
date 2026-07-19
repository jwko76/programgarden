"""키움증권 주식 정정/취소 TR 모듈입니다.

정정/취소는 api-id가 다릅니다:
- 정정: kt10002
- 취소: kt10003
"""

from typing import Literal

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    OrderRvsecnclBodyBlock,
    OrderRvsecnclOutBlock,
    OrderRvsecnclRequest,
    OrderRvsecnclResponse,
)


class TrOrderRvsecncl(GenericKiwoomTR[OrderRvsecnclResponse]):
    """키움 주식 정정/취소 TR 클래스입니다."""

    def __init__(self, request_data: OrderRvsecnclRequest, mode: Literal["modify", "cancel"]):
        if not isinstance(request_data, OrderRvsecnclRequest):
            raise TrRequestDataNotFoundException()
        if mode not in ("modify", "cancel"):
            raise ValueError("mode must be 'modify' or 'cancel'")

        self.mode = mode
        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.ORDR_PATH,
            tr_id=TR_IDS.ORDER_MODIFY if mode == "modify" else TR_IDS.ORDER_CANCEL,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderRvsecnclResponse:
        if exc is not None:
            return OrderRvsecnclResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return OrderRvsecnclResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        block = OrderRvsecnclOutBlock.model_validate(data)
        return OrderRvsecnclResponse(
            status_code=status, return_code=return_code, return_msg=return_msg, block=block,
        )


__all__ = [
    TrOrderRvsecncl,
    OrderRvsecnclBodyBlock,
    OrderRvsecnclOutBlock,
    OrderRvsecnclRequest,
    OrderRvsecnclResponse,
]
