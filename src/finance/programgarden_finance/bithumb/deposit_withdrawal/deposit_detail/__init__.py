"""빗썸 개별 입금 조회 (GET /v1/deposit) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    DepositDetailInBlock,
    DepositDetailOutBlock,
    DepositDetailRequest,
    DepositDetailResponse,
)


class TrDepositDetail(GenericBithumbTR[DepositDetailResponse]):
    """빗썸 개별 입금 조회 TR 클래스입니다."""

    def __init__(self, request_data: DepositDetailRequest):
        if not isinstance(request_data, DepositDetailRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.DEPOSIT_DETAIL_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> DepositDetailResponse:
        if exc is not None:
            return DepositDetailResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return DepositDetailResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        block = DepositDetailOutBlock.model_validate(data) if data else None
        return DepositDetailResponse(status_code=status_code, block=block)


__all__ = [
    TrDepositDetail,
    DepositDetailInBlock,
    DepositDetailOutBlock,
    DepositDetailRequest,
    DepositDetailResponse,
]
