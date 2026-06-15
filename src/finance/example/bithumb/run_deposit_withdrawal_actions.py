"""빗썸 입출금 관리 - 자금 이동성 엔드포인트 5개 예제입니다.

!!! 경고 !!!
이 파일에 포함된 함수들은 실제 자산(원화/코인)의 입출금에 영향을 줄 수 있는
엔드포인트를 호출합니다. 각 함수 상단의 ``ALLOW_*`` 플래그가 기본적으로
``False``로 설정되어 있어, 플래그를 ``True``로 바꾸지 않는 한 어떤 함수도
실제 요청을 보내지 않고 즉시 종료합니다.

- 입금주소생성요청 (#6): 코인 입금 주소를 새로 생성합니다. 한 번 생성한
  주소는 재발급 시 기존 주소가 만료될 수 있으니 신중히 사용하세요.
- 원화입금 (#9): 카카오페이 인증(two_factor_type="kakao")이 필요한 엔드포인트로,
  API만으로는 2FA를 완료할 수 없어 ``ALLOW_DEPOSIT_KRW=True``로 설정해도
  실제로는 인증 단계에서 실패합니다. 코드 형태 참고용입니다.
- 가상자산출금요청 (#12): **실제로 코인이 외부 주소로 전송됩니다.** 절대
  운영 자산에 대해 테스트하지 마세요.
- 가상자산출금취소 (#13): #12로 생성한 출금 요청을 취소합니다. 이미
  처리(DONE)된 출금은 취소할 수 없습니다.
- 원화출금요청 (#14): 카카오페이 인증이 필요하여 #9와 동일한 사유로
  ``ALLOW_WITHDRAW_KRW=True``로 설정해도 인증 단계에서 실패합니다.

실행해도 안전한 조회성 엔드포인트는 ``run_deposit_withdrawal_query.py``를
참고하세요.
"""

import logging
import os
from dotenv import load_dotenv
from programgarden_finance import (
    Bithumb,
    bithumb_deposit_address_generate,
    bithumb_deposit_krw,
    bithumb_withdraw_coin,
    bithumb_withdraw_coin_cancel,
    bithumb_withdraw_krw,
)

logger = logging.getLogger(__name__)

load_dotenv()


# 모든 플래그는 기본값 False입니다. 의미를 정확히 이해하지 못한 상태에서
# True로 변경하지 마세요.
ALLOW_DEPOSIT_ADDRESS_GENERATE = False
ALLOW_DEPOSIT_KRW = False
ALLOW_WITHDRAW_COIN = False
ALLOW_WITHDRAW_COIN_CANCEL = False
ALLOW_WITHDRAW_KRW = False


def _login() -> Bithumb:
    bithumb = Bithumb()
    bithumb.로그인(
        accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
        secretkey=os.getenv("BITHUMB_SECRET_KEY"),
    )
    return bithumb


def test_deposit_address_generate():
    """입금 주소 생성 요청 예제 (#6)

    ALLOW_DEPOSIT_ADDRESS_GENERATE=True로 설정하면 실제로 새 입금 주소
    생성을 요청합니다. 코인/네트워크에 따라 즉시 발급되지 않고 비동기로
    처리될 수 있습니다.
    """

    if not ALLOW_DEPOSIT_ADDRESS_GENERATE:
        logger.warning("ALLOW_DEPOSIT_ADDRESS_GENERATE=False 이므로 요청을 건너뜁니다.")
        return

    bithumb = _login()

    response = bithumb.입출금().입금주소생성요청(
        bithumb_deposit_address_generate.DepositAddressGenerateInBlock(currency="BTC", net_type="BTC")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"입금주소 생성 결과: {response.block}")


def test_deposit_krw():
    """원화 입금 예제 (#9)

    !!! 카카오페이 2FA가 필요하여 API만으로는 완료할 수 없습니다 !!!
    ALLOW_DEPOSIT_KRW=True로 설정하더라도 실제 응답은 인증 관련 오류를
    반환할 가능성이 높습니다. 요청 형태 참고용 코드입니다.
    """

    if not ALLOW_DEPOSIT_KRW:
        logger.warning("ALLOW_DEPOSIT_KRW=False 이므로 요청을 건너뜁니다.")
        return

    bithumb = _login()

    response = bithumb.입출금().원화입금(
        bithumb_deposit_krw.DepositKrwInBlock(amount="10000", two_factor_type="kakao")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"원화입금 결과: {response.block}")


def test_withdraw_coin():
    """가상자산 출금 요청 예제 (#12)

    !!! 위험: 실제 코인이 지정한 주소로 전송됩니다 !!!
    ALLOW_WITHDRAW_COIN=True로 설정하기 전에 currency/net_type/amount/address
    값을 반드시 본인 소유의 검증된 값으로 교체하세요.
    """

    if not ALLOW_WITHDRAW_COIN:
        logger.warning("ALLOW_WITHDRAW_COIN=False 이므로 요청을 건너뜁니다.")
        return

    bithumb = _login()

    response = bithumb.입출금().가상자산출금요청(
        bithumb_withdraw_coin.WithdrawCoinInBlock(
            currency="BTC",
            net_type="BTC",
            amount="0.001",
            address="REPLACE_WITH_YOUR_OWN_ADDRESS",
        )
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"가상자산출금 결과: {response.block}")


def test_withdraw_coin_cancel():
    """가상자산 출금 취소 예제 (#13)

    test_withdraw_coin()으로 생성한 출금의 withdrawal_id가 필요합니다.
    이미 DONE 상태로 처리된 출금은 취소할 수 없습니다.
    """

    if not ALLOW_WITHDRAW_COIN_CANCEL:
        logger.warning("ALLOW_WITHDRAW_COIN_CANCEL=False 이므로 요청을 건너뜁니다.")
        return

    bithumb = _login()

    response = bithumb.입출금().가상자산출금취소(
        bithumb_withdraw_coin_cancel.WithdrawCoinCancelInBlock(withdrawal_id="REPLACE_WITH_WITHDRAWAL_ID")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"가상자산출금취소 결과: {response.block}")


def test_withdraw_krw():
    """원화 출금 요청 예제 (#14)

    !!! 카카오페이 2FA가 필요하여 API만으로는 완료할 수 없습니다 !!!
    ALLOW_WITHDRAW_KRW=True로 설정하더라도 실제 응답은 인증 관련 오류를
    반환할 가능성이 높습니다. 요청 형태 참고용 코드입니다.
    """

    if not ALLOW_WITHDRAW_KRW:
        logger.warning("ALLOW_WITHDRAW_KRW=False 이므로 요청을 건너뜁니다.")
        return

    bithumb = _login()

    response = bithumb.입출금().원화출금요청(
        bithumb_withdraw_krw.WithdrawKrwInBlock(amount="10000", two_factor_type="kakao")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.error_name})")
        return

    logger.info(f"원화출금 결과: {response.block}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if not os.getenv("BITHUMB_ACCESS_KEY") or not os.getenv("BITHUMB_SECRET_KEY"):
        logger.error(".env에 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY를 설정해야 합니다.")
    else:
        test_deposit_address_generate()
        test_deposit_krw()
        test_withdraw_coin()
        test_withdraw_coin_cancel()
        test_withdraw_krw()
