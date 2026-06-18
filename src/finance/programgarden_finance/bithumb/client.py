"""빗썸(Bithumb) OpenAPI 클라이언트 진입점입니다."""

from typing import Dict

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

    실시간 WebSocket은 인증 없이 사용 가능합니다:
    ``bithumb.real()`` → ``await real.connect()`` → 구독.
    """

    # 인스턴스 id → BithumbReal 싱글톤 캐시
    _real_instances: Dict[int, "BithumbReal"] = {}  # type: ignore[name-defined]

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

    @require_korean_alias
    def real(
        self,
        reconnect: bool = True,
        max_backoff: float = 60.0,
        max_subscribe_codes: int = 15,
    ) -> "BithumbReal":  # type: ignore[name-defined]
        """실시간 WebSocket 클라이언트를 반환합니다 (싱글톤 — 인스턴스당 1개).

        인증 없이 사용할 수 있는 빗썸 공개 WebSocket(``wss://pubwss.bithumb.com/pub/ws``)에
        연결합니다. ``await real.connect()`` 후 ``ticker()`` / ``trade()`` / ``orderbook()``
        으로 스트림을 구독하세요.

        Parameters:
            reconnect: True면 연결 끊김 시 지수 백오프로 자동 재연결합니다.
            max_backoff: 재연결 최대 대기 시간(초).
            max_subscribe_codes: 스트림 타입당 최대 구독 코드 수.
                ``<=0`` 이면 제한 없음. 기본 15.
        """
        from programgarden_finance.bithumb.real import BithumbReal

        key = id(self)
        cached = Bithumb._real_instances.get(key)
        if cached is not None:
            return cached
        instance = BithumbReal(
            reconnect=reconnect,
            max_backoff=max_backoff,
            max_subscribe_codes=max_subscribe_codes,
        )
        Bithumb._real_instances[key] = instance
        return instance

    실시간 = real
    실시간.__doc__ = "실시간 WebSocket 클라이언트를 반환합니다."

    @classmethod
    def _clear_real_instance(cls, bithumb_id: int) -> None:
        cls._real_instances.pop(bithumb_id, None)

    @classmethod
    def _clear_all_real_instances(cls) -> None:
        cls._real_instances.clear()


__all__ = [
    Bithumb,
]
