"""빗썸 입출금 관리(비공개) API - DepositWithdrawal 카테고리입니다."""

from typing import Optional

from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from ..models import BithumbCredentials, SetupOptions
from ..tr_helpers import set_tr_options
from . import (
    deposit_address_generate,
    deposit_address,
    deposit_addresses,
    deposit_krw,
    deposits_krw,
    deposit_detail,
    withdraw_coin,
    withdraw_coin_cancel,
    withdraw_krw,
    withdraws_krw,
    withdraw_detail,
    withdraws_chance,
    withdraw_coin_addresses,
)
from .deposit_address_generate import (
    DepositAddressGenerateInBlock,
    DepositAddressGenerateRequest,
    TrDepositAddressGenerate,
)
from .deposit_address import DepositAddressInBlock, DepositAddressRequest, TrDepositAddress
from .deposit_addresses import DepositAddressesInBlock, DepositAddressesRequest, TrDepositAddresses
from .deposit_krw import DepositKrwInBlock, DepositKrwRequest, TrDepositKrw
from .deposits_krw import DepositsKrwInBlock, DepositsKrwRequest, TrDepositsKrw
from .deposit_detail import DepositDetailInBlock, DepositDetailRequest, TrDepositDetail
from .withdraw_coin import WithdrawCoinInBlock, WithdrawCoinRequest, TrWithdrawCoin
from .withdraw_coin_cancel import WithdrawCoinCancelInBlock, WithdrawCoinCancelRequest, TrWithdrawCoinCancel
from .withdraw_krw import WithdrawKrwInBlock, WithdrawKrwRequest, TrWithdrawKrw
from .withdraws_krw import WithdrawsKrwInBlock, WithdrawsKrwRequest, TrWithdrawsKrw
from .withdraw_detail import WithdrawDetailInBlock, WithdrawDetailRequest, TrWithdrawDetail
from .withdraws_chance import WithdrawsChanceInBlock, WithdrawsChanceRequest, TrWithdrawsChance
from .withdraw_coin_addresses import (
    WithdrawCoinAddressesInBlock,
    WithdrawCoinAddressesRequest,
    TrWithdrawCoinAddresses,
)


class DepositWithdrawal(metaclass=EnforceKoreanAliasMeta):
    """빗썸 입출금 관리(비공개) API 카테고리입니다. 인증(access_key/secret_key)이 필요합니다."""

    def __init__(self, credentials: Optional[BithumbCredentials] = None):
        self.credentials = credentials or BithumbCredentials()

    @require_korean_alias
    def deposit_address_generate(
        self,
        body: DepositAddressGenerateInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrDepositAddressGenerate:
        request_data = DepositAddressGenerateRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrDepositAddressGenerate(request_data)

    입금주소생성요청 = deposit_address_generate
    입금주소생성요청.__doc__ = "화폐/네트워크별 입금 주소 생성을 요청합니다."

    @require_korean_alias
    def deposit_address(
        self,
        params: DepositAddressInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrDepositAddress:
        request_data = DepositAddressRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrDepositAddress(request_data)

    개별입금주소조회 = deposit_address
    개별입금주소조회.__doc__ = "화폐/네트워크별 입금 주소를 조회합니다."

    @require_korean_alias
    def deposit_addresses(
        self,
        params: Optional[DepositAddressesInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrDepositAddresses:
        request_data = DepositAddressesRequest(params=params or DepositAddressesInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrDepositAddresses(request_data)

    전체입금주소조회 = deposit_addresses
    전체입금주소조회.__doc__ = "보유한 모든 입금 주소를 조회합니다."

    @require_korean_alias
    def deposit_krw(
        self,
        body: DepositKrwInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrDepositKrw:
        request_data = DepositKrwRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrDepositKrw(request_data)

    원화입금 = deposit_krw
    원화입금.__doc__ = "원화 입금을 요청합니다. (2차 인증(카카오) 필요, 고위험)"

    @require_korean_alias
    def deposits_krw(
        self,
        params: Optional[DepositsKrwInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrDepositsKrw:
        request_data = DepositsKrwRequest(params=params or DepositsKrwInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrDepositsKrw(request_data)

    원화입금리스트조회 = deposits_krw
    원화입금리스트조회.__doc__ = "원화 입금 내역 목록을 조회합니다."

    @require_korean_alias
    def deposit_detail(
        self,
        params: DepositDetailInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrDepositDetail:
        request_data = DepositDetailRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrDepositDetail(request_data)

    개별입금조회 = deposit_detail
    개별입금조회.__doc__ = "uuid 또는 txid로 개별 입금 내역을 조회합니다."

    @require_korean_alias
    def withdraw_coin(
        self,
        body: WithdrawCoinInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawCoin:
        request_data = WithdrawCoinRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawCoin(request_data)

    가상자산출금요청 = withdraw_coin
    가상자산출금요청.__doc__ = "등록된 주소로 가상자산 출금을 요청합니다. (고위험: 실제 자산이 이동합니다)"

    @require_korean_alias
    def withdraw_coin_cancel(
        self,
        params: WithdrawCoinCancelInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawCoinCancel:
        request_data = WithdrawCoinCancelRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawCoinCancel(request_data)

    가상자산출금취소 = withdraw_coin_cancel
    가상자산출금취소.__doc__ = "진행 중인 가상자산 출금 요청을 취소합니다."

    @require_korean_alias
    def withdraw_krw(
        self,
        body: WithdrawKrwInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawKrw:
        request_data = WithdrawKrwRequest(body=body)
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawKrw(request_data)

    원화출금요청 = withdraw_krw
    원화출금요청.__doc__ = "원화 출금을 요청합니다. (2차 인증(카카오) 필요, 고위험)"

    @require_korean_alias
    def withdraws_krw(
        self,
        params: Optional[WithdrawsKrwInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawsKrw:
        request_data = WithdrawsKrwRequest(params=params or WithdrawsKrwInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawsKrw(request_data)

    원화출금리스트조회 = withdraws_krw
    원화출금리스트조회.__doc__ = "원화 출금 내역 목록을 조회합니다."

    @require_korean_alias
    def withdraw_detail(
        self,
        params: WithdrawDetailInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawDetail:
        request_data = WithdrawDetailRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawDetail(request_data)

    개별출금조회 = withdraw_detail
    개별출금조회.__doc__ = "uuid 또는 txid로 개별 출금 내역을 조회합니다."

    @require_korean_alias
    def withdraws_chance(
        self,
        params: WithdrawsChanceInBlock,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawsChance:
        request_data = WithdrawsChanceRequest(params=params)
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawsChance(request_data)

    출금가능정보 = withdraws_chance
    출금가능정보.__doc__ = "화폐/네트워크별 출금 가능 정보(수수료, 한도, 보유 자산)를 조회합니다."

    @require_korean_alias
    def withdraw_coin_addresses(
        self,
        params: Optional[WithdrawCoinAddressesInBlock] = None,
        options: Optional[SetupOptions] = None,
    ) -> TrWithdrawCoinAddresses:
        request_data = WithdrawCoinAddressesRequest(params=params or WithdrawCoinAddressesInBlock())
        set_tr_options(self.credentials, options, request_data)
        return TrWithdrawCoinAddresses(request_data)

    출금허용주소리스트조회 = withdraw_coin_addresses
    출금허용주소리스트조회.__doc__ = "사전에 등록된 출금 허용 주소 목록을 조회합니다."


__all__ = [
    DepositWithdrawal,
    deposit_address_generate,
    deposit_address,
    deposit_addresses,
    deposit_krw,
    deposits_krw,
    deposit_detail,
    withdraw_coin,
    withdraw_coin_cancel,
    withdraw_krw,
    withdraws_krw,
    withdraw_detail,
    withdraws_chance,
    withdraw_coin_addresses,
]
