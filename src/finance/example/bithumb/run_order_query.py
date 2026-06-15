import logging
import os
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_orders_chance,
    bithumb_order_detail,
    bithumb_orders,
)

logger = logging.getLogger(__name__)

load_dotenv()


def _login() -> Bithumb:
    bithumb = Bithumb()
    bithumb.로그인(
        accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
        secretkey=os.getenv("BITHUMB_SECRET_KEY"),
    )
    return bithumb


def test_orders_chance():
    """주문 가능 정보 조회 테스트"""

    bithumb = _login()

    response = bithumb.주문().주문가능정보(
        bithumb_orders_chance.OrdersChanceInBlock(market="KRW-BTC")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    block = response.block
    if block is None:
        logger.info("주문 가능 정보 없음")
        return

    logger.info(f"마켓: {block.market.id} ({block.market.name}) | 상태: {block.market.state}")
    logger.info(f"매수 수수료: {block.bid_fee} | 매도 수수료: {block.ask_fee}")
    logger.info(f"매수 가능 금액: {block.bid_account.balance} {block.bid_account.currency}")
    logger.info(f"매도 가능 수량: {block.ask_account.balance} {block.ask_account.currency}")


def test_orders():
    """주문 리스트 조회 테스트"""

    bithumb = _login()

    response = bithumb.주문().주문리스트조회(
        bithumb_orders.OrdersInBlock(market="KRW-BTC", limit=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    if not response.blocks:
        logger.info("주문 내역이 없습니다.")
        return

    for item in response.blocks:
        logger.info(f"{item.uuid} | {item.side} {item.ord_type} | {item.state} | {item.price} x {item.volume}")


def test_order_detail(uuid: str):
    """개별 주문 조회 테스트 (uuid 필요)"""

    bithumb = _login()

    response = bithumb.주문().개별주문조회(
        bithumb_order_detail.OrderDetailInBlock(uuid=uuid)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    block = response.block
    if block is None:
        logger.info("주문 정보 없음")
        return

    logger.info(f"{block.uuid} | {block.side} {block.ord_type} | {block.state}")
    for trade in block.trades:
        logger.info(f"  체결: {trade.price} x {trade.volume} ({trade.created_at})")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        test_orders_chance()
        test_orders()
        # 개별 주문 조회는 uuid가 필요하므로, 위 주문 리스트에서 확인한 uuid로 직접 호출하세요.
        # test_order_detail(uuid="9e8f8eba-7050-4837-82c3-768e2e63b58a")
