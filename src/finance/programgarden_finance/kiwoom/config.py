"""키움증권(Kiwoom Securities) OpenAPI URL 및 TR ID(api-id) 상수입니다.

KIS와 달리 실전투자/모의투자는 tr_id 분기가 아니라 **도메인 자체**가 다릅니다.
- 실전: https://api.kiwoom.com
- 모의: https://mockapi.kiwoom.com
- 주문·계좌·시세 TR ID(``api-id``)는 실전/모의 공통이며 단일 문자열입니다.

실시간 WebSocket도 실전/모의 호스트가 분리되어 있으며 경로는
``/api/dostk/websocket`` 입니다 (2026-07-18 모의서버 라이브 접속으로 확인).
"""

from dataclasses import dataclass


@dataclass
class URLS:
    """키움 OpenAPI 기본 URL 및 엔드포인트 상수입니다."""

    PROD_URL: str = "https://api.kiwoom.com"
    MOCK_URL: str = "https://mockapi.kiwoom.com"

    # 실시간 WebSocket — 실전/모의 호스트 분리, 경로 /api/dostk/websocket
    WS_URL: str = "wss://api.kiwoom.com:10000/api/dostk/websocket"
    MOCK_WS_URL: str = "wss://mockapi.kiwoom.com:10000/api/dostk/websocket"

    # OAuth
    TOKEN_PATH: str = "/oauth2/token"

    # 국내주식 시세
    STKINFO_PATH: str = "/api/dostk/stkinfo"  # 종목기본정보요청(현재가 포함) ka10001
    MRKCOND_PATH: str = "/api/dostk/mrkcond"  # 주식호가요청 ka10004
    CHART_PATH: str = "/api/dostk/chart"      # 주식일봉차트조회요청 ka10081

    # 국내주식 계좌
    ACNT_PATH: str = "/api/dostk/acnt"  # 계좌평가잔고내역요청 kt00018 / 주문인출가능금액요청 kt00010

    # 국내주식 주문
    ORDR_PATH: str = "/api/dostk/ordr"  # 현금매수/매도/정정/취소 kt10000~kt10003

    @classmethod
    def get_base_url(cls, paper_trading: bool) -> str:
        """실전/모의 REST 기본 URL을 반환합니다."""
        return cls.MOCK_URL if paper_trading else cls.PROD_URL

    @classmethod
    def get_ws_url(cls, paper_trading: bool) -> str:
        """실전/모의 실시간 WebSocket URL을 반환합니다."""
        return cls.MOCK_WS_URL if paper_trading else cls.WS_URL


class TR_IDS:
    """TR ID(``api-id`` 헤더 값) 상수입니다.

    KIS의 ``(실전, 모의)`` 튜플과 달리 키움은 도메인이 실전/모의를
    구분하므로 모든 값이 단일 문자열입니다.
    """

    # 시세
    INQUIRE_PRICE: str = "ka10001"                 # 종목기본정보요청 (현재가 포함)
    INQUIRE_ASKING_PRICE: str = "ka10004"           # 주식호가요청
    INQUIRE_DAILY_ITEMCHARTPRICE: str = "ka10081"   # 주식일봉차트조회요청

    # 계좌
    INQUIRE_BALANCE: str = "kt00018"     # 계좌평가잔고내역요청
    INQUIRE_PSBL_ORDER: str = "kt00010"  # 주문인출가능금액요청

    # 주문 (현금)
    ORDER_CASH_BUY: str = "kt10000"   # 매수
    ORDER_CASH_SELL: str = "kt10001"  # 매도
    ORDER_MODIFY: str = "kt10002"     # 정정
    ORDER_CANCEL: str = "kt10003"     # 취소

    # 실시간 WebSocket 타입 코드 (``type`` 필드 값)
    REAL_CCNL: str = "0B"          # 주식체결
    REAL_ORDER_NOTICE: str = "00"  # 주문체결통보
