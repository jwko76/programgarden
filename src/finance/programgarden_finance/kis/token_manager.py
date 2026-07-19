"""한국투자증권(KIS) 접근토큰/승인키 관리자입니다.

LS증권의 ``TokenManager`` 구조(갱신 Lock, 만료 skew)를 따르되 KIS 특성을 반영합니다:

- 접근토큰은 24시간 유효하지만 **재발급이 약 1분당 1회로 제한**되므로
  JSON 파일 캐시로 프로세스 재시작 간에도 토큰을 재사용합니다.
- 실시간 WebSocket 접속에 필요한 ``approval_key`` 도 함께 관리합니다.
- 토큰 파일은 appkey 해시 + 실전/모의 모드별로 분리 저장됩니다.

보안: 토큰 캐시 파일에는 appkey/appsecret을 저장하지 않으며(토큰만 저장),
파일 권한은 사용자 전용(0o600)으로 설정합니다.
"""

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable, Optional, Tuple

import requests

from programgarden_core.exceptions import TokenNotFoundException

from .config import URLS

logger = logging.getLogger("programgarden.kis.token_manager")

# 토큰 재발급 임계 시간(초): 만료 5분 전부터 재발급 시도
TOKEN_REFRESH_SKEW_SECONDS = 300

# 기본 토큰 캐시 디렉토리
DEFAULT_CACHE_DIR = Path.home() / ".programgarden"


@dataclass
class KisTokenManager:
    appkey: Optional[str] = None
    appsecret: Optional[str] = None
    paper_trading: bool = False
    access_token: Optional[str] = field(default=None, repr=False)
    expires_at: Optional[float] = None  # epoch seconds
    approval_key: Optional[str] = field(default=None, repr=False)
    token_cache_path: Optional[Path] = None
    use_file_cache: bool = True
    # POST 주문 TR에 hashkey 헤더를 자동 첨부할지 여부 (클라이언트 설정 전파용)
    use_hashkey: bool = False

    # LS식 token-provider(consumer) 모드 — 외부 서버가 토큰 발급을 전담하고
    # 이 클라이언트는 소비만 한다 (appsecret 불필요, self-issue 금지).
    # 콜백은 (access_token, expires_at_epoch_seconds)를 반환한다.
    token_provider: Optional[Callable[[], Tuple[str, float]]] = field(
        default=None, compare=False, repr=False
    )
    async_token_provider: Optional[Callable[[], Awaitable[Tuple[str, float]]]] = field(
        default=None, compare=False, repr=False
    )

    def __post_init__(self):
        self._refresh_lock = threading.Lock()
        # provider 모드에서는 토큰 소유권이 외부에 있으므로 파일 캐시를 사용하지 않음
        if self.has_provider():
            self.use_file_cache = False
        if self.token_cache_path is None and self.use_file_cache:
            self.token_cache_path = DEFAULT_CACHE_DIR / self._cache_filename()
        if self.use_file_cache:
            self._load_cache()

    def has_provider(self) -> bool:
        """token-provider(consumer) 모드 여부."""
        return self.token_provider is not None or self.async_token_provider is not None

    def apply_token(self, access_token: str, expires_at: float) -> None:
        """외부에서 발급한 토큰을 직접 주입합니다 (provider/consumer 모드)."""
        self.access_token = access_token
        self.expires_at = float(expires_at)

    # ─────────────────────────────────────────────── 캐시 ──

    def _cache_filename(self) -> str:
        key_hash = hashlib.sha1((self.appkey or "").encode()).hexdigest()[:8]
        mode = "paper" if self.paper_trading else "real"
        return f"kis_token_{key_hash}_{mode}.json"

    def _load_cache(self) -> None:
        """파일 캐시에서 유효한 토큰을 복원합니다."""
        try:
            if self.token_cache_path and self.token_cache_path.exists():
                data = json.loads(self.token_cache_path.read_text(encoding="utf-8"))
                expires_at = data.get("expires_at")
                if expires_at and time.time() < expires_at - TOKEN_REFRESH_SKEW_SECONDS:
                    self.access_token = data.get("access_token")
                    self.expires_at = expires_at
                    self.approval_key = data.get("approval_key")
                    logger.debug("KIS 토큰 파일 캐시에서 복원")
        except Exception as e:
            logger.warning(f"KIS 토큰 캐시 로드 실패 (무시): {e}")

    def _save_cache(self) -> None:
        """토큰을 파일 캐시에 저장합니다 (appkey/appsecret은 저장하지 않음)."""
        if not self.use_file_cache or self.token_cache_path is None:
            return
        try:
            self.token_cache_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "access_token": self.access_token,
                "expires_at": self.expires_at,
                "approval_key": self.approval_key,
            }
            self.token_cache_path.write_text(
                json.dumps(payload), encoding="utf-8"
            )
            try:
                os.chmod(self.token_cache_path, 0o600)
            except OSError:
                pass  # Windows 등 chmod 미지원 환경
        except Exception as e:
            logger.warning(f"KIS 토큰 캐시 저장 실패 (무시): {e}")

    # ─────────────────────────────────────────────── 상태 ──

    def is_expired(self, skew_seconds: int = TOKEN_REFRESH_SKEW_SECONDS) -> bool:
        if self.expires_at is None or self.access_token is None:
            return True
        return time.time() >= (self.expires_at - skew_seconds)

    def is_token_available(self) -> bool:
        return self.access_token is not None and not self.is_expired()

    @property
    def base_url(self) -> str:
        return URLS.get_base_url(self.paper_trading)

    @property
    def ws_url(self) -> str:
        return URLS.get_ws_url(self.paper_trading)

    # ─────────────────────────────────────────────── 토큰 ──

    def ensure_fresh_token(self, force_refresh: bool = False) -> bool:
        """토큰이 만료되었거나 강제 갱신이 필요한 경우 동기적으로 갱신합니다.

        async_token_provider만 설정된 경우 동기 경로에서는 갱신할 수 없으므로
        ``ensure_fresh_token_async``를 사용하세요.
        """
        if not force_refresh and not self.is_expired():
            return True
        if self.token_provider is None and self.async_token_provider is not None:
            logger.error(
                "async_token_provider만 설정됨 — 동기 경로에서는 갱신 불가. "
                "ensure_fresh_token_async를 사용하거나 sync token_provider를 함께 설정하세요."
            )
            return self.is_token_available()
        return self._refresh_token()

    async def ensure_fresh_token_async(self, force_refresh: bool = False) -> bool:
        """비동기 토큰 갱신 — async_token_provider가 있으면 우선 사용합니다."""
        if not force_refresh and not self.is_expired():
            return True
        if self.async_token_provider is not None:
            try:
                access_token, expires_at = await self.async_token_provider()
                if access_token:
                    self.apply_token(access_token, expires_at)
                    logger.info("KIS 토큰을 async_token_provider로 갱신 완료")
                    return True
                logger.error("KIS async_token_provider가 빈 access_token을 반환")
                return False
            except Exception as e:
                logger.error(f"KIS async_token_provider 호출 중 예외: {e}")
                return False
        import asyncio as _asyncio
        return await _asyncio.to_thread(self._refresh_token)

    def get_bearer_token(self) -> str:
        """``Bearer <token>`` 형식의 토큰을 반환합니다. 만료 시 자동 갱신합니다."""
        if self.is_expired():
            self._refresh_token()
        if not self.access_token:
            raise TokenNotFoundException()
        return f"Bearer {self.access_token}"

    def _refresh_token(self) -> bool:
        """접근토큰을 발급/갱신합니다 (중복 갱신 방지 Lock).

        KIS 재발급 제한(약 1분당 1회) 때문에 실패 시 즉시 재시도하지 않습니다.
        token-provider 모드에서는 외부 서버가 유일한 발급자이며 self-issue하지 않습니다.
        """
        # provider/consumer 모드 — 콜백에서 토큰을 받아 주입 (appsecret 불필요)
        if self.token_provider is not None:
            if not self._refresh_lock.acquire(timeout=10):
                logger.warning("KIS 토큰 갱신 Lock 대기 초과 — 다른 갱신 진행 중")
                return self.is_token_available()
            try:
                if not self.is_expired():
                    return True
                access_token, expires_at = self.token_provider()
                if access_token:
                    self.apply_token(access_token, expires_at)
                    logger.info("KIS 토큰을 token_provider로 갱신 완료")
                    return True
                logger.error("KIS token_provider가 빈 access_token을 반환")
                return False
            except Exception as e:
                logger.error(f"KIS token_provider 호출 중 예외: {e}")
                return False
            finally:
                self._refresh_lock.release()

        if not self.appkey or not self.appsecret:
            return False

        if not self._refresh_lock.acquire(timeout=10):
            logger.warning("KIS 토큰 갱신 Lock 대기 초과 — 다른 갱신 진행 중")
            return self.is_token_available()

        try:
            if not self.is_expired():
                return True

            resp = requests.post(
                f"{self.base_url}{URLS.TOKEN_PATH}",
                json={
                    "grant_type": "client_credentials",
                    "appkey": self.appkey,
                    "appsecret": self.appsecret,
                },
                headers={"Content-Type": "application/json"},
                timeout=10,
            )
            data = resp.json()

            access_token = data.get("access_token")
            if resp.status_code != 200 or not access_token:
                # 토큰은 민감정보이므로 에러 코드/메시지만 로그
                logger.error(
                    "KIS 토큰 발급 실패: HTTP %s, error_code=%s, error_description=%s",
                    resp.status_code,
                    data.get("error_code"),
                    data.get("error_description"),
                )
                return False

            self.access_token = access_token
            expires_in = data.get("expires_in")
            self.expires_at = time.time() + int(expires_in or 86400)
            self._save_cache()
            logger.info("KIS 접근토큰 발급 완료 (만료: %d초 후)", int(expires_in or 86400))
            return True

        except Exception as e:
            logger.error(f"KIS 토큰 발급 중 예외: {e}")
            return False
        finally:
            self._refresh_lock.release()

    # ────────────────────────────────────────── approval_key ──

    def get_approval_key(self, force_refresh: bool = False) -> str:
        """실시간 WebSocket 접속용 approval_key를 반환합니다 (필요 시 발급)."""
        if self.approval_key and not force_refresh:
            return self.approval_key

        if not self.appkey or not self.appsecret:
            raise TokenNotFoundException()

        resp = requests.post(
            f"{self.base_url}{URLS.APPROVAL_PATH}",
            json={
                "grant_type": "client_credentials",
                "appkey": self.appkey,
                "secretkey": self.appsecret,  # Approval은 'secretkey' 키 사용 (tokenP와 다름)
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        data = resp.json()
        approval_key = data.get("approval_key")
        if resp.status_code != 200 or not approval_key:
            logger.error("KIS approval_key 발급 실패: HTTP %s", resp.status_code)
            raise TokenNotFoundException()

        self.approval_key = approval_key
        self._save_cache()
        logger.info("KIS approval_key 발급 완료")
        return approval_key

    def invalidate(self) -> None:
        """토큰을 무효화합니다 (만료 오류 응답 수신 시 강제 재발급용)."""
        self.access_token = None
        self.expires_at = None
