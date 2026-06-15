"""빗썸 입출금 현황 조회 (GET /v1/status/wallet) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    WalletStatusInBlock,
    WalletStatusOutBlock,
    WalletStatusRequest,
    WalletStatusResponse,
)


class TrWalletStatus(GenericBithumbTR[WalletStatusResponse]):
    """빗썸 입출금 현황 조회 TR 클래스입니다."""

    def __init__(self, request_data: WalletStatusRequest):
        if not isinstance(request_data, WalletStatusRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.WALLET_STATUS_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> WalletStatusResponse:
        if exc is not None:
            return WalletStatusResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return WalletStatusResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [WalletStatusOutBlock.model_validate(item) for item in (data or [])]
        return WalletStatusResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrWalletStatus,
    WalletStatusInBlock,
    WalletStatusOutBlock,
    WalletStatusRequest,
    WalletStatusResponse,
]
