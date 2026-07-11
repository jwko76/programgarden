"""KIS 실전투자 주문 라이프사이클 검증: 하한가 지정가 매수 1주 → 즉시 취소.

⚠️ 실전 계좌에 실제 주문이 접수됩니다. 반드시 내용을 이해하고 실행하세요.

안전장치:
    - KIS_PAPER=0(실전)이 아니면 거부 (모의투자는 run_order_lifecycle.py 사용)
    - 환경변수 KIS_LIVE_ORDER_CONFIRM=YES 가 없으면 거부
    - 주문가는 당일 하한가(stck_llam) 지정가 → 정상 장중에는 체결되지 않음
    - 수량 1주 고정, 접수 직후 전량 취소

환경변수 (.env):
    KIS_APPKEY, KIS_APPSECRET, KIS_ACCOUNT_NO
    KIS_PAPER=0
    KIS_LIVE_ORDER_CONFIRM=YES (실행 시에만 셸에서 지정 권장, .env 저장 비권장)
    KIS_LIVE_ORDER_PDNO (선택, 기본 088350 한화생명)
"""

import logging
import os
import time

from dotenv import load_dotenv

from programgarden_finance import (
    Kis,
    kis_inquire_price,
    kis_order_cash,
    kis_order_rvsecncl,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def main():
    if os.getenv("KIS_PAPER", "1") != "0":
        logger.error("이 스크립트는 실전투자(KIS_PAPER=0) 검증 전용입니다. 모의투자는 run_order_lifecycle.py를 사용하세요.")
        return
    if os.getenv("KIS_LIVE_ORDER_CONFIRM") != "YES":
        logger.error("실주문 안전장치: KIS_LIVE_ORDER_CONFIRM=YES 환경변수를 지정해야 실행됩니다.")
        return

    pdno = os.getenv("KIS_LIVE_ORDER_PDNO", "088350")

    kis = Kis(paper_trading=False)
    kis.login(
        appkey=os.getenv("KIS_APPKEY"),
        appsecretkey=os.getenv("KIS_APPSECRET"),
        account_no=os.getenv("KIS_ACCOUNT_NO"),
    )

    # 1) 현재가 조회 → 하한가를 주문가로 사용 (가격밴드 안이면서 체결 가능성 최소화)
    price_resp = kis.시세().현재가(
        kis_inquire_price.InquirePriceInBlock(fid_input_iscd=pdno)
    ).req()
    if price_resp.error_msg:
        logger.error(f"현재가 조회 실패: {price_resp.error_msg} ({price_resp.msg_cd})")
        return

    cur = price_resp.block.stck_prpr
    llam = price_resp.block.stck_llam
    if not llam or llam == "0":
        logger.error(f"하한가 정보를 얻지 못했습니다 (현재가 {cur}). 중단합니다.")
        return
    logger.info(f"{pdno} 현재가 {cur}원 / 주문가(하한가) {llam}원 / 수량 1주")

    # 2) 하한가 지정가 매수 1주
    order_resp = kis.주문().현금매수(
        kis_order_cash.OrderCashBodyBlock(
            cano="",  # 로그인 계좌 자동 사용
            pdno=pdno,
            ord_dvsn="00",   # 지정가
            ord_qty="1",
            ord_unpr=llam,
        )
    ).req()
    if order_resp.error_msg:
        logger.error(f"주문 실패: {order_resp.error_msg} ({order_resp.msg_cd})")
        return

    order_no = order_resp.block.odno
    org_no = order_resp.block.krx_fwdg_ord_orgno
    logger.info(f"매수 주문 접수: 주문번호 {order_no} (조직번호 {org_no}, 시각 {order_resp.block.ord_tmd})")

    time.sleep(2)

    # 3) 전량 취소
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
        logger.error(
            f"취소 실패: {cancel_resp.error_msg} ({cancel_resp.msg_cd}) — "
            f"HTS/MTS에서 주문번호 {order_no} 수동 취소 필요!"
        )
        return

    logger.info(f"주문 취소 접수: {cancel_resp.block.odno} ({cancel_resp.msg1})")
    logger.info("라이프사이클 검증 완료: 매수 접수 → 취소 접수")


if __name__ == "__main__":
    main()
