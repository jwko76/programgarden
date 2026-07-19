"""키움증권 주식 현금매수/매도 TR 모듈입니다.

매수/매도는 api-id가 다릅니다:
- 매수: kt10000
- 매도: kt10001
"""

from typing import Literal

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    OrderCashBodyBlock,
    OrderCashOutBlock,
    OrderCashRequest,
    OrderCashResponse,
)


class TrOrderCash(GenericKiwoomTR[OrderCashResponse]):
    """키움 주식 현금매수/매도 TR 클래스입니다."""

    def __init__(self, request_data: OrderCashRequest, side: Literal["buy", "sell"]):
        if not isinstance(request_data, OrderCashRequest):
            raise TrRequestDataNotFoundException()
        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'")

        self.side = side
        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.ORDR_PATH,
            tr_id=TR_IDS.ORDER_CASH_BUY if side == "buy" else TR_IDS.ORDER_CASH_SELL,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderCashResponse:
        if exc is not None:
            return OrderCashResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return OrderCashResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        block = OrderCashOutBlock.model_validate(data)
        return OrderCashResponse(
            status_code=status, return_code=return_code, return_msg=return_msg, block=block,
        )


__all__ = [
    TrOrderCash,
    OrderCashBodyBlock,
    OrderCashOutBlock,
    OrderCashRequest,
    OrderCashResponse,
]
