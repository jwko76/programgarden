"""빗썸 TWAP 주문내역 조회 (GET /v1/twap) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    TwapListInBlock,
    TwapListOutBlock,
    TwapListRequest,
    TwapListResponse,
    TwapOrderItem,
)


class TrTwapList(GenericBithumbTR[TwapListResponse]):
    """빗썸 TWAP 주문내역 조회 TR 클래스입니다."""

    def __init__(self, request_data: TwapListRequest):
        if not isinstance(request_data, TwapListRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.TWAP_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> TwapListResponse:
        if exc is not None:
            return TwapListResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return TwapListResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = TwapListOutBlock.model_validate(data) if data else None
        return TwapListResponse(status_code=status_code, block=block)


__all__ = [
    TrTwapList,
    TwapListInBlock,
    TwapListOutBlock,
    TwapListRequest,
    TwapListResponse,
    TwapOrderItem,
]
