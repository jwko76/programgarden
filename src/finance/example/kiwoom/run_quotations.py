"""키움증권 시세 조회 예제: 현재가·호가·일봉.

환경변수 (.env):
    KIWOOM_APPKEY, KIWOOM_APPSECRET (키움 OpenAPI에서 발급)
    KIWOOM_PAPER=1 이면 모의투자 서버(mockapi.kiwoom.com) 사용
"""

import logging
import os

from dotenv import load_dotenv

from programgarden_finance import (
    Kiwoom,
    kiwoom_inquire_price,
    kiwoom_inquire_asking_price,
    kiwoom_inquire_daily_itemchartprice,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def make_client() -> Kiwoom:
    kiwoom = Kiwoom(paper_trading=os.getenv("KIWOOM_PAPER", "1") == "1")
    kiwoom.login(
        appkey=os.getenv("KIWOOM_APPKEY"),
        appsecretkey=os.getenv("KIWOOM_APPSECRET"),
    )
    return kiwoom


def test_inquire_price():
    """종목기본정보요청 — 현재가 포함 (api-id ka10001)"""
    kiwoom = make_client()

    response = kiwoom.시세().현재가(
        kiwoom_inquire_price.InquirePriceInBlock(stk_cd="005930")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} (return_code={response.return_code})")
        return

    b = response.block
    logger.info(f"005930({b.stk_nm}) 현재가: {b.cur_prc}원 ({b.pred_pre} / {b.flu_rt}%)")
    logger.info(f"시가 {b.open_pric} / 고가 {b.high_pric} / 저가 {b.low_pric} / 거래량 {b.trde_qty}")


def test_inquire_asking_price():
    """주식호가요청 (api-id ka10004)"""
    kiwoom = make_client()

    response = kiwoom.시세().호가(
        kiwoom_inquire_asking_price.InquireAskingPriceInBlock(stk_cd="005930")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} (return_code={response.return_code})")
        return

    b = response.block
    logger.info(f"매도1호가 {b.sel_1th_pre_req_pric}({b.sel_1th_pre_req_qty}) / "
                f"매수1호가 {b.buy_1th_pre_req_pric}({b.buy_1th_pre_req_qty})")
    logger.info(f"총 매도잔량 {b.tot_sel_req} / 총 매수잔량 {b.tot_buy_req}")


def test_inquire_daily_candles():
    """주식일봉차트조회요청 (api-id ka10081)"""
    kiwoom = make_client()

    response = kiwoom.시세().일봉(
        kiwoom_inquire_daily_itemchartprice.InquireDailyItemChartPriceInBlock(
            stk_cd="005930",
            base_dt="20260717",
        )
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} (return_code={response.return_code})")
        return

    logger.info(f"수신 캔들 수: {len(response.blocks or [])}")
    for candle in (response.blocks or [])[:5]:
        logger.info(
            f"{candle.dt}: 시 {candle.open_pric} 고 {candle.high_pric} "
            f"저 {candle.low_pric} 종 {candle.cur_prc} 량 {candle.trde_qty}"
        )


if __name__ == "__main__":
    test_inquire_price()
    test_inquire_asking_price()
    test_inquire_daily_candles()
