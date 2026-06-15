"""빗썸 입출금 수수료 조회 (GET /v2/fee/inout/{currency}) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    FeeInoutInBlock,
    FeeInoutNetwork,
    FeeInoutOutBlock,
    FeeInoutRequest,
    FeeInoutResponse,
)


class TrFeeInout(GenericBithumbTR[FeeInoutResponse]):
    """빗썸 입출금 수수료 조회 TR 클래스입니다."""

    def __init__(self, request_data: FeeInoutRequest):
        if not isinstance(request_data, FeeInoutRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_builder=lambda rd: URLS.fee_inout_url(rd.params.currency),
            requires_auth=False,
            exclude_params={"currency"},
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> FeeInoutResponse:
        if exc is not None:
            return FeeInoutResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return FeeInoutResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [FeeInoutOutBlock.model_validate(item) for item in (data or [])]
        return FeeInoutResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrFeeInout,
    FeeInoutInBlock,
    FeeInoutNetwork,
    FeeInoutOutBlock,
    FeeInoutRequest,
    FeeInoutResponse,
]
