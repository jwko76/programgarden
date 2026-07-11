"""KIS 매수가능조회 (TTTC8908R/VTTC8908R) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    InquirePsblOrderInBlock,
    InquirePsblOrderOutBlock,
    InquirePsblOrderRequest,
    InquirePsblOrderResponse,
)


class TrInquirePsblOrder(GenericKisTR[InquirePsblOrderResponse]):
    """KIS 매수가능조회 TR 클래스입니다. 실전 TTTC8908R / 모의 VTTC8908R."""

    def __init__(self, request_data: InquirePsblOrderRequest):
        if not isinstance(request_data, InquirePsblOrderRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_path=URLS.INQUIRE_PSBL_ORDER_PATH,
            tr_id=TR_IDS.INQUIRE_PSBL_ORDER,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquirePsblOrderResponse:
        if exc is not None:
            return InquirePsblOrderResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return InquirePsblOrderResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        block = InquirePsblOrderOutBlock.model_validate(outputs.get("output") or {})
        return InquirePsblOrderResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1, block=block,
        )


__all__ = [
    TrInquirePsblOrder,
    InquirePsblOrderInBlock,
    InquirePsblOrderOutBlock,
    InquirePsblOrderRequest,
    InquirePsblOrderResponse,
]
