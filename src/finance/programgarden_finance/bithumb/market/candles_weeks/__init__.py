"""빗썸 주(週) 캔들 조회 (GET /v1/candles/weeks) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    CandlesWeeksInBlock,
    CandlesWeeksOutBlock,
    CandlesWeeksRequest,
    CandlesWeeksResponse,
)


class TrCandlesWeeks(GenericBithumbTR[CandlesWeeksResponse]):
    """빗썸 주 캔들 조회 TR 클래스입니다."""

    def __init__(self, request_data: CandlesWeeksRequest):
        if not isinstance(request_data, CandlesWeeksRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.CANDLES_WEEKS_URL,
            requires_auth=False,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> CandlesWeeksResponse:
        if exc is not None:
            return CandlesWeeksResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return CandlesWeeksResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [CandlesWeeksOutBlock.model_validate(item) for item in (data or [])]
        return CandlesWeeksResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrCandlesWeeks,
    CandlesWeeksInBlock,
    CandlesWeeksOutBlock,
    CandlesWeeksRequest,
    CandlesWeeksResponse,
]
