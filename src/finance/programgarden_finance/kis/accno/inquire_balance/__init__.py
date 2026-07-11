"""KIS 주식잔고조회 (TTTC8434R/VTTC8434R) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    InquireBalanceInBlock,
    InquireBalanceOutBlock1,
    InquireBalanceOutBlock2,
    InquireBalanceRequest,
    InquireBalanceResponse,
)


class TrInquireBalance(GenericKisTR[InquireBalanceResponse]):
    """KIS 주식잔고조회 TR 클래스입니다. 실전 TTTC8434R / 모의 VTTC8434R."""

    def __init__(self, request_data: InquireBalanceRequest):
        if not isinstance(request_data, InquireBalanceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_path=URLS.INQUIRE_BALANCE_PATH,
            tr_id=TR_IDS.INQUIRE_BALANCE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquireBalanceResponse:
        if exc is not None:
            return InquireBalanceResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return InquireBalanceResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        blocks = [
            InquireBalanceOutBlock1.model_validate(item)
            for item in (outputs.get("output1") or [])
            if isinstance(item, dict)
        ]
        # output2는 배열로 반환되며 첫 항목이 계좌 요약
        output2 = outputs.get("output2") or []
        block2_data = output2[0] if isinstance(output2, list) and output2 else (
            output2 if isinstance(output2, dict) else {}
        )
        block2 = InquireBalanceOutBlock2.model_validate(block2_data)
        return InquireBalanceResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
            blocks=blocks, block2=block2,
        )


__all__ = [
    TrInquireBalance,
    InquireBalanceInBlock,
    InquireBalanceOutBlock1,
    InquireBalanceOutBlock2,
    InquireBalanceRequest,
    InquireBalanceResponse,
]
