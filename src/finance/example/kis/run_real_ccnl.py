"""KIS 실시간 체결가 (H0STCNT0) WebSocket 예제.

환경변수 (.env):
    KIS_APPKEY, KIS_APPSECRET
    KIS_PAPER=1 이면 모의투자 서버(포트 31000) 사용
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

from programgarden_finance import Kis

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


async def main():
    kis = Kis(paper_trading=os.getenv("KIS_PAPER", "1") == "1")
    kis.login(
        appkey=os.getenv("KIS_APPKEY"),
        appsecretkey=os.getenv("KIS_APPSECRET"),
    )

    real = kis.실시간()
    await real.connect()
    logger.info("KIS WebSocket 연결 완료")

    ccnl = real.체결가()

    def on_tick(resp):
        logger.info(
            f"[{resp.stck_cntg_hour}] {resp.mksc_shrn_iscd} "
            f"체결가 {resp.stck_prpr} ({resp.prdy_vrss} / {resp.prdy_ctrt}%) "
            f"체결량 {resp.cntg_vol}"
        )

    ccnl.체결가수신(on_tick)
    ccnl.체결가등록(["005930", "000660"])
    logger.info("실시간 체결가 구독: 005930, 000660 (60초 수신)")

    await asyncio.sleep(60)

    ccnl.체결가해제(["005930", "000660"])
    await real.close()
    logger.info("연결 종료")


if __name__ == "__main__":
    asyncio.run(main())
