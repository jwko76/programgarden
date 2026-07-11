"""KIS 국내주식 기간별 시세 (FHKST03010100) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKisTR, is_kis_error, parse_kis_envelope
from .blocks import (
    InquireDailyItemChartPriceInBlock,
    InquireDailyItemChartPriceOutBlock1,
    InquireDailyItemChartPriceOutBlock2,
    InquireDailyItemChartPriceRequest,
    InquireDailyItemChartPriceResponse,
)


class TrInquireDailyItemChartPrice(GenericKisTR[InquireDailyItemChartPriceResponse]):
    """KIS 국내주식 기간별 시세(일/주/월/년) TR 클래스입니다."""

    def __init__(self, request_data: InquireDailyItemChartPriceRequest):
        if not isinstance(request_data, InquireDailyItemChartPriceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            method="GET",
            url_path=URLS.INQUIRE_DAILY_ITEMCHARTPRICE_PATH,
            tr_id=TR_IDS.INQUIRE_DAILY_ITEMCHARTPRICE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquireDailyItemChartPriceResponse:
        if exc is not None:
            return InquireDailyItemChartPriceResponse(error_msg=str(exc))

        status, rt_cd, msg_cd, msg1, outputs = parse_kis_envelope(resp, resp_json)

        if is_kis_error(status, rt_cd):
            return InquireDailyItemChartPriceResponse(
                status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
                error_msg=msg1 or f"HTTP {status}",
            )

        block1 = InquireDailyItemChartPriceOutBlock1.model_validate(outputs.get("output1") or {})
        # output2: 빈 항목({}만 있는 경우)이 섞일 수 있어 영업일자 없는 항목은 제외
        blocks = [
            InquireDailyItemChartPriceOutBlock2.model_validate(item)
            for item in (outputs.get("output2") or [])
            if isinstance(item, dict) and item.get("stck_bsop_date")
        ]
        return InquireDailyItemChartPriceResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
            block1=block1, blocks=blocks,
        )


__all__ = [
    TrInquireDailyItemChartPrice,
    InquireDailyItemChartPriceInBlock,
    InquireDailyItemChartPriceOutBlock1,
    InquireDailyItemChartPriceOutBlock2,
    InquireDailyItemChartPriceRequest,
    InquireDailyItemChartPriceResponse,
]
