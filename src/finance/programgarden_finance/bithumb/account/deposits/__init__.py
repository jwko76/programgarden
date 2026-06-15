"""빗썸 입금 리스트 조회 (GET /v1/deposits) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositOutBlock,
    DepositsInBlock,
    DepositsRequest,
    DepositsResponse,
    DepositState,
)


class TrDeposits(GenericBithumbTR[DepositsResponse]):
    """빗썸 입금 리스트 조회 TR 클래스입니다."""

    def __init__(self, request_data: DepositsRequest):
        if not isinstance(request_data, DepositsRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.DEPOSITS_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositsResponse:
        if exc is not None:
            return DepositsResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositsResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [DepositOutBlock.model_validate(item) for item in (data or [])]
        return DepositsResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrDeposits,
    DepositOutBlock,
    DepositsInBlock,
    DepositsRequest,
    DepositsResponse,
    DepositState,
]
