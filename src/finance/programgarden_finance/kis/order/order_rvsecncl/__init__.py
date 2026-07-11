"""KIS 주식주문(정정취소) (TTTC0803U/VTTC0803U) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    OrderRvsecnclBodyBlock,
    OrderRvsecnclOutBlock,
    OrderRvsecnclRequest,
    OrderRvsecnclResponse,
)


class TrOrderRvsecncl(GenericKisTR[OrderRvsecnclResponse]):
    """KIS 주식주문(정정취소) TR 클래스입니다. 실전 TTTC0803U / 모의 VTTC0803U."""

    def __init__(self, request_data: OrderRvsecnclRequest):
        if not isinstance(request_data, OrderRvsecnclRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url_path=URLS.ORDER_RVSECNCL_PATH,
            tr_id=TR_IDS.ORDER_RVSECNCL,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> OrderRvsecnclResponse:
        if exc is not None:
            return OrderRvsecnclResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return OrderRvsecnclResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        block = OrderRvsecnclOutBlock.model_validate(outputs.get("output") or {})
        return OrderRvsecnclResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1, block=block,
        )


__all__ = [
    TrOrderRvsecncl,
    OrderRvsecnclBodyBlock,
    OrderRvsecnclOutBlock,
    OrderRvsecnclRequest,
    OrderRvsecnclResponse,
]
