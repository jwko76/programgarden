"""빗썸(Bithumb) OpenAPI 클라이언트 진입점입니다."""

from programgarden_core.exceptions import AppKeyException, LoginException
from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from .account import Account
from .deposit_withdrawal import DepositWithdrawal
from .market import Market
from .models import BithumbCredentials
from .order import Order


class Bithumb(metaclass=EnforceKoreanAliasMeta):
    """빗썸(Bithumb) OpenAPI v2.1.5 클라이언트입니다.

    LS증권과 달리 OAuth 토큰 발급 절차가 없으며, ``login()``으로 등록한
    access_key/secret_key는 요청마다 JWT를 생성하는 데 사용됩니다.
    """

    def __init__(self):
        self.credentials = BithumbCredentials()

    def is_logged_in(self) -> bool:
        """access_key/secret_key가 등록되어 있는지 확인합니다."""
        return self.credentials.is_available()

    @require_korean_alias
    def login(self, accesskey: str = None, secretkey: str = None) -> bool:
        """빗썸 API Access Key/Secret Key를 등록합니다."""
        if not accesskey or not secretkey:
            raise AppKeyException("Bithumb access_key/secret_key가 존재하지 않습니다.")

        self.credentials.access_key = accesskey
        self.credentials.secret_key = secretkey
        return True

    로그인 = login
    로그인.__doc__ = "빗썸 API Access Key/Secret Key를 등록합니다."

    @require_korean_alias
    async def async_login(self, accesskey: str = None, secretkey: str = None) -> bool:
        """빗썸 API Access Key/Secret Key를 등록합니다 (비동기)."""
        return self.login(accesskey, secretkey)

    비동기로그인 = async_login
    비동기로그인.__doc__ = "빗썸 API Access Key/Secret Key를 등록합니다 (비동기)."

    @require_korean_alias
    def market(self) -> Market:
        """시세(공개) API 카테고리를 반환합니다. 인증이 필요하지 않습니다."""
        return Market(credentials=self.credentials)

    시세 = market
    시세.__doc__ = "시세(공개) API 카테고리를 반환합니다. 인증이 필요하지 않습니다."

    @require_korean_alias
    def account(self) -> Account:
        """계좌(비공개) API 카테고리를 반환합니다. 로그인이 필요합니다."""
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")
        return Account(credentials=self.credentials)

    계좌 = account
    계좌.__doc__ = "계좌(비공개) API 카테고리를 반환합니다. 로그인이 필요합니다."

    @require_korean_alias
    def order(self) -> Order:
        """주문(비공개) API 카테고리를 반환합니다. 로그인이 필요합니다."""
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")
        return Order(credentials=self.credentials)

    주문 = order
    주문.__doc__ = "주문(비공개) API 카테고리를 반환합니다. 로그인이 필요합니다."

    @require_korean_alias
    def deposit_withdrawal(self) -> DepositWithdrawal:
        """입출금 관리(비공개) API 카테고리를 반환합니다. 로그인이 필요합니다."""
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")
        return DepositWithdrawal(credentials=self.credentials)

    입출금 = deposit_withdrawal
    입출금.__doc__ = "입출금 관리(비공개) API 카테고리를 반환합니다. 로그인이 필요합니다."


__all__ = [
    Bithumb,
]
