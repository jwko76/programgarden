"""한국투자증권(KIS Developers) OpenAPI 래퍼 패키지입니다.

Example:
    from programgarden_finance import Kis
    from programgarden_finance.kis.quotations.inquire_price import InquirePriceInBlock

    kis = Kis(paper_trading=True)
    kis.login(appkey="...", appsecretkey="...", account_no="12345678")
    resp = kis.quotations().inquire_price(InquirePriceInBlock(fid_input_iscd="005930")).req()
    print(resp.block.stck_prpr)
"""

from .client import Kis
from .config import URLS, TR_IDS
from .models import KisResponseBase, SetupOptions
from .status import RequestStatus
from .token_manager import KisTokenManager

__all__ = [
    Kis,
    URLS,
    TR_IDS,
    KisResponseBase,
    SetupOptions,
    RequestStatus,
    KisTokenManager,
]
