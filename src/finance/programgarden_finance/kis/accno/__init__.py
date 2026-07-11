"""KIS 국내주식 계좌 API - Accno 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import SetupOptions
from ..token_manager import KisTokenManager
from ..tr_helpers import set_tr_options
from . import inquire_balance, inquire_psbl_order
from .inquire_balance import InquireBalanceInBlock, InquireBalanceRequest, TrInquireBalance
from .inquire_psbl_order import InquirePsblOrderInBlock, InquirePsblOrderRequest, TrInquirePsblOrder


class Accno(metaclass=EnforceKoreanAliasMeta):
    """KIS 국내주식 계좌 API 카테고리입니다.

    계좌번호(cano/acnt_prdt_cd)를 생략하면 클라이언트 로그인 시 등록한
    계좌 정보로 자동 채워집니다.
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

    def _fill_account(self, params) -> None:
        """params의 계좌 필드가 비어 있으면 클라이언트 등록 값으로 채웁니다."""
        if not getattr(params, "cano", None) and self.account_no:
            params.cano = self.account_no
        if getattr(params, "acnt_prdt_cd", None) in (None, "") and self.account_product_code:
            params.acnt_prdt_cd = self.account_product_code

    @require_korean_alias
    def inquire_balance(
        self,
        params: Optional[InquireBalanceInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrInquireBalance:
        if params is None:
            params = InquireBalanceInBlock(cano=self.account_no or "")
        self._fill_account(params)
        request_data = InquireBalanceRequest(params=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquireBalance(request_data)

    잔고 = inquire_balance
    잔고.__doc__ = "주식 잔고(보유 종목·예수금·평가금액)를 조회합니다. (TTTC8434R/VTTC8434R)"

    @require_korean_alias
    def inquire_psbl_order(
        self,
        params: InquirePsblOrderInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrInquirePsblOrder:
        self._fill_account(params)
        request_data = InquirePsblOrderRequest(params=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquirePsblOrder(request_data)

    주문가능 = inquire_psbl_order
    주문가능.__doc__ = "종목별 매수가능 금액/수량을 조회합니다. (TTTC8908R/VTTC8908R)"


__all__ = [
    Accno,
    inquire_balance,
    inquire_psbl_order,
]
