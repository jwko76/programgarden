"""KIS 주식현재가 시세 (FHKST01010100) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    InquirePriceInBlock,
    InquirePriceOutBlock,
    InquirePriceRequest,
    InquirePriceResponse,
)


class TrInquirePrice(GenericKisTR[InquirePriceResponse]):
    """KIS 주식현재가 시세 TR 클래스입니다."""

    def __init__(self, request_data: InquirePriceRequest):
        if not isinstance(request_data, InquirePriceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_path=URLS.INQUIRE_PRICE_PATH,
            tr_id=TR_IDS.INQUIRE_PRICE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquirePriceResponse:
        if exc is not None:
            return InquirePriceResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return InquirePriceResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        block = InquirePriceOutBlock.model_validate(outputs.get("output") or {})
        return InquirePriceResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1, block=block,
        )


__all__ = [
    TrInquirePrice,
    InquirePriceInBlock,
    InquirePriceOutBlock,
    InquirePriceRequest,
    InquirePriceResponse,
]
