from dataclasses import dataclass


@dataclass
class URLS:
    """빗썸(Bithumb) OpenAPI 기본 URL 및 엔드포인트 상수입니다."""

    BITHUMB_URL: str = "https://api.bithumb.com"

    # 시세 (공개 API)
    MARKET_ALL_URL: str = f"{BITHUMB_URL}/v1/market/all"
    TICKER_URL: str = f"{BITHUMB_URL}/v1/ticker"
    ORDERBOOK_URL: str = f"{BITHUMB_URL}/v1/orderbook"
    TRADES_TICKS_URL: str = f"{BITHUMB_URL}/v1/trades/ticks"
    CANDLES_DAYS_URL: str = f"{BITHUMB_URL}/v1/candles/days"
    CANDLES_WEEKS_URL: str = f"{BITHUMB_URL}/v1/candles/weeks"
    CANDLES_MONTHS_URL: str = f"{BITHUMB_URL}/v1/candles/months"

    # 계좌 (비공개 API)
    ACCOUNTS_URL: str = f"{BITHUMB_URL}/v1/accounts"
    WALLET_STATUS_URL: str = f"{BITHUMB_URL}/v1/status/wallet"
    DEPOSITS_URL: str = f"{BITHUMB_URL}/v1/deposits"
    WITHDRAWS_URL: str = f"{BITHUMB_URL}/v1/withdraws"

    # 주문 (비공개 API)
    ORDERS_CHANCE_URL: str = f"{BITHUMB_URL}/v1/orders/chance"
    ORDER_URL: str = f"{BITHUMB_URL}/v1/order"
    ORDERS_URL: str = f"{BITHUMB_URL}/v1/orders"
    ORDER_NEW_URL: str = f"{BITHUMB_URL}/v2/orders"
    ORDER_CANCEL_URL: str = f"{BITHUMB_URL}/v2/order"
    ORDER_NEW_BATCH_URL: str = f"{BITHUMB_URL}/v2/orders/batch"
    ORDER_CANCEL_BATCH_URL: str = f"{BITHUMB_URL}/v2/orders/cancel"
    TWAP_URL: str = f"{BITHUMB_URL}/v1/twap"

    # 입출금 관리 (비공개 API)
    DEPOSIT_ADDRESS_GENERATE_URL: str = f"{BITHUMB_URL}/v1/deposits/generate_coin_address"
    DEPOSIT_ADDRESS_URL: str = f"{BITHUMB_URL}/v1/deposits/coin_address"
    DEPOSIT_ADDRESSES_URL: str = f"{BITHUMB_URL}/v1/deposits/coin_addresses"
    DEPOSITS_KRW_URL: str = f"{BITHUMB_URL}/v1/deposits/krw"  # POST(원화입금)/GET(원화입금리스트조회) 공용
    DEPOSIT_DETAIL_URL: str = f"{BITHUMB_URL}/v1/deposit"
    WITHDRAWS_COIN_URL: str = f"{BITHUMB_URL}/v1/withdraws/coin"  # POST(가상자산출금요청)/DELETE(가상자산출금취소) 공용
    WITHDRAWS_KRW_URL: str = f"{BITHUMB_URL}/v1/withdraws/krw"  # POST(원화출금요청)/GET(원화출금리스트조회) 공용
    WITHDRAW_DETAIL_URL: str = f"{BITHUMB_URL}/v1/withdraw"
    WITHDRAWS_CHANCE_URL: str = f"{BITHUMB_URL}/v1/withdraws/chance"
    WITHDRAW_COIN_ADDRESSES_URL: str = f"{BITHUMB_URL}/v1/withdraws/coin_addresses"

    # 기타 (공개 API)
    FEE_INOUT_URL: str = f"{BITHUMB_URL}/v2/fee/inout"

    # 계좌 (비공개 API)
    API_KEYS_URL: str = f"{BITHUMB_URL}/v1/api_keys"

    @classmethod
    def fee_inout_url(cls, currency: str) -> str:
        """화폐별 입출금 수수료 조회 URL을 생성합니다."""
        return f"{cls.FEE_INOUT_URL}/{currency}"

    @classmethod
    def candles_minutes_url(cls, unit: int) -> str:
        """분(分) 캔들 조회 URL을 생성합니다.

        unit: 1, 3, 5, 10, 15, 30, 60, 240 중 하나입니다.
        """
        return f"{cls.BITHUMB_URL}/v1/candles/minutes/{unit}"
