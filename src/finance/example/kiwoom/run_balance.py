"""키움증권 계좌 조회 예제: 잔고·주문가능금액.

환경변수 (.env):
    KIWOOM_APPKEY, KIWOOM_APPSECRET, KIWOOM_ACCOUNT_NO
    KIWOOM_PAPER=1 이면 모의투자 서버(mockapi.kiwoom.com) 사용
"""

import logging
import os

from dotenv import load_dotenv

from programgarden_finance import Kiwoom, kiwoom_inquire_psbl_order

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def make_client() -> Kiwoom:
    kiwoom = Kiwoom(paper_trading=os.getenv("KIWOOM_PAPER", "1") == "1")
    kiwoom.login(
        appkey=os.getenv("KIWOOM_APPKEY"),
        appsecretkey=os.getenv("KIWOOM_APPSECRET"),
        account_no=os.getenv("KIWOOM_ACCOUNT_NO"),
    )
    return kiwoom


def test_inquire_balance():
    """계좌평가잔고내역요청 (api-id kt00018) — 계좌번호 자동 채움"""
    kiwoom = make_client()

    response = kiwoom.계좌().잔고().req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} (return_code={response.return_code})")
        return

    s = response.block
    logger.info(f"예수금 {s.entr} / 총매입 {s.tot_pur_amt} / 총평가 {s.tot_evlt_amt} / "
                f"평가손익 {s.tot_evlt_pl} ({s.tot_pl_rt}%)")
    for p in response.blocks or []:
        logger.info(f"  {p.stk_cd}({p.stk_nm}) {p.rmnd_qty}주 매입가 {p.pur_pric} "
                    f"현재가 {p.cur_prc} 평가손익 {p.evltv_prft}")


def test_inquire_psbl_order():
    """주문인출가능금액요청 (api-id kt00010)"""
    kiwoom = make_client()

    response = kiwoom.계좌().주문가능(
        kiwoom_inquire_psbl_order.InquirePsblOrderInBlock(
            acnt_no="",  # 로그인 시 등록한 계좌 자동 사용
            stk_cd="005930",
            uv="60000",
        )
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} (return_code={response.return_code})")
        return

    logger.info(f"주문가능 응답: {response.block}")


if __name__ == "__main__":
    test_inquire_balance()
    test_inquire_psbl_order()
