"""키움증권 주문 API - Order 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import SetupOptions
from ..token_manager import KiwoomTokenManager
from ..tr_helpers import set_tr_options
from . import order_cash, order_rvsecncl
from .order_cash import OrderCashBodyBlock, OrderCashRequest, TrOrderCash
from .order_rvsecncl import OrderRvsecnclBodyBlock, OrderRvsecnclRequest, TrOrderRvsecncl


class Order(metaclass=EnforceKoreanAliasMeta):
    """키움증권 주문 API 카테고리입니다.

    계좌번호(account_no)를 생략하면 클라이언트 로그인 시 등록한 계좌
    정보로 자동 채워집니다. KIS는 정정/취소를 하나의 TR + 구분 필드로
    처리하지만, 키움은 api-id 자체가 다르므로(kt10002 정정 / kt10003
    취소) ``order_modify``/``order_cancel`` 두 메서드로 분리했습니다.
    """

    def __init__(
        self,
        token_manager: KiwoomTokenManager,
        account_no: Optional[str] = None,
        account_product_code: str = "01",
    ):
        self.token_manager = token_manager
        self.account_no = account_no
        # 키움 TR 바디에는 현재 미사용 — KIS와의 구조적 정합성을 위해 보관.
        self.account_product_code = account_product_code

    def _fill_account(self, body) -> None:
        """body의 계좌 필드가 비어 있으면 클라이언트 등록 값으로 채웁니다."""
        if not getattr(body, "acnt_no", None) and self.account_no:
            body.acnt_no = self.account_no

    @require_korean_alias
    def order_cash_buy(
        self, body: OrderCashBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderCash:
        self._fill_account(body)
        request_data = OrderCashRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderCash(request_data, side="buy")

    현금매수 = order_cash_buy
    현금매수.__doc__ = "주식 현금 매수 주문을 실행합니다. (kt10000)"

    @require_korean_alias
    def order_cash_sell(
        self, body: OrderCashBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderCash:
        self._fill_account(body)
        request_data = OrderCashRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderCash(request_data, side="sell")

    현금매도 = order_cash_sell
    현금매도.__doc__ = "주식 현금 매도 주문을 실행합니다. (kt10001)"

    @require_korean_alias
    def order_modify(
        self, body: OrderRvsecnclBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderRvsecncl:
        self._fill_account(body)
        request_data = OrderRvsecnclRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderRvsecncl(request_data, mode="modify")

    정정 = order_modify
    정정.__doc__ = "주식 주문을 정정합니다. (kt10002)"

    @require_korean_alias
    def order_cancel(
        self, body: OrderRvsecnclBodyBlock, options: Optional[SetupOptions] = None
    ) -> TrOrderRvsecncl:
        self._fill_account(body)
        request_data = OrderRvsecnclRequest(body=body)
        set_tr_options(self.token_manager, options, request_data)
        return TrOrderRvsecncl(request_data, mode="cancel")

    취소 = order_cancel
    취소.__doc__ = "주식 주문을 취소합니다. (kt10003)"


__all__ = [
    Order,
    order_cash,
    order_rvsecncl,
]
