"""KIS 실시간 체결가 (H0STCNT0) 스트림 클라이언트입니다."""

from typing import Any, Callable, List

from ...config import TR_IDS


class RealCcnl:
    """실시간 체결가 구독 클라이언트입니다.

    Example:
        ccnl = kis.real().ccnl()
        ccnl.add_ccnl_symbols(["005930"])
        ccnl.on_ccnl(lambda resp: print(resp.stck_prpr))
    """

    def __init__(self, parent):
        self._parent = parent

    def add_ccnl_symbols(self, symbols: List[str]) -> None:
        """체결가 스트림에 종목코드를 추가 구독합니다."""
        self._parent._add_keys(symbols, TR_IDS.REAL_CCNL)

    체결가등록 = add_ccnl_symbols

    def remove_ccnl_symbols(self, symbols: List[str]) -> None:
        """체결가 스트림 구독에서 종목코드를 제거합니다."""
        self._parent._remove_keys(symbols, TR_IDS.REAL_CCNL)

    체결가해제 = remove_ccnl_symbols

    def on_ccnl(self, listener: Callable[[Any], Any]) -> None:
        """체결가 메시지 콜백을 등록합니다 (sync/async 모두 허용)."""
        self._parent._on_message(TR_IDS.REAL_CCNL, listener)

    체결가수신 = on_ccnl

    def on_remove_ccnl(self) -> None:
        """체결가 메시지 콜백을 해제합니다."""
        self._parent._on_remove_message(TR_IDS.REAL_CCNL)

    체결가수신해제 = on_remove_ccnl
