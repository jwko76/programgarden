"""빗썸 원화 입금 리스트 조회 (GET /v1/deposits/krw) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositKrwListItem,
    DepositKrwState,
    DepositsKrwInBlock,
    DepositsKrwRequest,
    DepositsKrwResponse,
)


class TrDepositsKrw(GenericBithumbTR[DepositsKrwResponse]):
    """빗썸 원화 입금 리스트 조회 TR 클래스입니다."""

    def __init__(self, request_data: DepositsKrwRequest):
        if not isinstance(request_data, DepositsKrwRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.DEPOSITS_KRW_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositsKrwResponse:
        if exc is not None:
            return DepositsKrwResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositsKrwResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [DepositKrwListItem.model_validate(item) for item in (data or [])]
        return DepositsKrwResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrDepositsKrw,
    DepositKrwListItem,
    DepositKrwState,
    DepositsKrwInBlock,
    DepositsKrwRequest,
    DepositsKrwResponse,
]
