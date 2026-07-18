"""키움증권 계좌평가잔고내역요청 (kt00018) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    InquireBalanceInBlock,
    InquireBalanceOutBlock1,
    InquireBalanceOutBlock2,
    InquireBalanceRequest,
    InquireBalanceResponse,
)


class TrInquireBalance(GenericKiwoomTR[InquireBalanceResponse]):
    """키움 계좌평가잔고내역요청 TR 클래스입니다. api-id: kt00018."""

    def __init__(self, request_data: InquireBalanceRequest):
        if not isinstance(request_data, InquireBalanceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.ACNT_PATH,
            tr_id=TR_IDS.INQUIRE_BALANCE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquireBalanceResponse:
        if exc is not None:
            return InquireBalanceResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return InquireBalanceResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        blocks = [
            InquireBalanceOutBlock1.model_validate(item)
            for item in (data.get("stk_acnt_evlt_prst") or [])
            if isinstance(item, dict)
        ]
        block = InquireBalanceOutBlock2.model_validate(data)
        return InquireBalanceResponse(
            status_code=status, return_code=return_code, return_msg=return_msg,
            blocks=blocks, block=block,
        )


__all__ = [
    TrInquireBalance,
    InquireBalanceInBlock,
    InquireBalanceOutBlock1,
    InquireBalanceOutBlock2,
    InquireBalanceRequest,
    InquireBalanceResponse,
]
