"""KIS 주식잔고조회 (TTTC8434R/VTTC8434R) TR 모듈입니다."""

from programgarden_core.exceptions import TrRequestDataNotFoundException

from ...config import URLS, TR_IDS
from ...tr_helpers import (
    GenericKisTR,
    has_next_page,
    is_kis_error,
    parse_kis_envelope,
    parse_tr_cont,
)
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
        body = resp_json if isinstance(resp_json, dict) else {}
        return InquireBalanceResponse(
            status_code=status, rt_cd=rt_cd, msg_cd=msg_cd, msg1=msg1,
            blocks=blocks, block2=block2,
            tr_cont=parse_tr_cont(resp_headers),
            ctx_area_fk100=(body.get("ctx_area_fk100") or "").strip() or None,
            ctx_area_nk100=(body.get("ctx_area_nk100") or "").strip() or None,
        )

    # ─────────────────────────────────────── 연속조회 (tr_cont) ──

    def _apply_continuation(self, response: InquireBalanceResponse) -> None:
        """다음 페이지 요청을 위해 연속조회 키를 파라미터에 반영합니다."""
        self.request_data.params.ctx_area_fk100 = response.ctx_area_fk100 or ""
        self.request_data.params.ctx_area_nk100 = response.ctx_area_nk100 or ""
        self.set_continuation("N")

    def _merge_pages(self, first: InquireBalanceResponse, pages: list) -> InquireBalanceResponse:
        """여러 페이지의 보유 종목을 첫 응답에 병합합니다 (요약은 마지막 페이지 기준)."""
        merged_blocks = list(first.blocks or [])
        last = first
        for page in pages:
            merged_blocks.extend(page.blocks or [])
            last = page
        first.blocks = merged_blocks
        if last.block2 is not None:
            first.block2 = last.block2
        first.tr_cont = last.tr_cont
        return first

    def req_all(self, max_pages: int = 10) -> InquireBalanceResponse:
        """보유 종목이 여러 페이지일 때 tr_cont 연속조회로 전체를 수집합니다.

        Parameters:
            max_pages: 안전 상한 (기본 10페이지 = 종목 수백 개 수준).
        """
        first = self.req()
        if first.error_msg is not None:
            return first

        pages = []
        current = first
        while has_next_page(current.tr_cont) and len(pages) < max_pages - 1:
            self._apply_continuation(current)
            current = self.req()
            if current.error_msg is not None:
                break
            pages.append(current)
        return self._merge_pages(first, pages)

    async def req_all_async(self, max_pages: int = 10) -> InquireBalanceResponse:
        """``req_all``의 비동기 버전입니다."""
        first = await self.req_async()
        if first.error_msg is not None:
            return first

        pages = []
        current = first
        while has_next_page(current.tr_cont) and len(pages) < max_pages - 1:
            self._apply_continuation(current)
            current = await self.req_async()
            if current.error_msg is not None:
                break
            pages.append(current)
        return self._merge_pages(first, pages)


__all__ = [
    TrInquireBalance,
    InquireBalanceInBlock,
    InquireBalanceOutBlock1,
    InquireBalanceOutBlock2,
    InquireBalanceRequest,
    InquireBalanceResponse,
]
