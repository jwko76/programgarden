"""키움증권(Kiwoom Securities) OpenAPI 래퍼 패키지입니다.

Example:
    from programgarden_finance.kiwoom import Kiwoom
    from programgarden_finance.kiwoom.quotations.inquire_price import InquirePriceInBlock

    kiwoom = Kiwoom(paper_trading=True)
    kiwoom.login(appkey="...", appsecretkey="...", account_no="12345678")
    resp = kiwoom.quotations().inquire_price(InquirePriceInBlock(stk_cd="005930")).req()
    print(resp.block.cur_prc)
"""

from .client import Kiwoom
from .config import URLS, TR_IDS
from .models import KiwoomResponseBase, SetupOptions
from .status import RequestStatus
from .token_manager import KiwoomTokenManager

__all__ = [
    Kiwoom,
    URLS,
    TR_IDS,
    KiwoomResponseBase,
    SetupOptions,
    RequestStatus,
    KiwoomTokenManager,
]
