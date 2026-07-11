"""KIS 국내주식 주문 API - Order 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import SetupOptions
from ..token_manager import KisTokenManager
from ..tr_helpers import set_tr_options
from . import order_cash, order_rvsecncl
from .order_cash import OrderCashBodyBlock, OrderCashRequest, TrOrderCash
from .order_rvsecncl import OrderRvsecnclBodyBlock, OrderRvsecnclRequest, TrOrderRvsecncl


class Order(metaclass=EnforceKoreanAliasMeta):
    """KIS 국내주식 주문 API 카테고리입니다.

    계좌번호(cano/acnt_prdt_cd)를 생략하면 클라이언트 로그인 시 등록한
    계좌 정보로 자동 채워집니다. 모의투자 tr_id 전환은 자동입니다.
    """

    def __init__(
        self,
        token_manager: KisTokenManager,
        account_no: Optional[str] = None,
        account_product_code: str = "01",
    ):
        self.token_manager = token_manager
        self.account_no = account_no
        self.account_product_code = account_product_code

    def _fill_account(self, body) -> None:
        """body의 계좌 필드가 비어 있으면 클라이언트 등록 값으로 채웁니다."""
        if not getattr(body, "cano", None) and self.account_no:
            body.cano = self.account_no
        if getattr(body, "acnt_prdt_cd", None) in (None, "") and self.account_product_code:
            body.acnt_prdt_cd = self.account_product_code

    @require_korean_alias
    def order_cash_buy(
        self, body: OrderCashBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderCash:
        self._fill_account(body)
        request_data = OrderCashRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderCash(request_data, side="buy")

    현금매수 = order_cash_buy
    현금매수.__doc__ = "주식 현금 매수 주문을 실행합니다. (TTTC0802U/VTTC0802U)"

    @require_korean_alias
    def order_cash_sell(
        self, body: OrderCashBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderCash:
        self._fill_account(body)
        request_data = OrderCashRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderCash(request_data, side="sell")

    현금매도 = order_cash_sell
    현금매도.__doc__ = "주식 현금 매도 주문을 실행합니다. (TTTC0801U/VTTC0801U)"

    @require_korean_alias
    def order_rvsecncl(
        self, body: OrderRvsecnclBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderRvsecncl:
        self._fill_account(body)
        request_data = OrderRvsecnclRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderRvsecncl(request_data)

    정정취소 = order_rvsecncl
    정정취소.__doc__ = "주식 주문을 정정/취소합니다. (TTTC0803U/VTTC0803U)"


__all__ = [
    Order,
    order_cash,
    order_rvsecncl,
]
