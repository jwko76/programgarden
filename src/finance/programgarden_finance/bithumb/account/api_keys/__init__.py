"""빗썸 API 키 리스트 조회 (GET /v1/api_keys) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS
from ...tr_helpers import GenericBithumbTR, parse_bithumb_envelope
from .blocks import (
    ApiKeysInBlock,
    ApiKeysOutBlock,
    ApiKeysRequest,
    ApiKeysResponse,
)


class TrApiKeys(GenericBithumbTR[ApiKeysResponse]):
    """빗썸 API 키 리스트 조회 TR 클래스입니다."""

    def __init__(self, request_data: ApiKeysRequest):
        if not isinstance(request_data, ApiKeysRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url=URLS.API_KEYS_URL,
            requires_auth=True,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> ApiKeysResponse:
        if exc is not None:
            return ApiKeysResponse(error_msg=str(exc))

        status_code, data, error_name, error_msg = parse_bithumb_envelope(resp, resp_json)

        if error_msg is not None:
            return ApiKeysResponse(status_code=status_code, error_name=error_name, error_msg=error_msg)

        blocks = [ApiKeysOutBlock.model_validate(item) for item in (data or [])]
        return ApiKeysResponse(status_code=status_code, blocks=blocks)


__all__ = [
    TrApiKeys,
    ApiKeysInBlock,
    ApiKeysOutBlock,
    ApiKeysRequest,
    ApiKeysResponse,
]
