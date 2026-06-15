"""빗썸 전체 계좌 조회 (GET /v1/accounts) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    AccountsInBlock,
    AccountsOutBlock,
    AccountsRequest,
    AccountsResponse,
)


class TrAccounts(GenericBithumbTR[AccountsResponse]):
    """빗썸 전체 계좌 조회 TR 클래스입니다."""

    def __init__(self, request_data: AccountsRequest):
        if not isinstance(request_data, AccountsRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.ACCOUNTS_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> AccountsResponse:
        if exc is not None:
            return AccountsResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return AccountsResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [AccountsOutBlock.model_validate(item) for item in (data or [])]
        return AccountsResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrAccounts,
    AccountsInBlock,
    AccountsOutBlock,
    AccountsRequest,
    AccountsResponse,
]
