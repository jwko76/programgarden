"""키움증권 주문 라이프사이클 예제: 지정가 매수 → 취소 (모의투자 권장).

환경변수 (.env):
    KIWOOM_APPKEY, KIWOOM_APPSECRET, KIWOOM_ACCOUNT_NO
    KIWOOM_PAPER=1 이면 모의투자 서버(mockapi.kiwoom.com) 사용

주의: KIWOOM_PAPER=0 이면 실계좌에 실제 주문이 전송됩니다.
      체결 방지를 위해 현재가보다 충분히 낮은 지정가를 사용하세요.
"""

import logging
import os

from dotenv import load_dotenv

from programgarden_finance import Kiwoom, kiwoom_order_cash, kiwoom_order_rvsecncl

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

SYMBOL = "005930"
LIMIT_PRICE = "50000"  # 체결 방지용 저가 지정가
QUANTITY = "1"


def make_client() -> Kiwoom:
    kiwoom = Kiwoom(paper_trading=os.getenv("KIWOOM_PAPER", "1") == "1")
    kiwoom.login(
        appkey=os.getenv("KIWOOM_APPKEY"),
        appsecretkey=os.getenv("KIWOOM_APPSECRET"),
        account_no=os.getenv("KIWOOM_ACCOUNT_NO"),
    )
    return kiwoom


def main():
    kiwoom = make_client()
    order_api = kiwoom.주문()

    # 1) 지정가 매수 (api-id kt10000)
    buy = order_api.현금매수(
        kiwoom_order_cash.OrderCashBodyBlock(
            acnt_no="",  # 로그인 시 등록한 계좌 자동 사용
            stk_cd=SYMBOL,
            ord_qty=QUANTITY,
            ord_uv=LIMIT_PRICE,
            trde_tp="0",  # 지정가로 추정 (TODO(실계좌 검증))
        )
    ).req()

    if buy.error_msg:
        logger.error(f"매수 실패: {buy.error_msg} (return_code={buy.return_code})")
        return
    order_no = buy.block.ord_no
    logger.info(f"매수 주문 접수: order_no={order_no}")

    # 2) 취소 (api-id kt10003) — 키움은 취소에도 종목코드가 필수
    cancel = order_api.취소(
        kiwoom_order_rvsecncl.OrderRvsecnclBodyBlock(
            acnt_no="",
            orig_ord_no=order_no,
            stk_cd=SYMBOL,
            ord_qty="0",  # 잔량 전부로 추정 (TODO(실계좌 검증))
            ord_uv="0",
        )
    ).req()

    if cancel.error_msg:
        logger.error(f"취소 실패: {cancel.error_msg} (return_code={cancel.return_code})")
        return
    logger.info(f"취소 접수: receipt={getattr(cancel.block, 'ord_no', None)}")


if __name__ == "__main__":
    main()
