"""빗썸 출금 허용 주소 리스트 조회 (GET /v1/withdraws/coin_addresses) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    WithdrawCoinAddressesInBlock,
    WithdrawCoinAddressesOutBlock,
    WithdrawCoinAddressesRequest,
    WithdrawCoinAddressesResponse,
)


class TrWithdrawCoinAddresses(GenericBithumbTR[WithdrawCoinAddressesResponse]):
    """빗썸 출금 허용 주소 리스트 조회 TR 클래스입니다."""

    def __init__(self, request_data: WithdrawCoinAddressesRequest):
        if not isinstance(request_data, WithdrawCoinAddressesRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.WITHDRAW_COIN_ADDRESSES_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> WithdrawCoinAddressesResponse:
        if exc is not None:
            return WithdrawCoinAddressesResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return WithdrawCoinAddressesResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [WithdrawCoinAddressesOutBlock.model_validate(item) for item in (data or [])]
        return WithdrawCoinAddressesResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrWithdrawCoinAddresses,
    WithdrawCoinAddressesInBlock,
    WithdrawCoinAddressesOutBlock,
    WithdrawCoinAddressesRequest,
    WithdrawCoinAddressesResponse,
]
