"""빗썸 가상자산 출금 취소 (DELETE /v1/withdraws/coin) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    WithdrawCoinCancelInBlock,
    WithdrawCoinCancelOutBlock,
    WithdrawCoinCancelRequest,
    WithdrawCoinCancelResponse,
)


class TrWithdrawCoinCancel(GenericBithumbTR[WithdrawCoinCancelResponse]):
    """빗썸 가상자산 출금 취소 TR 클래스입니다."""

    def __init__(self, request_data: WithdrawCoinCancelRequest):
        if not isinstance(request_data, WithdrawCoinCancelRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="DELETE",
            url=URLS.WITHDRAWS_COIN_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> WithdrawCoinCancelResponse:
        if exc is not None:
            return WithdrawCoinCancelResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return WithdrawCoinCancelResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = WithdrawCoinCancelOutBlock.model_validate(data) if data else None
        return WithdrawCoinCancelResponse(status_code=status_code, block=block)


__all__ = [
    TrWithdrawCoinCancel,
    WithdrawCoinCancelInBlock,
    WithdrawCoinCancelOutBlock,
    WithdrawCoinCancelRequest,
    WithdrawCoinCancelResponse,
]
