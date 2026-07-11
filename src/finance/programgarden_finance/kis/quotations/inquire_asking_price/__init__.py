"""KIS 주식현재가 호가/예상체결 (FHKST01010200) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    InquireAskingPriceInBlock,
    InquireAskingPriceOutBlock1,
    InquireAskingPriceOutBlock2,
    InquireAskingPriceRequest,
    InquireAskingPriceResponse,
)


class TrInquireAskingPrice(GenericKisTR[InquireAskingPriceResponse]):
    """KIS 주식현재가 호가/예상체결 TR 클래스입니다."""

    def __init__(self, request_data: InquireAskingPriceRequest):
        if not isinstance(request_data, InquireAskingPriceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_path=URLS.INQUIRE_ASKING_PRICE_PATH,
            tr_id=TR_IDS.INQUIRE_ASKING_PRICE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquireAskingPriceResponse:
        if exc is not None:
            return InquireAskingPriceResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return InquireAskingPriceResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        block1 = InquireAskingPriceOutBlock1.model_validate(outputs.get("output1") or {})
        block2 = InquireAskingPriceOutBlock2.model_validate(outputs.get("output2") or {})
        return InquireAskingPriceResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
            block1=block1, block2=block2,
        )


__all__ = [
    TrInquireAskingPrice,
    InquireAskingPriceInBlock,
    InquireAskingPriceOutBlock1,
    InquireAskingPriceOutBlock2,
    InquireAskingPriceRequest,
    InquireAskingPriceResponse,
]
