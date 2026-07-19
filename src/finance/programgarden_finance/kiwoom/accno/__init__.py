"""키움증권 계좌 API - Accno 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import SetupOptions
from ..token_manager import KiwoomTokenManager
from ..tr_helpers import set_tr_options
from . import inquire_balance, inquire_psbl_order
from .inquire_balance import InquireBalanceInBlock, InquireBalanceRequest, TrInquireBalance
from .inquire_psbl_order import InquirePsblOrderInBlock, InquirePsblOrderRequest, TrInquirePsblOrder


class Accno(metaclass=EnforceKoreanAliasMeta):
    """키움증권 계좌 API 카테고리입니다.

    계좌번호(account_no)를 생략하면 클라이언트 로그인 시 등록한 계좌
    정보로 자동 채워집니다. 키움 REST 계좌 필드는 KIS의 cano+acnt_prdt_cd
    2단 구조와 달리 단일 계좌번호(acnt_no)로 판단해 account_product_code는
    TR 바디에 사용하지 않습니다 (구조적 정합성을 위해 보관만 합니다).
    TODO(실계좌 검증): 실제 계좌 필드 구조 확인.
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

    def _fill_account(self, block) -> None:
        """block의 계좌 필드가 비어 있으면 클라이언트 등록 값으로 채웁니다."""
        if not getattr(block, "acnt_no", None) and self.account_no:
            block.acnt_no = self.account_no

    @require_korean_alias
    def inquire_balance(
        self,
        params: Optional[InquireBalanceInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrInquireBalance:
        if params is None:
            params = InquireBalanceInBlock(acnt_no=self.account_no or "")
        self._fill_account(params)
        request_data = InquireBalanceRequest(body=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquireBalance(request_data)

    잔고 = inquire_balance
    잔고.__doc__ = "계좌평가잔고내역(보유 종목·예수금·평가금액)을 조회합니다. (kt00018)"

    @require_korean_alias
    def inquire_psbl_order(
        self,
        params: InquirePsblOrderInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrInquirePsblOrder:
        self._fill_account(params)
        request_data = InquirePsblOrderRequest(body=params)
        set_tr_options(self.token_manager, options, request_data)
        return TrInquirePsblOrder(request_data)

    주문가능 = inquire_psbl_order
    주문가능.__doc__ = "종목별 주문인출가능금액을 조회합니다. (kt00010)"


__all__ = [
    Accno,
    inquire_balance,
    inquire_psbl_order,
]
