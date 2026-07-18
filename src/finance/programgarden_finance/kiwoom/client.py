"""키움증권(Kiwoom Securities) OpenAPI 클라이언트 진입점입니다."""

from typing import Dict, Optional

from programgarden_core.exceptions import AppKeyException, LoginException
from programgarden_core.korea_alias import EnforceKoreanAliasMeta, require_korean_alias

from .accno import Accno
from .order import Order
from .quotations import Quotations
from .token_manager import KiwoomTokenManager


class Kiwoom(metaclass=EnforceKoreanAliasMeta):
    """키움증권(Kiwoom Securities) OpenAPI 클라이언트입니다.

    KIS와 유사한 OAuth 접근토큰 방식이지만 세부 규격이 다릅니다:
    - 토큰 발급 요청 필드명이 다릅니다 (``secretkey`` vs KIS ``appsecret``).
    - 토큰 발급 응답 필드명이 다릅니다 (``token`` vs KIS ``access_token``).
    - 실전/모의투자는 KIS처럼 tr_id 분기가 아니라 **도메인 자체**가
      다릅니다 (``api.kiwoom.com`` ↔ ``mockapi.kiwoom.com``).
    - 모든 TR이 POST이며, 조회/주문 구분 없이 하나의 JSON 바디로 전송됩니다.

    ``paper_trading=True`` 로 생성하면 모의투자(mock) 서버로 접속합니다.

    Example:
        kiwoom = Kiwoom(paper_trading=True)
        kiwoom.login(appkey="...", appsecretkey="...", account_no="12345678")
        resp = kiwoom.quotations().inquire_price(InquirePriceInBlock(stk_cd="005930")).req()
        print(resp.block.cur_prc)
    """

    # 인스턴스 id → KiwoomReal 싱글톤 캐시
    _real_instances: Dict[int, "KiwoomReal"] = {}  # type: ignore[name-defined]

    def __init__(self, paper_trading: bool = False, use_token_file_cache: bool = True):
        self.paper_trading = paper_trading
        self.token_manager = KiwoomTokenManager(
            paper_trading=paper_trading,
            use_file_cache=use_token_file_cache,
        )
        self.account_no: Optional[str] = None
        self.account_product_code: str = "01"

    def is_logged_in(self) -> bool:
        """appkey/secretkey가 등록되어 있는지 확인합니다."""
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
        """키움 OpenAPI appkey/secretkey와 계좌번호를 등록합니다.

        토큰은 기본적으로 첫 TR 요청 시 지연 발급됩니다.
        ``issue_token=True`` 면 즉시 발급을 시도합니다.

        Parameters:
            appkey: 키움 OpenAPI 앱 키.
            appsecretkey: 키움 OpenAPI 시크릿 키 (발급 요청 시 ``secretkey`` 필드로 전송됩니다).
            account_no: 키움 계좌번호(전체).
            account_product_code: 계좌상품코드. 키움 REST 계좌 필드가 KIS의
                cano+acnt_prdt_cd 2단 구조인지 확인되지 않아, login() 시그니처는
                구조적 정합성을 위해 유지하되 TR 바디에는 사용하지 않습니다
                (TODO(실계좌 검증)).
            issue_token: True면 로그인 시점에 접근토큰을 즉시 발급합니다.
        """
        if not appkey or not appsecretkey:
            raise AppKeyException("Kiwoom appkey/secretkey가 존재하지 않습니다.")

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
    로그인.__doc__ = "키움 OpenAPI appkey/secretkey와 계좌번호를 등록합니다."

    @require_korean_alias
    async def async_login(
        self,
        appkey: str = None,
        appsecretkey: str = None,
        account_no: str = None,
        account_product_code: str = "01",
        issue_token: bool = False,
    ) -> bool:
        """키움 OpenAPI appkey/secretkey와 계좌번호를 등록합니다 (비동기)."""
        return self.login(appkey, appsecretkey, account_no, account_product_code, issue_token)

    비동기로그인 = async_login
    비동기로그인.__doc__ = "키움 OpenAPI appkey/secretkey와 계좌번호를 등록합니다 (비동기)."

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
    ) -> "KiwoomReal":  # type: ignore[name-defined]
        """실시간 WebSocket 클라이언트를 반환합니다 (싱글톤 — 인스턴스당 1개).

        키움은 KIS의 approval_key 같은 별도 개념 없이 REST 접근토큰을
        그대로 재사용해 접속합니다. ``await real.connect()`` 후
        ``ccnl()`` / ``order_notice()`` 로 구독하세요.

        Parameters:
            reconnect: True면 연결 끊김 시 지수 백오프로 자동 재연결합니다.
            max_backoff: 재연결 최대 대기 시간(초).
            max_subscribe_keys: 세션당 최대 구독 건수. ``<=0`` 이면 제한 없음.
        """
        if not self.is_logged_in():
            raise LoginException("로그인이 필요합니다.")

        from programgarden_finance.kiwoom.real import KiwoomReal

        key = id(self)
        cached = Kiwoom._real_instances.get(key)
        if cached is not None:
            return cached
        instance = KiwoomReal(
            token_manager=self.token_manager,
            reconnect=reconnect,
            max_backoff=max_backoff,
            max_subscribe_keys=max_subscribe_keys,
        )
        Kiwoom._real_instances[key] = instance
        return instance

    실시간 = real
    실시간.__doc__ = "실시간 WebSocket 클라이언트를 반환합니다."

    @classmethod
    def _clear_real_instance(cls, kiwoom_id: int) -> None:
        cls._real_instances.pop(kiwoom_id, None)

    @classmethod
    def _clear_all_real_instances(cls) -> None:
        cls._real_instances.clear()


__all__ = [
    Kiwoom,
]
