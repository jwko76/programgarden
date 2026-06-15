"""빗썸 출금 가능 정보 조회 (GET /v1/withdraws/chance) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    WithdrawsChanceAccount,
    WithdrawsChanceCurrency,
    WithdrawsChanceInBlock,
    WithdrawsChanceMemberLevel,
    WithdrawsChanceOutBlock,
    WithdrawsChanceRequest,
    WithdrawsChanceResponse,
    WithdrawsChanceWithdrawLimit,
)


class TrWithdrawsChance(GenericBithumbTR[WithdrawsChanceResponse]):
    """빗썸 출금 가능 정보 조회 TR 클래스입니다."""

    def __init__(self, request_data: WithdrawsChanceRequest):
        if not isinstance(request_data, WithdrawsChanceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.WITHDRAWS_CHANCE_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> WithdrawsChanceResponse:
        if exc is not None:
            return WithdrawsChanceResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return WithdrawsChanceResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = WithdrawsChanceOutBlock.model_validate(data) if data else None
        return WithdrawsChanceResponse(status_code=status_code, block=block)


__all__ = [
    TrWithdrawsChance,
    WithdrawsChanceAccount,
    WithdrawsChanceCurrency,
    WithdrawsChanceInBlock,
    WithdrawsChanceMemberLevel,
    WithdrawsChanceOutBlock,
    WithdrawsChanceRequest,
    WithdrawsChanceResponse,
    WithdrawsChanceWithdrawLimit,
]
