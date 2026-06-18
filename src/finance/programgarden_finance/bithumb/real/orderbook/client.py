from __future__ import annotations

from typing import Callable, List, TYPE_CHECKING

from .blocks import OrderbookRealResponse

if TYPE_CHECKING:
    from programgarden_finance.bithumb.real import BithumbReal


class RealOrderbook:
    """빗썸 실시간 호가(orderbook) 구독 클라이언트입니다."""

    def __init__(self, parent: BithumbReal):
        self._parent = parent

    def add_orderbook_codes(self, codes: List[str]) -> None:
        """orderbook 스트림에 마켓 코드를 추가합니다.

        Parameters:
            codes: 구독할 마켓 코드 목록 (ex. ``["KRW-BTC"]``).
        """
        self._parent._add_codes(codes=codes, stream_type="orderbook")

    def remove_orderbook_codes(self, codes: List[str]) -> None:
        """orderbook 스트림에서 마켓 코드를 제거합니다."""
        self._parent._remove_codes(codes=codes, stream_type="orderbook")

    def on_orderbook(self, listener: Callable[[OrderbookRealResponse], None]) -> None:
        """orderbook push 메시지 수신 콜백을 등록합니다.

        Parameters:
            listener: sync 또는 async 함수. ``OrderbookRealResponse`` 를 인자로 받습니다.
        """
        self._parent._on_message("orderbook", listener)

    def on_remove_orderbook(self) -> None:
        """등록된 orderbook 콜백을 해제합니다."""
        self._parent._on_remove_message("orderbook")
