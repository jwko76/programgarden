from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

from .blocks import TickerRealResponse

if TYPE_CHECKING:
    from programgarden_finance.bithumb.real import BithumbReal


class RealTicker:
    """빗썸 실시간 현재가(ticker) 구독 클라이언트입니다."""

    def __init__(self, parent: BithumbReal):
        self._parent = parent

    def add_ticker_codes(self, codes: List[str]) -> None:
        """ticker 스트림에 마켓 코드를 추가합니다.

        Parameters:
            codes: 구독할 마켓 코드 목록 (ex. ``["KRW-BTC", "KRW-ETH"]``).
        """
        self._parent._add_codes(codes=codes, stream_type="ticker")

    def remove_ticker_codes(self, codes: List[str]) -> None:
        """ticker 스트림에서 마켓 코드를 제거합니다.

        Parameters:
            codes: 구독 해제할 마켓 코드 목록.
        """
        self._parent._remove_codes(codes=codes, stream_type="ticker")

    def on_ticker(self, listener: Callable[[TickerRealResponse], None]) -> None:
        """ticker push 메시지 수신 콜백을 등록합니다.

        Parameters:
            listener: sync 또는 async 함수. ``TickerRealResponse`` 를 인자로 받습니다.
        """
        self._parent._on_message("ticker", listener)

    def on_remove_ticker(self) -> None:
        """등록된 ticker 콜백을 해제합니다."""
        self._parent._on_remove_message("ticker")
