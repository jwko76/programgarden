"""KIS 계좌 잔고 조회 예제.

환경변수 (.env):
    KIS_APPKEY, KIS_APPSECRET, KIS_ACCOUNT_NO (계좌번호 앞 8자리)
    KIS_PAPER=1 이면 모의투자 서버 사용
"""

import logging
import os

from dotenv import load_dotenv

from programgarden_finance import Kis, kis_inquire_psbl_order

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def make_client() -> Kis:
    kis = Kis(paper_trading=os.getenv("KIS_PAPER", "1") == "1")
    kis.login(
        appkey=os.getenv("KIS_APPKEY"),
        appsecretkey=os.getenv("KIS_APPSECRET"),
        account_no=os.getenv("KIS_ACCOUNT_NO"),
    )
    return kis


def test_inquire_balance():
    """주식잔고조회 (TTTC8434R/VTTC8434R) — 계좌번호는 로그인 값 자동 사용"""
    kis = make_client()

    response = kis.계좌().잔고().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.msg_cd})")
        return

    summary = response.block2
    logger.info(f"예수금: {summary.dnca_tot_amt}원 / 총평가: {summary.tot_evlu_amt}원")
    logger.info(f"평가손익 합계: {summary.evlu_pfls_smtl_amt}원")

    for position in response.blocks or []:
        logger.info(
            f"{position.prdt_name}({position.pdno}): {position.hldg_qty}주 "
            f"@ {position.pchs_avg_pric} → 현재 {position.prpr} "
            f"(손익 {position.evlu_pfls_amt}원 / {position.evlu_pfls_rt}%)"
        )


def test_inquire_psbl_order():
    """매수가능조회 (TTTC8908R/VTTC8908R)"""
    kis = make_client()

    response = kis.계좌().주문가능(
        kis_inquire_psbl_order.InquirePsblOrderInBlock(
            cano="", pdno="005930", ord_unpr="0", ord_dvsn="01",
        )
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.msg_cd})")
        return

    b = response.block
    logger.info(f"주문가능현금: {b.ord_psbl_cash}원 / 최대매수수량: {b.max_buy_qty}주")


if __name__ == "__main__":
    test_inquire_balance()
    test_inquire_psbl_order()
