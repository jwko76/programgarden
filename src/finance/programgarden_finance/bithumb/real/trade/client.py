from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

from .blocks import TradeRealResponse

if TYPE_CHECKING:
    from programgarden_finance.bithumb.real import BithumbReal


class RealTrade:
    """빗썸 실시간 체결(trade) 구독 클라이언트입니다."""

    def __init__(self, parent: BithumbReal):
        self._parent = parent

    def add_trade_codes(self, codes: List[str]) -> None:
        """trade 스트림에 마켓 코드를 추가합니다.

        Parameters:
            codes: 구독할 마켓 코드 목록 (ex. ``["KRW-BTC"]``).
        """
        self._parent._add_codes(codes=codes, stream_type="trade")

    def remove_trade_codes(self, codes: List[str]) -> None:
        """trade 스트림에서 마켓 코드를 제거합니다."""
        self._parent._remove_codes(codes=codes, stream_type="trade")

    def on_trade(self, listener: Callable[[TradeRealResponse], None]) -> None:
        """trade push 메시지 수신 콜백을 등록합니다.

        Parameters:
            listener: sync 또는 async 함수. ``TradeRealResponse`` 를 인자로 받습니다.
        """
        self._parent._on_message("trade", listener)

    def on_remove_trade(self) -> None:
        """등록된 trade 콜백을 해제합니다."""
        self._parent._on_remove_message("trade")
