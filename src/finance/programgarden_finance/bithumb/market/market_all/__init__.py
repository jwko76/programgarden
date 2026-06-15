"""빗썸 거래대상목록 조회 (GET /v1/market/all) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    MarketAllInBlock,
    MarketAllOutBlock,
    MarketAllRequest,
    MarketAllResponse,
)


class TrMarketAll(GenericBithumbTR[MarketAllResponse]):
    """빗썸 거래대상목록 조회 TR 클래스입니다."""

    def __init__(self, request_data: MarketAllRequest):
        if not isinstance(request_data, MarketAllRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.MARKET_ALL_URL,
            requires_auth=False,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> MarketAllResponse:
        if exc is not None:
            return MarketAllResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return MarketAllResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [MarketAllOutBlock.model_validate(item) for item in (data or [])]
        return MarketAllResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrMarketAll,
    MarketAllInBlock,
    MarketAllOutBlock,
    MarketAllRequest,
    MarketAllResponse,
]
