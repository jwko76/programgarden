"""빗썸 TWAP 주문 등록 -> 조회 -> 취소 예제입니다.

[!] 주의: ALLOW_REAL_ORDER를 True로 변경하면 실제 자금으로 TWAP 주문을 등록합니다.
TWAP 주문은 등록 즉시 분할 체결이 시작되며 최소 300초(5분) 동안 진행되므로,
실행 전 MARKET/SIDE/DURATION/FREQUENCY/PRICE/VOLUME 값을 반드시 확인하세요.

TWAP 주문내역 조회(``TWAP주문조회``)는 읽기 전용이라 ALLOW_REAL_ORDER와 무관하게
항상 실행됩니다.
"""

import logging
import os
import time
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_ticker,
    bithumb_twap_new,
    bithumb_twap_cancel,
)

logger = logging.getLogger(__name__)

load_dotenv()

# 실제 TWAP 주문을 등록하려면 True로 변경하세요. (실제 자금 사용, 최소 5분 진행)
ALLOW_REAL_ORDER = False

MARKET = "KRW-BTC"
SIDE = "bid"  # bid(매수)인 경우 price 필수, ask(매도)인 경우 volume 필수
DURATION = "300"  # 최소 300초(5분), 최대 43200초(12시간)
FREQUENCY = "60"  # 15/20/30/60/120 중 하나
ORDER_PRICE = "80000000"  # 현재가보다 충분히 낮은 한정가 (예시, bid일 때 사용)


def _login() -> Bithumb:
    bithumb = Bithumb()
    bithumb.로그인(
        accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
        secretkey=os.getenv("BITHUMB_SECRET_KEY"),
    )
    return bithumb


def query_twap_list(bithumb: Bithumb):
    """TWAP 주문내역 조회 (읽기 전용)"""

    list_resp = bithumb.주문().TWAP주문조회().req()

    if list_resp.error_msg:
        logger.error(f"TWAP 주문내역 조회 실패: {list_resp.error_msg} ({list_resp.error_name})")
        return

    logger.info(f"TWAP 주문 수: {len(list_resp.block.orders)} (has_next={list_resp.block.has_next})")
    for o in list_resp.block.orders:
        logger.info(f"  uuid={o.uuid} market={o.market} state={o.state} side={o.side}")


def run_twap_lifecycle():
    """TWAP 주문 등록 -> 조회 -> 취소"""

    bithumb = _login()

    # 0. 현재가 확인 (체결 불가능한 가격인지 검증용)
    ticker_resp = bithumb.시세().현재가(
        bithumb_ticker.TickerInBlock(markets=MARKET)
    ).req()

    if ticker_resp.error_msg or not ticker_resp.blocks:
        logger.error(f"현재가 조회 실패: {ticker_resp.error_msg}")
        return

    current_price = ticker_resp.blocks[0].trade_price
    logger.info(f"{MARKET} 현재가: {current_price:,.0f}")

    if SIDE == "bid" and float(ORDER_PRICE) >= current_price:
        logger.error("ORDER_PRICE가 현재가보다 낮아야 체결 위험이 줄어듭니다. 값을 확인하세요.")
        return

    # 1. TWAP 주문 등록
    new_resp = bithumb.주문().TWAP주문(
        bithumb_twap_new.TwapNewInBlock(
            market=MARKET,
            side=SIDE,
            duration=DURATION,
            frequency=FREQUENCY,
            price=ORDER_PRICE if SIDE == "bid" else None,
        )
    ).req()

    if new_resp.error_msg or new_resp.block is None:
        logger.error(f"TWAP 주문 등록 실패: {new_resp.error_msg} ({new_resp.error_name})")
        return

    algo_order_id = new_resp.block.algo_order_id
    logger.info(f"TWAP 주문 등록됨: algo_order_id={algo_order_id}")

    time.sleep(1)

    # 2. TWAP 주문 상태 확인
    query_twap_list(bithumb)

    # 3. TWAP 주문 취소
    cancel_resp = bithumb.주문().TWAP주문취소(
        bithumb_twap_cancel.TwapCancelInBlock(algo_order_id=algo_order_id)
    ).req()

    if cancel_resp.error_msg or cancel_resp.block is None:
        logger.error(f"TWAP 주문 취소 실패: {cancel_resp.error_msg} ({cancel_resp.error_name})")
        return

    logger.info(f"TWAP 주문 취소됨: algo_order_id={cancel_resp.block.algo_order_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        query_twap_list(_login())

        if not ALLOW_REAL_ORDER:
            logger.warning(
                "ALLOW_REAL_ORDER가 False입니다. 실제 TWAP 주문을 등록하려면 "
                "스크립트 상단의 ALLOW_REAL_ORDER를 True로 변경하고, "
                "MARKET/SIDE/DURATION/FREQUENCY/ORDER_PRICE 값을 확인한 뒤 실행하세요."
            )
        else:
            run_twap_lifecycle()
