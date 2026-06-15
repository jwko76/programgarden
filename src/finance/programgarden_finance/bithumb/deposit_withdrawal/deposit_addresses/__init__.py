"""빗썸 전체 입금 주소 조회 (GET /v1/deposits/coin_addresses) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositAddressesInBlock,
    DepositAddressesOutBlock,
    DepositAddressesRequest,
    DepositAddressesResponse,
)


class TrDepositAddresses(GenericBithumbTR[DepositAddressesResponse]):
    """빗썸 전체 입금 주소 조회 TR 클래스입니다."""

    def __init__(self, request_data: DepositAddressesRequest):
        if not isinstance(request_data, DepositAddressesRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.DEPOSIT_ADDRESSES_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositAddressesResponse:
        if exc is not None:
            return DepositAddressesResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositAddressesResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [DepositAddressesOutBlock.model_validate(item) for item in (data or [])]
        return DepositAddressesResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrDepositAddresses,
    DepositAddressesInBlock,
    DepositAddressesOutBlock,
    DepositAddressesRequest,
    DepositAddressesResponse,
]
