"""빗썸 개별 출금 조회 (GET /v1/withdraw) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    WithdrawDetailInBlock,
    WithdrawDetailOutBlock,
    WithdrawDetailRequest,
    WithdrawDetailResponse,
)


class TrWithdrawDetail(GenericBithumbTR[WithdrawDetailResponse]):
    """빗썸 개별 출금 조회 TR 클래스입니다."""

    def __init__(self, request_data: WithdrawDetailRequest):
        if not isinstance(request_data, WithdrawDetailRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.WITHDRAW_DETAIL_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> WithdrawDetailResponse:
        if exc is not None:
            return WithdrawDetailResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return WithdrawDetailResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = WithdrawDetailOutBlock.model_validate(data) if data else None
        return WithdrawDetailResponse(status_code=status_code, block=block)


__all__ = [
    TrWithdrawDetail,
    WithdrawDetailInBlock,
    WithdrawDetailOutBlock,
    WithdrawDetailRequest,
    WithdrawDetailResponse,
]
