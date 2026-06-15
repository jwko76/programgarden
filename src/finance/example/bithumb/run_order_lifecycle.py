"""빗썸 주문 생성 -> 조회 -> 취소 예제입니다.

[!] 주의: ALLOW_REAL_ORDER를 True로 변경하면 실제 자금으로 매수 주문을 생성합니다.
체결 위험을 낮추기 위해 현재가보다 충분히 낮은 한정가로 최소 주문금액(5,000원)
수준의 매수 주문을 생성한 뒤 즉시 취소하지만, 시세 변동에 따라 체결될 수 있습니다.
실행 전 MARKET/ORDER_PRICE/ORDER_VOLUME 값을 반드시 확인하세요.
"""

import logging
import os
import time
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_ticker,
    bithumb_order_new,
    bithumb_order_detail,
    bithumb_order_cancel,
)

logger = logging.getLogger(__name__)

load_dotenv()

# 실제 주문을 생성하려면 True로 변경하세요. (실제 자금 사용)
ALLOW_REAL_ORDER = False

MARKET = "KRW-BTC"
# 최소 주문 금액(5,000원) 이상이 되도록 가격 x 수량을 설정합니다.
ORDER_PRICE = "80000000"  # 현재가보다 충분히 낮은 한정가 (예시)
ORDER_VOLUME = "0.00008"  # ORDER_PRICE x ORDER_VOLUME >= 5000원


def _login() -> Bithumb:
    bithumb = Bithumb()
    bithumb.로그인(
        accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
        secretkey=os.getenv("BITHUMB_SECRET_KEY"),
    )
    return bithumb


def run_lifecycle():
    """매수 주문 생성 -> 상태 조회 -> 취소"""

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

    if float(ORDER_PRICE) >= current_price:
        logger.error("ORDER_PRICE가 현재가보다 낮아야 체결 위험이 줄어듭니다. 값을 확인하세요.")
        return

    # 1. 매수 주문 생성 (지정가)
    new_resp = bithumb.주문().주문하기(
        bithumb_order_new.OrderNewInBlock(
            market=MARKET,
            side="bid",
            order_type="limit",
            price=ORDER_PRICE,
            volume=ORDER_VOLUME,
        )
    ).req()

    if new_resp.error_msg or new_resp.block is None:
        logger.error(f"주문 생성 실패: {new_resp.error_msg} ({new_resp.error_name})")
        return

    order = new_resp.block
    logger.info(f"주문 생성됨: order_id={order.order_id} order_type={order.order_type}")

    time.sleep(1)

    # 2. 주문 상태 확인
    detail_resp = bithumb.주문().개별주문조회(
        bithumb_order_detail.OrderDetailInBlock(uuid=order.order_id)
    ).req()

    if detail_resp.error_msg or detail_resp.block is None:
        logger.error(f"주문 조회 실패: {detail_resp.error_msg}")
    else:
        logger.info(f"주문 상태: {detail_resp.block.state}")

    # 3. 주문 취소
    cancel_resp = bithumb.주문().주문취소(
        bithumb_order_cancel.OrderCancelInBlock(order_id=order.order_id)
    ).req()

    if cancel_resp.error_msg or cancel_resp.block is None:
        logger.error(f"주문 취소 실패: {cancel_resp.error_msg} ({cancel_resp.error_name})")
        return

    logger.info(f"주문 취소됨: order_id={cancel_resp.block.order_id} created_at={cancel_resp.block.created_at}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not ALLOW_REAL_ORDER:
        logger.warning(
            "ALLOW_REAL_ORDER가 False입니다. 실제 주문을 생성하려면 "
            "스크립트 상단의 ALLOW_REAL_ORDER를 True로 변경하고, "
            "MARKET/ORDER_PRICE/ORDER_VOLUME 값을 확인한 뒤 실행하세요."
        )
    elif not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        run_lifecycle()
