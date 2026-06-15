"""빗썸 계좌(비공개) API - Account 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import BithumbCredentials, SetupOptions
from ..tr_helpers import set_tr_options
from . import accounts, wallet_status, deposits, withdraws, api_keys
from .accounts import AccountsInBlock, AccountsRequest, TrAccounts
from .wallet_status import TrWalletStatus, WalletStatusInBlock, WalletStatusRequest
from .deposits import DepositsInBlock, DepositsRequest, TrDeposits
from .withdraws import TrWithdraws, WithdrawsInBlock, WithdrawsRequest
from .api_keys import ApiKeysInBlock, ApiKeysRequest, TrApiKeys


class Account(metaclass=EnforceKoreanAliasMeta):
    """빗썸 계좌(비공개) API 카테고리입니다. 인증(access_key/secret_key)이 필요합니다."""

    def __init__(self, credentials: Optional[BithumbCredentials] = None):
        self.credentials = credentials or BithumbCredentials()

    @require_korean_alias
    def accounts(
        self,
        params: Optional[AccountsInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrAccounts:
        request_data = AccountsRequest(params=params or AccountsInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrAccounts(request_data)

    전체자산조회 = accounts
    전체자산조회.__doc__ = "보유 자산(화폐별 잔고/평단가) 전체를 조회합니다."

    @require_korean_alias
    def wallet_status(
        self,
        params: Optional[WalletStatusInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrWalletStatus:
        request_data = WalletStatusRequest(params=params or WalletStatusInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrWalletStatus(request_data)

    입출금현황 = wallet_status
    입출금현황.__doc__ = "화폐/네트워크별 입출금 가능 상태를 조회합니다."

    @require_korean_alias
    def deposits(
        self,
        params: Optional[DepositsInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrDeposits:
        request_data = DepositsRequest(params=params or DepositsInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrDeposits(request_data)

    입금리스트조회 = deposits
    입금리스트조회.__doc__ = "입금 내역 목록을 조회합니다."

    @require_korean_alias
    def withdraws(
        self,
        params: Optional[WithdrawsInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdraws:
        request_data = WithdrawsRequest(params=params or WithdrawsInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrWithdraws(request_data)

    출금리스트조회 = withdraws
    출금리스트조회.__doc__ = "출금 내역 목록을 조회합니다."

    @require_korean_alias
    def api_keys(
        self,
        params: Optional[ApiKeysInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrApiKeys:
        request_data = ApiKeysRequest(params=params or ApiKeysInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrApiKeys(request_data)

    API키리스트조회 = api_keys
    API키리스트조회.__doc__ = "등록된 API 키 목록과 만료 일시를 조회합니다."


__all__ = [
    Account,
    accounts,
    wallet_status,
    deposits,
    withdraws,
    api_keys,
]
