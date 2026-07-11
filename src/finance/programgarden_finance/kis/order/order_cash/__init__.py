"""KIS 주식주문(현금) TR 모듈입니다.

매수/매도의 tr_id가 다릅니다:
- 매수: 실전 TTTC0802U / 모의 VTTC0802U
- 매도: 실전 TTTC0801U / 모의 VTTC0801U
"""

from typing import Literal

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    OrderCashBodyBlock,
    OrderCashOutBlock,
    OrderCashRequest,
    OrderCashResponse,
)


class TrOrderCash(GenericKisTR[OrderCashResponse]):
    """KIS 주식주문(현금) TR 클래스입니다."""

    def __init__(self, request_data: OrderCashRequest, side: Literal["buy", "sell"]):
        if not isinstance(request_data, OrderCashRequest):
            raise TrRequestDataNotFoundException()
        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'")

        self.side = side
        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url_path=URLS.ORDER_CASH_PATH,
            tr_id=TR_IDS.ORDER_CASH_BUY if side == "buy" else TR_IDS.ORDER_CASH_SELL,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderCashResponse:
        if exc is not None:
            return OrderCashResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return OrderCashResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        block = OrderCashOutBlock.model_validate(outputs.get("output") or {})
        return OrderCashResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1, block=block,
        )


__all__ = [
    TrOrderCash,
    OrderCashBodyBlock,
    OrderCashOutBlock,
    OrderCashRequest,
    OrderCashResponse,
]
