"""KIS 주문 라이프사이클 예제: 지정가 매수 → 취소 (모의투자 전용).

체결 가능성이 낮은 가격으로 지정가 매수를 넣고 즉시 취소합니다.

환경변수 (.env):
    KIS_APPKEY, KIS_APPSECRET, KIS_ACCOUNT_NO
    KIS_PAPER=1 (이 예제는 안전을 위해 모의투자가 아니면 실행을 거부합니다)
"""

import logging
import os
import time

from dotenv import load_dotenv

from programgarden_finance import Kis, kis_order_cash, kis_order_rvsecncl

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    if os.getenv("KIS_PAPER", "1") != "1":
        logger.error("이 예제는 모의투자(KIS_PAPER=1)에서만 실행할 수 있습니다.")
        return

    kis = Kis(paper_trading=True)
    kis.login(
        appkey=os.getenv("KIS_APPKEY"),
        appsecretkey=os.getenv("KIS_APPSECRET"),
        account_no=os.getenv("KIS_ACCOUNT_NO"),
    )

    # 1) 현재가보다 충분히 낮은 가격으로 지정가 매수 (체결 방지)
    order_resp = kis.주문().현금매수(
        kis_order_cash.OrderCashBodyBlock(
            cano="",  # 로그인 계좌 자동 사용
            pdno="005930",
            ord_dvsn="00",   # 지정가
            ord_qty="1",
            ord_unpr="50000",
        )
    ).req()

    if order_resp.error_msg:
        logger.error(f"주문 실패: {order_resp.error_msg} ({order_resp.msg_cd})")
        return

    order_no = order_resp.block.odno
    org_no = order_resp.block.krx_fwdg_ord_orgno
    logger.info(f"매수 주문 접수: 주문번호 {order_no} (조직번호 {org_no}, 시각 {order_resp.block.ord_tmd})")

    time.sleep(2)

    # 2) 주문 취소 (잔량 전부)
    cancel_resp = kis.주문().정정취소(
        kis_order_rvsecncl.OrderRvsecnclBodyBlock(
            cano="",
            orgn_odno=order_no,
            krx_fwdg_ord_orgno=org_no or "",
            rvse_cncl_dvsn_cd="02",  # 취소
            qty_all_ord_yn="Y",
        )
    ).req()

    if cancel_resp.error_msg:
        logger.error(f"취소 실패: {cancel_resp.error_msg} ({cancel_resp.msg_cd})")
        return

    logger.info(f"주문 취소 접수: {cancel_resp.block.odno} ({cancel_resp.msg1})")


if __name__ == "__main__":
    main()
