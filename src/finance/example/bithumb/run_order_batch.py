"""빗썸 다건 주문 생성 -> 조회 -> 다건 취소 예제입니다.

[!] 주의: ALLOW_REAL_ORDER를 True로 변경하면 실제 자금으로 매수 주문을 생성합니다.
체결 위험을 낮추기 위해 현재가보다 충분히 낮은 한정가로 최소 주문금액(5,000원)
수준의 매수 주문을 여러 건 생성한 뒤 즉시 다건 취소하지만, 시세 변동에 따라
체결될 수 있습니다. 실행 전 MARKET/ORDERS 값을 반드시 확인하세요.
"""

import logging
import os
import time
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_ticker,
    bithumb_order_new_batch,
    bithumb_order_cancel_batch,
)

logger = logging.getLogger(__name__)

load_dotenv()

# 실제 주문을 생성하려면 True로 변경하세요. (실제 자금 사용)
ALLOW_REAL_ORDER = False

MARKET = "KRW-BTC"
# 각 주문은 price x volume >= 5,000원이 되도록 설정합니다. (현재가보다 충분히 낮은 한정가)
ORDERS = [
    {"price": "80000000", "volume": "0.00008"},  # 약 6,400원
    {"price": "75000000", "volume": "0.00008"},  # 약 6,000원
]


def _login() -> Bithumb:
    bithumb = Bithumb()
    bithumb.로그인(
        accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
        secretkey=os.getenv("BITHUMB_SECRET_KEY"),
    )
    return bithumb


def run_batch_lifecycle():
    """다건 매수 주문 생성 -> 상태 조회 -> 다건 취소"""

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

    for order in ORDERS:
        if float(order["price"]) >= current_price:
            logger.error("ORDERS의 price가 현재가보다 낮아야 체결 위험이 줄어듭니다. 값을 확인하세요.")
            return

    # 1. 다건 매수 주문 생성 (지정가)
    batch_resp = bithumb.주문().다건주문(
        bithumb_order_new_batch.OrderNewBatchInBlock(
            batch_orders=[
                bithumb_order_new_batch.BatchOrderItem(
                    market=MARKET,
                    side="bid",
                    order_type="limit",
                    price=order["price"],
                    volume=order["volume"],
                )
                for order in ORDERS
            ]
        )
    ).req()

    if batch_resp.error_msg or batch_resp.block is None:
        logger.error(f"다건 주문 생성 실패: {batch_resp.error_msg} ({batch_resp.error_name})")
        return

    order_ids = []
    for item in batch_resp.block.batch_orders_response:
        if item.order_id:
            logger.info(f"주문 생성됨: order_id={item.order_id} order_type={item.order_type}")
            order_ids.append(item.order_id)
        else:
            logger.warning(f"주문 생성 실패: {item.name} - {item.message}")

    if not order_ids:
        logger.error("생성된 주문이 없어 이후 단계를 진행하지 않습니다.")
        return

    time.sleep(1)

    # 2. 주문 상태 확인
    orders_resp = bithumb.주문().주문리스트조회().req()
    if orders_resp.error_msg:
        logger.error(f"주문 조회 실패: {orders_resp.error_msg}")
    else:
        for o in orders_resp.blocks or []:
            if o.uuid in order_ids:
                logger.info(f"주문 상태: order_id={o.uuid} state={o.state}")

    # 3. 다건 주문 취소
    cancel_resp = bithumb.주문().다건주문취소(
        bithumb_order_cancel_batch.OrderCancelBatchInBlock(order_ids=order_ids)
    ).req()

    if cancel_resp.error_msg or cancel_resp.block is None:
        logger.error(f"다건 주문 취소 실패: {cancel_resp.error_msg} ({cancel_resp.error_name})")
        return

    for item in cancel_resp.block.success:
        logger.info(f"주문 취소됨: order_id={item.order_id} created_at={item.created_at}")
    for item in cancel_resp.block.fail:
        logger.warning(f"주문 취소 실패: order_id={item.order_id} error={item.error}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not ALLOW_REAL_ORDER:
        logger.warning(
            "ALLOW_REAL_ORDER가 False입니다. 실제 주문을 생성하려면 "
            "스크립트 상단의 ALLOW_REAL_ORDER를 True로 변경하고, "
            "MARKET/ORDERS 값을 확인한 뒤 실행하세요."
        )
    elif not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        run_batch_lifecycle()
