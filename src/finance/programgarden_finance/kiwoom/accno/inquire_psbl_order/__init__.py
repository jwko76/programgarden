"""키움증권 주문인출가능금액요청 (kt00010) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    InquirePsblOrderInBlock,
    InquirePsblOrderOutBlock,
    InquirePsblOrderRequest,
    InquirePsblOrderResponse,
)


class TrInquirePsblOrder(GenericKiwoomTR[InquirePsblOrderResponse]):
    """키움 주문인출가능금액요청 TR 클래스입니다. api-id: kt00010."""

    def __init__(self, request_data: InquirePsblOrderRequest):
        if not isinstance(request_data, InquirePsblOrderRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.ACNT_PATH,
            tr_id=TR_IDS.INQUIRE_PSBL_ORDER,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquirePsblOrderResponse:
        if exc is not None:
            return InquirePsblOrderResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return InquirePsblOrderResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        block = InquirePsblOrderOutBlock.model_validate(data)
        return InquirePsblOrderResponse(
            status_code=status, return_code=return_code, return_msg=return_msg, block=block,
        )


__all__ = [
    TrInquirePsblOrder,
    InquirePsblOrderInBlock,
    InquirePsblOrderOutBlock,
    InquirePsblOrderRequest,
    InquirePsblOrderResponse,
]
