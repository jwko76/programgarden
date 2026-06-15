"""빗썸 원화 입금 (POST /v1/deposits/krw) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositKrwInBlock,
    DepositKrwOutBlock,
    DepositKrwRequest,
    DepositKrwResponse,
)


class TrDepositKrw(GenericBithumbTR[DepositKrwResponse]):
    """빗썸 원화 입금 TR 클래스입니다."""

    def __init__(self, request_data: DepositKrwRequest):
        if not isinstance(request_data, DepositKrwRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.DEPOSITS_KRW_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositKrwResponse:
        if exc is not None:
            return DepositKrwResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositKrwResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = DepositKrwOutBlock.model_validate(data) if data else None
        return DepositKrwResponse(status_code=status_code, block=block)


__all__ = [
    TrDepositKrw,
    DepositKrwInBlock,
    DepositKrwOutBlock,
    DepositKrwRequest,
    DepositKrwResponse,
]
