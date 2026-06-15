"""빗썸 TWAP 주문 등록 (POST /v1/twap) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    TwapNewInBlock,
    TwapNewOutBlock,
    TwapNewRequest,
    TwapNewResponse,
)


class TrTwapNew(GenericBithumbTR[TwapNewResponse]):
    """빗썸 TWAP 주문 등록 TR 클래스입니다."""

    def __init__(self, request_data: TwapNewRequest):
        if not isinstance(request_data, TwapNewRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.TWAP_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> TwapNewResponse:
        if exc is not None:
            return TwapNewResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return TwapNewResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = TwapNewOutBlock.model_validate(data) if data else None
        return TwapNewResponse(status_code=status_code, block=block)


__all__ = [
    TrTwapNew,
    TwapNewInBlock,
    TwapNewOutBlock,
    TwapNewRequest,
    TwapNewResponse,
]
