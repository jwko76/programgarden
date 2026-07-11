"""KIS 시세 조회 예제: 현재가·호가·일봉.

환경변수 (.env):
    KIS_APPKEY, KIS_APPSECRET (KIS Developers에서 발급)
    KIS_PAPER=1 이면 모의투자 서버 사용
"""

import logging
import os

from dotenv import load_dotenv

from programgarden_finance import (
    Kis,
    kis_inquire_price,
    kis_inquire_asking_price,
    kis_inquire_daily_itemchartprice,
)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


def make_client() -> Kis:
    kis = Kis(paper_trading=os.getenv("KIS_PAPER", "1") == "1")
    kis.login(
        appkey=os.getenv("KIS_APPKEY"),
        appsecretkey=os.getenv("KIS_APPSECRET"),
    )
    return kis


def test_inquire_price():
    """주식현재가 시세 조회 (FHKST01010100)"""
    kis = make_client()

    response = kis.시세().현재가(
        kis_inquire_price.InquirePriceInBlock(fid_input_iscd="005930")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.msg_cd})")
        return

    b = response.block
    logger.info(f"{b.hts_kor_isnm} 현재가: {b.stck_prpr}원 ({b.prdy_vrss} / {b.prdy_ctrt}%)")
    logger.info(f"시가 {b.stck_oprc} / 고가 {b.stck_hgpr} / 저가 {b.stck_lwpr} / 거래량 {b.acml_vol}")


def test_inquire_asking_price():
    """호가/예상체결 조회 (FHKST01010200)"""
    kis = make_client()

    response = kis.시세().호가(
        kis_inquire_asking_price.InquireAskingPriceInBlock(fid_input_iscd="005930")
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.msg_cd})")
        return

    b = response.block1
    logger.info(f"매도1호가 {b.askp1}({b.askp_rsqn1}) / 매수1호가 {b.bidp1}({b.bidp_rsqn1})")
    logger.info(f"총 매도잔량 {b.total_askp_rsqn} / 총 매수잔량 {b.total_bidp_rsqn}")


def test_inquire_daily_candles():
    """일봉 조회 (FHKST03010100)"""
    kis = make_client()

    response = kis.시세().일봉(
        kis_inquire_daily_itemchartprice.InquireDailyItemChartPriceInBlock(
            fid_input_iscd="005930",
            fid_input_date_1="20260601",
            fid_input_date_2="20260711",
        )
    ).req()

    if response.error_msg:
        logger.error(f"요청 실패: {response.error_msg} ({response.msg_cd})")
        return

    logger.info(f"수신 캔들 수: {len(response.blocks or [])}")
    for candle in (response.blocks or [])[:5]:
        logger.info(
            f"{candle.stck_bsop_date}: 시 {candle.stck_oprc} 고 {candle.stck_hgpr} "
            f"저 {candle.stck_lwpr} 종 {candle.stck_clpr} 량 {candle.acml_vol}"
        )


if __name__ == "__main__":
    test_inquire_price()
    test_inquire_asking_price()
    test_inquire_daily_candles()
