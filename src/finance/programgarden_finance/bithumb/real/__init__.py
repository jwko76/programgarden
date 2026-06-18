"""빗썸(Bithumb) 실시간 WebSocket 클래스입니다."""

from programgarden_core.korea_alias import require_korean_alias

from programgarden_finance.bithumb.real_base import (
    BithumbRealBase,
    BithumbSubscriptionLimitExceeded,
    DEFAULT_MAX_SUBSCRIBE_CODES,
)
from .ticker import RealTicker, TickerRealResponse
from .trade import RealTrade, TradeRealResponse
from .orderbook import RealOrderbook, OrderbookRealResponse, OrderbookRealUnit


class BithumbReal(BithumbRealBase):
    """빗썸 실시간 WebSocket 클라이언트입니다.

    ``Bithumb().real()`` 을 통해 얻는 싱글톤 인스턴스입니다.
    ``await real.connect()`` → 구독 → ``await real.close()`` 패턴으로 사용합니다.

    지원 스트림:
        - ``ticker()`` — 현재가 실시간 업데이트
        - ``trade()`` — 체결 틱 실시간 스트림
        - ``orderbook()`` — 호가창 실시간 스냅샷

    Example::

        bithumb = Bithumb()
        real = bithumb.real()

        await real.connect()

        real.ticker().add_ticker_codes(["KRW-BTC", "KRW-ETH"])
        real.ticker().on_ticker(lambda msg: print(msg.code, msg.trade_price))

        await asyncio.sleep(10)
        await real.close()
    """

    def __init__(
        self,
        reconnect: bool = True,
        max_backoff: float = 60.0,
        max_subscribe_codes: int = DEFAULT_MAX_SUBSCRIBE_CODES,
    ):
        super().__init__(
            reconnect=reconnect,
            max_backoff=max_backoff,
            max_subscribe_codes=max_subscribe_codes,
        )

    @require_korean_alias
    def ticker(self) -> RealTicker:
        """실시간 현재가(ticker) 구독 클라이언트를 반환합니다."""
        if self._ws is None:
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        return RealTicker(parent=self)

    현재가 = ticker
    현재가.__doc__ = "실시간 현재가(ticker) 구독 클라이언트를 반환합니다."

    @require_korean_alias
    def trade(self) -> RealTrade:
        """실시간 체결(trade) 구독 클라이언트를 반환합니다."""
        if self._ws is None:
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        return RealTrade(parent=self)

    체결 = trade
    체결.__doc__ = "실시간 체결(trade) 구독 클라이언트를 반환합니다."

    @require_korean_alias
    def orderbook(self) -> RealOrderbook:
        """실시간 호가(orderbook) 구독 클라이언트를 반환합니다."""
        if self._ws is None:
            raise RuntimeError("빗썸 WebSocket이 연결되지 않았습니다")
        return RealOrderbook(parent=self)

    호가 = orderbook
    호가.__doc__ = "실시간 호가(orderbook) 구독 클라이언트를 반환합니다."


__all__ = [
    "BithumbReal",
    "BithumbSubscriptionLimitExceeded",
    "DEFAULT_MAX_SUBSCRIBE_CODES",

    "RealTicker",
    "TickerRealResponse",

    "RealTrade",
    "TradeRealResponse",

    "RealOrderbook",
    "OrderbookRealResponse",
    "OrderbookRealUnit",
]
