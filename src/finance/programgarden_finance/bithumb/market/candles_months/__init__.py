"""빗썸 월(月) 캔들 조회 (GET /v1/candles/months) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    CandlesMonthsInBlock,
    CandlesMonthsOutBlock,
    CandlesMonthsRequest,
    CandlesMonthsResponse,
)


class TrCandlesMonths(GenericBithumbTR[CandlesMonthsResponse]):
    """빗썸 월 캔들 조회 TR 클래스입니다."""

    def __init__(self, request_data: CandlesMonthsRequest):
        if not isinstance(request_data, CandlesMonthsRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.CANDLES_MONTHS_URL,
            requires_auth=False,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> CandlesMonthsResponse:
        if exc is not None:
            return CandlesMonthsResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return CandlesMonthsResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [CandlesMonthsOutBlock.model_validate(item) for item in (data or [])]
        return CandlesMonthsResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrCandlesMonths,
    CandlesMonthsInBlock,
    CandlesMonthsOutBlock,
    CandlesMonthsRequest,
    CandlesMonthsResponse,
]
