"""키움 예제 공용 .env 로딩 헬퍼.

.env 변수 (키 값은 로그·코드에 절대 노출하지 않는다):
    실전: KIWOOM_APPKEY / KIWOOM_APPSECRET / KIWOOM_ACCOUNT_NO
    모의: KIWOOM_MOCK_APPKEY / KIWOOM_MOCK_APPSECRET / KIWOOM_MOCK_ACCOUNT_NO
    KIWOOM_PAPER=1 이면 모의투자 서버(mockapi.kiwoom.com) + MOCK_* 키 사용 (기본값 1)
"""

import os

from dotenv import load_dotenv

from programgarden_finance import Kiwoom

load_dotenv()


def is_paper() -> bool:
    return os.getenv("KIWOOM_PAPER", "1") == "1"


def make_client() -> Kiwoom:
    paper = is_paper()
    prefix = "KIWOOM_MOCK_" if paper else "KIWOOM_"
    kiwoom = Kiwoom(paper_trading=paper)
    kiwoom.login(
        appkey=os.getenv(prefix + "APPKEY") or os.getenv("KIWOOM_APPKEY"),
        appsecretkey=os.getenv(prefix + "APPSECRET") or os.getenv("KIWOOM_APPSECRET"),
        account_no=os.getenv(prefix + "ACCOUNT_NO") or os.getenv("KIWOOM_ACCOUNT_NO"),
    )
    return kiwoom
