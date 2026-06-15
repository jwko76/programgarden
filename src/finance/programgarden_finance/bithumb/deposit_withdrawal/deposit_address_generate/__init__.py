"""빗썸 입금 주소 생성 요청 (POST /v1/deposits/generate_coin_address) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositAddressGenerateInBlock,
    DepositAddressGenerateOutBlock,
    DepositAddressGenerateRequest,
    DepositAddressGenerateResponse,
)


class TrDepositAddressGenerate(GenericBithumbTR[DepositAddressGenerateResponse]):
    """빗썸 입금 주소 생성 요청 TR 클래스입니다."""

    def __init__(self, request_data: DepositAddressGenerateRequest):
        if not isinstance(request_data, DepositAddressGenerateRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="POST",
            url=URLS.DEPOSIT_ADDRESS_GENERATE_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositAddressGenerateResponse:
        if exc is not None:
            return DepositAddressGenerateResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositAddressGenerateResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = DepositAddressGenerateOutBlock.model_validate(data) if data else None
        return DepositAddressGenerateResponse(status_code=status_code, block=block)


__all__ = [
    TrDepositAddressGenerate,
    DepositAddressGenerateInBlock,
    DepositAddressGenerateOutBlock,
    DepositAddressGenerateRequest,
    DepositAddressGenerateResponse,
]
