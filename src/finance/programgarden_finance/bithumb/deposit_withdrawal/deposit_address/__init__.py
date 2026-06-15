"""빗썸 개별 입금 주소 조회 (GET /v1/deposits/coin_address) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositAddressInBlock,
    DepositAddressOutBlock,
    DepositAddressRequest,
    DepositAddressResponse,
)


class TrDepositAddress(GenericBithumbTR[DepositAddressResponse]):
    """빗썸 개별 입금 주소 조회 TR 클래스입니다."""

    def __init__(self, request_data: DepositAddressRequest):
        if not isinstance(request_data, DepositAddressRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.DEPOSIT_ADDRESS_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositAddressResponse:
        if exc is not None:
            return DepositAddressResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositAddressResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = DepositAddressOutBlock.model_validate(data) if data else None
        return DepositAddressResponse(status_code=status_code, block=block)


__all__ = [
    TrDepositAddress,
    DepositAddressInBlock,
    DepositAddressOutBlock,
    DepositAddressRequest,
    DepositAddressResponse,
]
