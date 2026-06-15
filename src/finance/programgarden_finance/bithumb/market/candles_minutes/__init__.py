"""빗썸 분(分) 캔들 조회 (GET /v1/candles/minutes/{unit}) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    CandleMinuteUnit,
    CandlesMinutesInBlock,
    CandlesMinutesOutBlock,
    CandlesMinutesRequest,
    CandlesMinutesResponse,
)


class TrCandlesMinutes(GenericBithumbTR[CandlesMinutesResponse]):
    """빗썸 분 캔들 조회 TR 클래스입니다."""

    def __init__(self, request_data: CandlesMinutesRequest):
        if not isinstance(request_data, CandlesMinutesRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_builder=lambda rd: URLS.candles_minutes_url(rd.params.unit),
            requires_auth=False,
            exclude_params={"unit"},
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> CandlesMinutesResponse:
        if exc is not None:
            return CandlesMinutesResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return CandlesMinutesResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [CandlesMinutesOutBlock.model_validate(item) for item in (data or [])]
        return CandlesMinutesResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrCandlesMinutes,
    CandleMinuteUnit,
    CandlesMinutesInBlock,
    CandlesMinutesOutBlock,
    CandlesMinutesRequest,
    CandlesMinutesResponse,
]
