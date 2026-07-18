"""키움증권 실시간 체결(0B) 구독 예제.

환경변수 (.env):
    KIWOOM_APPKEY, KIWOOM_APPSECRET
    KIWOOM_PAPER=1 이면 모의투자 서버 사용

주의: 키움 실시간 WebSocket 주소·메시지 구조는 실계좌 검증 전
      추정 구현입니다 (kiwoom/config.py TODO 참조).
"""

import asyncio
import logging
import os

from dotenv import load_dotenv

from programgarden_finance import Kiwoom

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

load_dotenv()


async def main():
    kiwoom = Kiwoom(paper_trading=os.getenv("KIWOOM_PAPER", "1") == "1")
    kiwoom.login(
        appkey=os.getenv("KIWOOM_APPKEY"),
        appsecretkey=os.getenv("KIWOOM_APPSECRET"),
    )

    real = kiwoom.실시간()
    await real.connect()

    ccnl = real.체결가()
    ccnl.체결가수신(
        lambda r: logger.info(f"{r.item} 체결 {r.cur_prc}원 ({r.pred_pre} / {r.flu_rt}%) 량 {r.cntr_qty}")
    )
    ccnl.체결가등록(["005930", "000660"])

    logger.info("60초간 체결 수신 대기...")
    await asyncio.sleep(60)
    await real.close()


if __name__ == "__main__":
    asyncio.run(main())
