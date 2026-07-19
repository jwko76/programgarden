"""키움증권 주식호가요청 (ka10004) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    InquireAskingPriceInBlock,
    InquireAskingPriceOutBlock,
    InquireAskingPriceRequest,
    InquireAskingPriceResponse,
)


class TrInquireAskingPrice(GenericKiwoomTR[InquireAskingPriceResponse]):
    """키움 주식호가요청 TR 클래스입니다. api-id: ka10004."""

    def __init__(self, request_data: InquireAskingPriceRequest):
        if not isinstance(request_data, InquireAskingPriceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.MRKCOND_PATH,
            tr_id=TR_IDS.INQUIRE_ASKING_PRICE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquireAskingPriceResponse:
        if exc is not None:
            return InquireAskingPriceResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return InquireAskingPriceResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        block = InquireAskingPriceOutBlock.model_validate(data)
        return InquireAskingPriceResponse(
            status_code=status, return_code=return_code, return_msg=return_msg, block=block,
        )


__all__ = [
    TrInquireAskingPrice,
    InquireAskingPriceInBlock,
    InquireAskingPriceOutBlock,
    InquireAskingPriceRequest,
    InquireAskingPriceResponse,
]
