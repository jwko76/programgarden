import logging
import os
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_deposits,
    bithumb_withdraws,
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


def test_accounts():
    """전체 자산 조회 테스트"""

    bithumb = _login()

    response = bithumb.계좌().전체자산조회().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(f"{item.currency} | 보유: {item.balance} | 사용중: {item.locked} | 평단가: {item.avg_buy_price}")


def test_wallet_status():
    """화폐별 입출금 현황 조회 테스트"""

    bithumb = _login()

    response = bithumb.계좌().입출금현황().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in (response.blocks or [])[:10]:
        logger.info(f"{item.currency} ({item.net_type}) | {item.wallet_state} | 블록상태: {item.block_state}")


def test_deposits():
    """입금 리스트 조회 테스트"""

    bithumb = _login()

    response = bithumb.계좌().입금리스트조회(
        bithumb_deposits.DepositsInBlock(limit=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    if not response.blocks:
        logger.info("입금 내역이 없습니다.")
        return

    for item in response.blocks:
        logger.info(f"{item.currency} | {item.state} | {item.amount} | {item.created_at}")


def test_withdraws():
    """출금 리스트 조회 테스트"""

    bithumb = _login()

    response = bithumb.계좌().출금리스트조회(
        bithumb_withdraws.WithdrawsInBlock(limit=5)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    if not response.blocks:
        logger.info("출금 내역이 없습니다.")
        return

    for item in response.blocks:
        logger.info(f"{item.currency} | {item.state} | {item.amount} | {item.created_at}")


def test_api_keys():
    """API 키 리스트 조회 테스트"""

    bithumb = _login()

    response = bithumb.계좌().API키리스트조회().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in response.blocks or []:
        logger.info(f"{item.access_key} | 만료일시: {item.expire_at}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        test_accounts()
        test_wallet_status()
        test_deposits()
        test_withdraws()
        test_api_keys()
