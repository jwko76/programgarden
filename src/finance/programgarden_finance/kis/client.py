"""한국투자증권(KIS Developers) OpenAPI 클라이언트 진입점입니다."""

from typing import Dict, Optional

from programgarden_core.exceptions import AppKeyException, LoginException
from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from .accno import Accno
from .order import Order
from .quotations import Quotations
from .token_manager import KisTokenManager


class Kis(metaclass=EnforceKoreanAliasMeta):
    """한국투자증권(KIS Developers) OpenAPI 클라이언트입니다.

    LS증권과 유사한 OAuth 접근토큰 방식이지만, 토큰이 24시간 유효하고
    재발급이 분당 1회로 제한되므로 파일 캐시로 토큰을 재사용합니다.

    ``paper_trading=True`` 로 생성하면 모의투자 서버로 접속하며,
    주문·계좌 TR ID(TTTC↔VTTC)도 자동 전환됩니다.

    Example:
        kis = Kis(paper_trading=True)
        kis.login(appkey="...", appsecretkey="...", account_no="12345678")
        resp = kis.quotations().inquire_price(InquirePriceInBlock(fid_input_iscd="005930")).req()
    """

    # 인스턴스 id → KisReal 싱글톤 캐시
    _real_instances: Dict[int, "KisReal"] = {}  # type: ignore[name-defined]

    def __init__(self, paper_trading: bool = False, use_token_file_cache: bool = True):
        self.paper_trading = paper_trading
        self.token_manager = KisTokenManager(
            paper_trading=paper_trading,
            use_file_cache=use_token_file_cache,
        )
        self.account_no: Optional[str] = None
        self.account_product_code: str = "01"

    def is_logged_in(self) -> bool:
        """appkey/appsecret이 등록되어 있는지 확인합니다."""
        return bool(self.token_manager.appkey and self.token_manager.appsecret)

    @require_korean_alias
    def login(
        self,
        appkey: str = None,
        appsecretkey: str = None,
        account_no: str = None,
        account_product_code: str = "01",
        issue_token: bool = False,
    ) -> bool:
        """KIS API appkey/appsecret과 계좌번호를 등록합니다.

        토큰은 기본적으로 첫 TR 요청 시 지연 발급됩니다 (재발급 분당 1회 제한 회피).
        ``issue_token=True`` 면 즉시 발급을 시도합니다.

        Parameters:
            appkey: KIS Developers 앱 키.
            appsecretkey: KIS Developers 앱 시크릿.
            account_no: 종합계좌번호 앞 8자리 (CANO).
            account_product_code: 계좌상품코드 뒤 2자리 (기본 "01").
            issue_token: True면 로그인 시점에 접근토큰을 즉시 발급합니다.
        """
        if not appkey or not appsecretkey:
            raise AppKeyException("KIS appkey/appsecret이 존재하지 않습니다.")

        self.token_manager.appkey = appkey
        self.token_manager.appsecret = appsecretkey
        # appkey가 정해졌으므로 파일 캐시 경로를 재설정하고 캐시된 토큰을 복원
        if self.token_manager.use_file_cache:
            self.token_manager.token_cache_path = (
                self.token_manager.token_cache_path.parent / self.token_manager._cache_filename()
            )
            self.token_manager._load_cache()

        self.account_no = account_no
        self.account_product_code = account_product_code or "01"

        if issue_token:
            return self.token_manager.ensure_fresh_token()
        return True

    로그인 = login
    로그인.__doc__ = "KIS API appkey/appsecret과 계좌번호를 등록합니다."

    @require_korean_alias
    async def async_login(
        self,
        appkey: str = None,
        appsecretkey: str = None,
        account_no: str = None,
        account_product_code: str = "01",
        issue_token: bool = False,
    ) -> bool:
        """KIS API appkey/appsecret과 계좌번호를 등록합니다 (비동기)."""
        return self.login(appkey, appsecretkey, account_no, account_product_code, issue_token)

    비동기로그인 = async_login
    비동기로그인.__doc__ = "KIS API appkey/appsecret과 계좌번호를 등록합니다 (비동기)."

    @require_korean_alias
    def quotations(self) -> Quotations:
        """시세 API 카테고리를 반환합니다. 로그인이 필요합니다."""
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")
        return Quotations(token_manager=self.token_manager)

    시세 = quotations
    시세.__doc__ = "시세 API 카테고리를 반환합니다. 로그인이 필요합니다."

    @require_korean_alias
    def accno(self) -> Accno:
        """계좌 API 카테고리를 반환합니다. 로그인이 필요합니다."""
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")
        return Accno(
            token_manager=self.token_manager,
            account_no=self.account_no,
            account_product_code=self.account_product_code,
        )

    계좌 = accno
    계좌.__doc__ = "계좌 API 카테고리를 반환합니다. 로그인이 필요합니다."

    @require_korean_alias
    def order(self) -> Order:
        """주문 API 카테고리를 반환합니다. 로그인이 필요합니다."""
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")
        return Order(
            token_manager=self.token_manager,
            account_no=self.account_no,
            account_product_code=self.account_product_code,
        )

    주문 = order
    주문.__doc__ = "주문 API 카테고리를 반환합니다. 로그인이 필요합니다."

    @require_korean_alias
    def real(
        self,
        reconnect: bool = True,
        max_backoff: float = 60.0,
        max_subscribe_keys: int = 40,
    ) -> "KisReal":  # type: ignore[name-defined]
        """실시간 WebSocket 클라이언트를 반환합니다 (싱글톤 — 인스턴스당 1개).

        접속에는 approval_key가 필요하며 TokenManager가 자동 발급합니다.
        ``await real.connect()`` 후 ``ccnl()`` / ``order_notice()`` 로 구독하세요.

        Parameters:
            reconnect: True면 연결 끊김 시 지수 백오프로 자동 재연결합니다.
            max_backoff: 재연결 최대 대기 시간(초).
            max_subscribe_keys: 세션당 최대 구독 건수. ``<=0`` 이면 제한 없음.
        """
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")

        from programgarden_finance.kis.real import KisReal

        key = id(self)
        cached = Kis._real_instances.get(key)
        if cached is not None:
            return cached
        instance = KisReal(
            token_manager=self.token_manager,
            reconnect=reconnect,
            max_backoff=max_backoff,
            max_subscribe_keys=max_subscribe_keys,
        )
        Kis._real_instances[key] = instance
        return instance

    실시간 = real
    실시간.__doc__ = "실시간 WebSocket 클라이언트를 반환합니다."

    @classmethod
    def _clear_real_instance(cls, kis_id: int) -> None:
        cls._real_instances.pop(kis_id, None)

    @classmethod
    def _clear_all_real_instances(cls) -> None:
        cls._real_instances.clear()


__all__ = [
    Kis,
]
