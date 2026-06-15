"""빗썸 가상자산 출금 요청 (POST /v1/withdraws/coin) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    WithdrawCoinInBlock,
    WithdrawCoinOutBlock,
    WithdrawCoinRequest,
    WithdrawCoinResponse,
)


class TrWithdrawCoin(GenericBithumbTR[WithdrawCoinResponse]):
    """빗썸 가상자산 출금 요청 TR 클래스입니다."""

    def __init__(self, request_data: WithdrawCoinRequest):
        if not isinstance(request_data, WithdrawCoinRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.WITHDRAWS_COIN_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> WithdrawCoinResponse:
        if exc is not None:
            return WithdrawCoinResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return WithdrawCoinResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = WithdrawCoinOutBlock.model_validate(data) if data else None
        return WithdrawCoinResponse(status_code=status_code, block=block)


__all__ = [
    TrWithdrawCoin,
    WithdrawCoinInBlock,
    WithdrawCoinOutBlock,
    WithdrawCoinRequest,
    WithdrawCoinResponse,
]
