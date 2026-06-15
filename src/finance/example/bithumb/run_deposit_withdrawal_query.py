"""빗썸 입출금 관리 - 조회성 엔드포인트 8개 예제입니다.

전부 읽기 전용(GET) 엔드포인트이므로 ``.env``에 BITHUMB_ACCESS_KEY/SECRET_KEY가
설정되어 있으면 그대로 실행해도 안전합니다.
"""

import logging
import os
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_deposit_address,
    bithumb_deposit_detail,
    bithumb_withdraw_detail,
    bithumb_withdraws_chance,
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


def test_deposit_address():
    """개별 입금 주소 조회 테스트 (#7)"""

    bithumb = _login()

    response = bithumb.입출금().개별입금주소조회(
        bithumb_deposit_address.DepositAddressInBlock(currency="BTC", net_type="BTC")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"BTC(BTC) 입금주소: {response.block.deposit_address}")


def test_deposit_addresses():
    """전체 입금 주소 조회 테스트 (#8)"""

    bithumb = _login()

    response = bithumb.입출금().전체입금주소조회().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    for item in (response.blocks or [])[:10]:
        logger.info(f"{item.currency} ({item.net_type}) | {item.deposit_address}")


def test_deposits_krw():
    """원화 입금 리스트 조회 테스트 (#10)"""

    bithumb = _login()

    response = bithumb.입출금().원화입금리스트조회().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    if not response.blocks:
        logger.info("원화 입금 내역이 없습니다.")
        return

    for item in response.blocks:
        logger.info(f"{item.uuid} | {item.state} | {item.amount}원 | {item.created_at}")


def test_deposit_detail():
    """개별 입금 조회 테스트 (#11, 원화 입금 내역 중 첫 건 사용)"""

    bithumb = _login()

    deposits_resp = bithumb.입출금().원화입금리스트조회().req()
    if deposits_resp.error_msg:
        logger.error(f"원화 입금 리스트 조회 실패: {deposits_resp.error_msg} ({deposits_resp.error_name})")
        return

    if not deposits_resp.blocks:
        logger.info("조회할 원화 입금 내역이 없습니다.")
        return

    first = deposits_resp.blocks[0]
    response = bithumb.입출금().개별입금조회(
        bithumb_deposit_detail.DepositDetailInBlock(currency=first.currency, uuid=first.uuid)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"입금 상세: uuid={response.block.uuid} state={response.block.state} amount={response.block.amount}")


def test_withdraws_krw():
    """원화 출금 리스트 조회 테스트 (#15)"""

    bithumb = _login()

    response = bithumb.입출금().원화출금리스트조회().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    if not response.blocks:
        logger.info("원화 출금 내역이 없습니다.")
        return

    for item in response.blocks:
        logger.info(f"{item.uuid} | {item.state} | {item.amount}원 | {item.created_at}")


def test_withdraw_detail():
    """개별 출금 조회 테스트 (#16, 원화 출금 내역 중 첫 건 사용)"""

    bithumb = _login()

    withdraws_resp = bithumb.입출금().원화출금리스트조회().req()
    if withdraws_resp.error_msg:
        logger.error(f"원화 출금 리스트 조회 실패: {withdraws_resp.error_msg} ({withdraws_resp.error_name})")
        return

    if not withdraws_resp.blocks:
        logger.info("조회할 원화 출금 내역이 없습니다.")
        return

    first = withdraws_resp.blocks[0]
    response = bithumb.입출금().개별출금조회(
        bithumb_withdraw_detail.WithdrawDetailInBlock(currency=first.currency, uuid=first.uuid)
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"출금 상세: uuid={response.block.uuid} state={response.block.state} amount={response.block.amount}")


def test_withdraws_chance():
    """출금 가능 정보 조회 테스트 (#17)"""

    bithumb = _login()

    response = bithumb.입출금().출금가능정보(
        bithumb_withdraws_chance.WithdrawsChanceInBlock(currency="BTC", net_type="BTC")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    limit = response.block.withdraw_limit
    logger.info(
        f"BTC 출금 가능 여부: {limit.can_withdraw} | 1회한도: {limit.onetime} | "
        f"1일잔여한도: {limit.remaining_daily} | 보유: {response.block.account.balance}"
    )


def test_withdraw_coin_addresses():
    """출금 허용 주소 리스트 조회 테스트 (#18)"""

    bithumb = _login()

    response = bithumb.입출금().출금허용주소리스트조회().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    if not response.blocks:
        logger.info("등록된 출금 허용 주소가 없습니다.")
        return

    for item in response.blocks:
        logger.info(f"{item.currency} ({item.net_type}) | {item.withdraw_address} | {item.exchange_name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        test_deposit_address()
        test_deposit_addresses()
        test_deposits_krw()
        test_deposit_detail()
        test_withdraws_krw()
        test_withdraw_detail()
        test_withdraws_chance()
        test_withdraw_coin_addresses()
