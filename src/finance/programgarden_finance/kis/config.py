"""한국투자증권(KIS Developers) OpenAPI URL 및 TR ID 상수입니다.

실전투자와 모의투자는 도메인(포트)과 일부 TR ID가 다릅니다.
- 실전: https://openapi.koreainvestment.com:9443 / ws://ops.koreainvestment.com:21000
- 모의: https://openapivts.koreainvestment.com:29443 / ws://ops.koreainvestment.com:31000
- 주문·계좌 TR ID는 실전 TTTC…, 모의 VTTC… 로 나뉩니다 (시세 TR은 공통).
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class URLS:
    """KIS OpenAPI 기본 URL 및 엔드포인트 상수입니다."""

    REAL_URL: str = "https://openapi.koreainvestment.com:9443"
    PAPER_URL: str = "https://openapivts.koreainvestment.com:29443"

    # 실시간 WebSocket
    WS_REAL_URL: str = "ws://ops.koreainvestment.com:21000"
    WS_PAPER_URL: str = "ws://ops.koreainvestment.com:31000"

    # OAuth
    TOKEN_PATH: str = "/oauth2/tokenP"
    APPROVAL_PATH: str = "/oauth2/Approval"

    # 국내주식 시세
    INQUIRE_PRICE_PATH: str = "/uapi/domestic-stock/v1/quotations/inquire-price"
    INQUIRE_ASKING_PRICE_PATH: str = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
    INQUIRE_DAILY_ITEMCHARTPRICE_PATH: str = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"

    # 국내주식 계좌
    INQUIRE_BALANCE_PATH: str = "/uapi/domestic-stock/v1/trading/inquire-balance"
    INQUIRE_PSBL_ORDER_PATH: str = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"

    # 국내주식 주문
    ORDER_CASH_PATH: str = "/uapi/domestic-stock/v1/trading/order-cash"
    ORDER_RVSECNCL_PATH: str = "/uapi/domestic-stock/v1/trading/order-rvsecncl"

    @classmethod
    def get_base_url(cls, paper_trading: bool) -> str:
        """실전/모의 REST 기본 URL을 반환합니다."""
        return cls.PAPER_URL if paper_trading else cls.REAL_URL

    @classmethod
    def get_ws_url(cls, paper_trading: bool) -> str:
        """실전/모의 WebSocket URL을 반환합니다."""
        return cls.WS_PAPER_URL if paper_trading else cls.WS_REAL_URL


class TR_IDS:
    """TR ID 상수. (실전, 모의) 튜플은 GenericKisTR이 paper_trading으로 해석합니다.

    KIS Developers 공식 샘플(open-trading-api) 기준 ID입니다.
    문서 개정으로 ID가 변경될 경우 이 클래스만 수정하면 됩니다.
    """

    # 시세 (실전/모의 공통)
    INQUIRE_PRICE: str = "FHKST01010100"                 # 주식현재가 시세
    INQUIRE_ASKING_PRICE: str = "FHKST01010200"          # 주식현재가 호가/예상체결
    INQUIRE_DAILY_ITEMCHARTPRICE: str = "FHKST03010100"  # 국내주식 기간별 시세(일/주/월/년)

    # 계좌
    INQUIRE_BALANCE: Tuple[str, str] = ("TTTC8434R", "VTTC8434R")     # 주식잔고조회
    INQUIRE_PSBL_ORDER: Tuple[str, str] = ("TTTC8908R", "VTTC8908R")  # 매수가능조회

    # 주문 (현금)
    ORDER_CASH_BUY: Tuple[str, str] = ("TTTC0802U", "VTTC0802U")   # 주식주문(현금) 매수
    ORDER_CASH_SELL: Tuple[str, str] = ("TTTC0801U", "VTTC0801U")  # 주식주문(현금) 매도
    ORDER_RVSECNCL: Tuple[str, str] = ("TTTC0803U", "VTTC0803U")   # 주식주문(정정취소)

    # 실시간 WebSocket
    REAL_CCNL: str = "H0STCNT0"          # 국내주식 실시간 체결가
    REAL_ASKING_PRICE: str = "H0STASP0"  # 국내주식 실시간 호가 (MVP 미사용)
    REAL_ORDER_NOTICE: Tuple[str, str] = ("H0STCNI0", "H0STCNI9")  # 실시간 체결통보 (실전/모의)
