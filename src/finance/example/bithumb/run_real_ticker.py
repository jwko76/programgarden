"""빗썸 실시간 WebSocket 예제 — ticker / trade / orderbook 구독.

실행 방법::

    python -m example.bithumb.run_real_ticker

인증 불필요 (공개 WebSocket). Ctrl+C 로 종료합니다.
"""

import asyncio
import logging

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.real import (
    TickerRealResponse,
    TradeRealResponse,
    OrderbookRealResponse,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

MARKETS = ["KRW-BTC", "KRW-ETH"]


def on_ticker(msg: TickerRealResponse) -> None:
    logger.info(
        "[ticker] %s | 현재가: %,.0f | %s %.4f%% | %s",
        msg.code,
        msg.trade_price,
        msg.change,
        msg.signed_change_rate * 100,
        msg.stream_type,
    )


def on_trade(msg: TradeRealResponse) -> None:
    logger.info(
        "[trade ] %s | %s %.4f @ %,.0f | seq=%d",
        msg.code,
        msg.ask_bid,
        msg.trade_volume,
        msg.trade_price,
        msg.sequential_id,
    )


def on_orderbook(msg: OrderbookRealResponse) -> None:
    if msg.orderbook_units:
        top = msg.orderbook_units[0]
        logger.info(
            "[order ] %s | 매도 %,.0f(%.4f) / 매수 %,.0f(%.4f)",
            msg.code,
            top.ask_price,
            top.ask_size,
            top.bid_price,
            top.bid_size,
        )


async def main() -> None:
    bithumb = Bithumb()
    real = bithumb.real(max_subscribe_codes=0)  # 제한 없음

    logger.info("빗썸 WebSocket 연결 중...")
    await real.connect()
    logger.info("연결 완료. 구독 시작: %s", MARKETS)

    # ─── ticker 구독 ───────────────────────────
    real.ticker().add_ticker_codes(MARKETS)
    real.ticker().on_ticker(on_ticker)

    # ─── trade 구독 ────────────────────────────
    real.trade().add_trade_codes(["KRW-BTC"])
    real.trade().on_trade(on_trade)

    # ─── orderbook 구독 ────────────────────────
    real.orderbook().add_orderbook_codes(["KRW-BTC"])
    real.orderbook().on_orderbook(on_orderbook)

    logger.info("Ctrl+C 로 종료합니다.")
    try:
        while True:
            await asyncio.sleep(1)
    except asyncio.CancelledError:
        pass
    finally:
        logger.info("WebSocket 종료 중...")
        await real.close()
        logger.info("종료 완료.")


if __name__ == "__main__":
    asyncio.run(main())
