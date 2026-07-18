"""키움증권(Kiwoom Securities) 접근토큰 관리자입니다.

KIS ``KisTokenManager`` 구조(갱신 Lock, 만료 skew, 파일 캐시)를 따르되
키움 API의 특성을 반영합니다.

- 토큰 발급 엔드포인트 요청 필드명이 KIS와 다릅니다: ``secretkey``
  (KIS는 ``appsecret``).
- 토큰 발급 응답 필드명도 다릅니다: ``token``(접근토큰 문자열, KIS는
  ``access_token``), ``expires_dt``(만료 "일시" 문자열 — 초 단위
  유효기간이 아님).
- ``expires_dt`` 는 정확한 포맷이 문서로 확인되지 않아 신뢰하지 않고,
  보수적인 고정 TTL(24시간)로 만료 시각을 계산합니다.
  TODO(실계좌 검증): ``expires_dt`` 실제 포맷 확인 후 필요하면 파싱 로직으로
  교체.
- 키움은 실시간 WebSocket 인증에도 REST 접근토큰을 그대로 재사용하므로
  (KIS의 ``approval_key`` 같은 별도 개념이 없음) ``get_approval_key()`` 가
  존재하지 않습니다.

보안: 토큰 캐시 파일에는 appkey/secretkey를 저장하지 않으며(토큰만
저장), 파일 권한은 사용자 전용(0o600)으로 설정합니다.
"""

import hashlib
import json
import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import requests

from programgarden_core.exceptions import TokenNotFoundException

from .config import URLS

logger = logging.getLogger("programgarden.kiwoom.token_manager")

# 토큰 재발급 임계 시간(초): 만료 5분 전부터 재발급 시도
TOKEN_REFRESH_SKEW_SECONDS = 300

# 키움 토큰 발급 응답의 expires_dt는 만료 "일시" 문자열이며 정확한 포맷이
# 문서로 확인되지 않아 파싱을 신뢰하지 않습니다. 대신 보수적인 고정
# TTL(24시간)로 만료 시각을 계산합니다.
# TODO(실계좌 검증): expires_dt 실제 포맷 확인 후 필요하면 파싱 로직으로 교체.
TOKEN_TTL_SECONDS = 24 * 60 * 60

# 기본 토큰 캐시 디렉토리
DEFAULT_CACHE_DIR = Path.home() / ".programgarden"


@dataclass
class KiwoomTokenManager:
    appkey: Optional[str] = None
    appsecret: Optional[str] = None
    paper_trading: bool = False
    access_token: Optional[str] = field(default=None, repr=False)
    expires_at: Optional[float] = None  # epoch seconds
    token_cache_path: Optional[Path] = None
    use_file_cache: bool = True

    def __post_init__(self):
        self._refresh_lock = threading.Lock()
        if self.token_cache_path is None and self.use_file_cache:
            self.token_cache_path = DEFAULT_CACHE_DIR / self._cache_filename()
        if self.use_file_cache:
            self._load_cache()

    # ─────────────────────────────────────────────── 캐시 ──

    def _cache_filename(self) -> str:
        key_hash = hashlib.sha1((self.appkey or "").encode()).hexdigest()[:8]
        mode = "mock" if self.paper_trading else "real"
        return f"kiwoom_token_{key_hash}_{mode}.json"

    def _load_cache(self) -> None:
        """파일 캐시에서 유효한 토큰을 복원합니다."""
        try:
            if self.token_cache_path and self.token_cache_path.exists():
                data = json.loads(self.token_cache_path.read_text(encoding="utf-8"))
                expires_at = data.get("expires_at")
                if expires_at and time.time() < expires_at - TOKEN_REFRESH_SKEW_SECONDS:
                    self.access_token = data.get("access_token")
                    self.expires_at = expires_at
                    logger.debug("Kiwoom 토큰 파일 캐시에서 복원")
        except Exception as e:
            logger.warning(f"Kiwoom 토큰 캐시 로드 실패 (무시): {e}")

    def _save_cache(self) -> None:
        """토큰을 파일 캐시에 저장합니다 (appkey/secretkey는 저장하지 않음)."""
        if not self.use_file_cache or self.token_cache_path is None:
            return
        try:
            self.token_cache_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "access_token": self.access_token,
                "expires_at": self.expires_at,
            }
            self.token_cache_path.write_text(
                json.dumps(payload), encoding="utf-8"
            )
            try:
                os.chmod(self.token_cache_path, 0o600)
            except OSError:
                pass  # Windows 등 chmod 미지원 환경
        except Exception as e:
            logger.warning(f"Kiwoom 토큰 캐시 저장 실패 (무시): {e}")

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
        """토큰이 만료되었거나 강제 갱신이 필요한 경우 동기적으로 갱신합니다."""
        if not force_refresh and not self.is_expired():
            return True
        return self._refresh_token()

    def get_bearer_token(self) -> str:
        """``Bearer <token>`` 형식의 토큰을 반환합니다. 만료 시 자동 갱신합니다."""
        if self.is_expired():
            self._refresh_token()
        if not self.access_token:
            raise TokenNotFoundException()
        return f"Bearer {self.access_token}"

    def _refresh_token(self) -> bool:
        """접근토큰을 발급/갱신합니다 (중복 갱신 방지 Lock)."""
        if not self.appkey or not self.appsecret:
            return False

        if not self._refresh_lock.acquire(timeout=10):
            logger.warning("Kiwoom 토큰 갱신 Lock 대기 초과 — 다른 갱신 진행 중")
            return self.is_token_available()

        try:
            if not self.is_expired():
                return True

            resp = requests.post(
                f"{self.base_url}{URLS.TOKEN_PATH}",
                json={
                    "grant_type": "client_credentials",
                    "appkey": self.appkey,
                    # 키움은 'secretkey' 필드명을 사용합니다 (KIS 'appsecret'과 다름).
                    "secretkey": self.appsecret,
                },
                headers={"Content-Type": "application/json;charset=UTF-8"},
                timeout=10,
            )
            try:
                data = resp.json()
            except ValueError:
                data = {}

            # 키움은 'token' 필드로 접근토큰을 반환합니다 (KIS 'access_token'과 다름).
            access_token = data.get("token")
            return_code = data.get("return_code")
            if resp.status_code != 200 or not access_token or return_code not in (None, 0):
                # 토큰은 민감정보이므로 에러 코드/메시지만 로그
                logger.error(
                    "Kiwoom 토큰 발급 실패: HTTP %s, return_code=%s, return_msg=%s",
                    resp.status_code,
                    return_code,
                    data.get("return_msg"),
                )
                return False

            self.access_token = access_token
            # expires_dt는 신뢰하지 않고 고정 TTL로 만료 시각을 계산합니다.
            self.expires_at = time.time() + TOKEN_TTL_SECONDS
            self._save_cache()
            logger.info(
                "Kiwoom 접근토큰 발급 완료 (고정 TTL: %d초, 서버 expires_dt=%s)",
                TOKEN_TTL_SECONDS,
                data.get("expires_dt"),
            )
            return True

        except Exception as e:
            logger.error(f"Kiwoom 토큰 발급 중 예외: {e}")
            return False
        finally:
            self._refresh_lock.release()

    def invalidate(self) -> None:
        """토큰을 무효화합니다 (만료 오류 응답 수신 시 강제 재발급용)."""
        self.access_token = None
        self.expires_at = None
