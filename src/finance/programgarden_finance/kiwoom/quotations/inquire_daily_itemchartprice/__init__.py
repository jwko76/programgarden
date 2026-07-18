"""키움증권 주식일봉차트조회요청 (ka10081) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import GenericKiwoomTR, is_kiwoom_error, parse_kiwoom_envelope
from .blocks import (
    InquireDailyItemChartPriceInBlock,
    InquireDailyItemChartPriceOutCandle,
    InquireDailyItemChartPriceRequest,
    InquireDailyItemChartPriceResponse,
)


class TrInquireDailyItemChartPrice(GenericKiwoomTR[InquireDailyItemChartPriceResponse]):
    """키움 주식일봉차트조회요청 TR 클래스입니다. api-id: ka10081."""

    def __init__(self, request_data: InquireDailyItemChartPriceRequest):
        if not isinstance(request_data, InquireDailyItemChartPriceRequest):
            raise TrRequestDataNotFoundException()

        super().__init__(
            request_data,
            self._build_response,
            url_path=URLS.CHART_PATH,
            tr_id=TR_IDS.INQUIRE_DAILY_ITEMCHARTPRICE,
        )

    def _build_response(self, resp, resp_json, resp_headers, exc) -> InquireDailyItemChartPriceResponse:
        if exc is not None:
            return InquireDailyItemChartPriceResponse(error_msg=str(exc))

        status, return_code, return_msg, data = parse_kiwoom_envelope(resp, resp_json)

        if is_kiwoom_error(status, return_code):
            return InquireDailyItemChartPriceResponse(
                status_code=status, return_code=return_code, return_msg=return_msg,
                error_msg=return_msg or f"HTTP {status}",
            )

        # 키움은 빈 항목이 섞여 올 수 있어 일자 없는 항목은 제외합니다 (KIS 패턴 준용).
        blocks = [
            InquireDailyItemChartPriceOutCandle.model_validate(item)
            for item in (data.get("stk_dt_pole") or [])
            if isinstance(item, dict) and item.get("dt")
        ]
        return InquireDailyItemChartPriceResponse(
            status_code=status, return_code=return_code, return_msg=return_msg, blocks=blocks,
        )


__all__ = [
    TrInquireDailyItemChartPrice,
    InquireDailyItemChartPriceInBlock,
    InquireDailyItemChartPriceOutCandle,
    InquireDailyItemChartPriceRequest,
    InquireDailyItemChartPriceResponse,
]
