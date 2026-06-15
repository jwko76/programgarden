import logging
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_market_all,
    bithumb_ticker,
    bithumb_orderbook,
    bithumb_trades_ticks,
    bithumb_candles_minutes,
    bithumb_candles_days,
    bithumb_candles_weeks,
    bithumb_candles_months,
    bithumb_fee_inout,
)

logger = logging.getLogger(__name__)

load_dotenv()


def test_market_all():
    """거래대상목록 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().거래대상목록(
        bithumb_market_all.MarketAllInBlock(isDetails=False)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    krw_markets = [b for b in (response.blocks or []) if b.market.startswith("KRW-")]
    logger.info(f"KRW 마켓 수: {len(krw_markets)}")
    for item in krw_markets[:5]:
        logger.info(f"{item.market} | {item.korean_name} ({item.english_name})")


def test_ticker():
    """현재가(스냅샷) 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().현재가(
        bithumb_ticker.TickerInBlock(markets="KRW-BTC,KRW-ETH")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(
            f"{item.market} | 현재가: {item.trade_price:,.0f} | "
            f"전일대비: {item.change} {item.signed_change_rate:+.2%}"
        )


def test_orderbook():
    """호가 정보 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().호가(
        bithumb_orderbook.OrderbookInBlock(markets="KRW-BTC")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(f"{item.market} | 매도총잔량: {item.total_ask_size} | 매수총잔량: {item.total_bid_size}")
        top = item.orderbook_units[0]
        logger.info(f"  1호가: 매도 {top.ask_price:,.0f}({top.ask_size}) / 매수 {top.bid_price:,.0f}({top.bid_size})")


def test_trades_ticks():
    """최근 체결 내역 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().체결내역(
        bithumb_trades_ticks.TradesTicksInBlock(market="KRW-BTC", count=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(
            f"{item.trade_date_utc} {item.trade_time_utc} UTC | {item.ask_bid} | "
            f"{item.trade_price:,.0f} x {item.trade_volume}"
        )


def test_candles_minutes():
    """분(分) 캔들 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().분캔들(
        bithumb_candles_minutes.CandlesMinutesInBlock(market="KRW-BTC", unit=1, count=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(
            f"{item.candle_date_time_kst} | 종가 {item.trade_price:,.0f} | "
            f"누적거래량 {item.candle_acc_trade_volume}"
        )


def test_candles_days():
    """일(日) 캔들 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().일캔들(
        bithumb_candles_days.CandlesDaysInBlock(market="KRW-BTC", count=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(
            f"{item.candle_date_time_kst} | 종가 {item.trade_price:,.0f} | "
            f"변화율 {item.change_rate:+.2%}"
        )


def test_candles_weeks():
    """주(週) 캔들 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().주캔들(
        bithumb_candles_weeks.CandlesWeeksInBlock(market="KRW-BTC", count=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(f"{item.first_day_of_period} 시작 | 종가 {item.trade_price:,.0f}")


def test_candles_months():
    """월(月) 캔들 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().월캔들(
        bithumb_candles_months.CandlesMonthsInBlock(market="KRW-BTC", count=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(f"{item.first_day_of_period} 시작 | 종가 {item.trade_price:,.0f}")


def test_fee_inout():
    """입출금 수수료 조회 테스트"""

    bithumb = Bithumb()

    response = bithumb.시세().입출금수수료조회(
        bithumb_fee_inout.FeeInoutInBlock(currency="BTC")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        for network in item.networks:
            logger.info(
                f"{item.currency} ({network.net_name}) | "
                f"입금수수료: {network.deposit_fee_quantity} | "
                f"출금수수료: {network.withdraw_fee_quantity or network.withdraw_rate}"
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    test_market_all()
    test_ticker()
    test_orderbook()
    test_trades_ticks()
    test_candles_minutes()
    test_candles_days()
    test_candles_weeks()
    test_candles_months()
    test_fee_inout()
