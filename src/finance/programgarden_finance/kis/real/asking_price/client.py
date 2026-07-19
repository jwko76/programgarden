"""KIS 실시간 호가 (H0STASP0) 스트림 클라이언트입니다."""

from typing import Any, Callable, List

from ...config import TR_IDS


class RealAskingPrice:
    """실시간 호가 구독 클라이언트입니다.

    Example:
        asking = kis.real().asking_price()
        asking.add_asking_price_symbols(["005930"])
        asking.on_asking_price(lambda resp: print(resp.askp1, resp.bidp1))
    """

    def __init__(self, parent):
        self._parent = parent

    def add_asking_price_symbols(self, symbols: List[str]) -> None:
        """호가 스트림에 종목코드를 추가 구독합니다."""
        self._parent._add_keys(symbols, TR_IDS.REAL_ASKING_PRICE)

    호가등록 = add_asking_price_symbols

    def remove_asking_price_symbols(self, symbols: List[str]) -> None:
        """호가 스트림 구독에서 종목코드를 제거합니다."""
        self._parent._remove_keys(symbols, TR_IDS.REAL_ASKING_PRICE)

    호가해제 = remove_asking_price_symbols

    def on_asking_price(self, listener: Callable[[Any], Any]) -> None:
        """호가 메시지 콜백을 등록합니다 (sync/async 모두 허용)."""
        self._parent._on_message(TR_IDS.REAL_ASKING_PRICE, listener)

    호가수신 = on_asking_price

    def on_remove_asking_price(self) -> None:
        """호가 메시지 콜백을 해제합니다."""
        self._parent._on_remove_message(TR_IDS.REAL_ASKING_PRICE)

    호가수신해제 = on_remove_asking_price
