"""키움증권 종목기본정보요청 (ka10001) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    InquirePriceInBlock,
    InquirePriceOutBlock,
    InquirePriceRequest,
    InquirePriceResponse,
)


class TrInquirePrice(GenericKiwoomTR[InquirePriceResponse]):
    """키움 종목기본정보요청 TR 클래스입니다. api-id: ka10001."""

    def __init__(self, request_data: InquirePriceRequest):
        if not isinstance(request_data, InquirePriceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.STKINFO_PATH,
            tr_id=TR_IDS.INQUIRE_PRICE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquirePriceResponse:
        if exc is not None:
            return InquirePriceResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return InquirePriceResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        block = InquirePriceOutBlock.model_validate(data)
        return InquirePriceResponse(
            status_code=status, return_code=return_code, return_msg=return_msg, block=block,
        )


__all__ = [
    TrInquirePrice,
    InquirePriceInBlock,
    InquirePriceOutBlock,
    InquirePriceRequest,
    InquirePriceResponse,
]
