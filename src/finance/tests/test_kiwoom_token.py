"""키움증권 토큰 관리자(KiwoomTokenManager) 테스트.

- 토큰 발급/캐시/만료 갱신 (requests_mock — 실제 API 호출 없음)
- 파일 캐시 round-trip
- 키움 특유 필드명 확인: 요청 'secretkey' (KIS 'appsecret'과 다름),
  응답 'token' (KIS 'access_token'과 다름)
- expires_dt 미신뢰 → 고정 TTL 사용 확인
"""

import json
import time

import pytest

from programgarden_finance.kiwoom.config import URLS
from programgarden_finance.kiwoom.token_manager import (
    KiwoomTokenManager,
    TOKEN_REFRESH_SKEW_SECONDS,
    TOKEN_TTL_SECONDS,
)

TOKEN_URL_REAL = f"{URLS.PROD_URL}{URLS.TOKEN_PATH}"
TOKEN_URL_MOCK = f"{URLS.MOCK_URL}{URLS.TOKEN_PATH}"


def _make_manager(**kwargs) -> KiwoomTokenManager:
    defaults = dict(
        appkey="test-appkey",
        appsecret="test-appsecret",
        paper_trading=True,
        use_file_cache=False,
    )
    defaults.update(kwargs)
    return KiwoomTokenManager(**defaults)


class TestTokenIssue:
    def test_issue_token_success(self, requests_mock):
        requests_mock.post(
            TOKEN_URL_MOCK,
            json={"token": "tok-123", "token_type": "bearer", "return_code": 0, "return_msg": "정상"},
        )
        tm = _make_manager()
        assert tm.ensure_fresh_token() is True
        assert tm.access_token == "tok-123"
        assert tm.get_bearer_token() == "Bearer tok-123"

        # 발급 요청 본문 확인 — 'secretkey' 필드 사용 (KIS의 'appsecret'과 다름)
        body = requests_mock.last_request.json()
        assert body["grant_type"] == "client_credentials"
        assert body["appkey"] == "test-appkey"
        assert body["secretkey"] == "test-appsecret"
        assert "appsecret" not in body

    def test_paper_flag_selects_mock_domain(self, requests_mock):
        mock_ep = requests_mock.post(TOKEN_URL_MOCK, json={"token": "p", "return_code": 0})
        real_ep = requests_mock.post(TOKEN_URL_REAL, json={"token": "r", "return_code": 0})

        _make_manager(paper_trading=True).ensure_fresh_token()
        assert mock_ep.call_count == 1 and real_ep.call_count == 0

        _make_manager(paper_trading=False).ensure_fresh_token()
        assert real_ep.call_count == 1

    def test_cached_token_skips_reissue(self, requests_mock):
        mock = requests_mock.post(TOKEN_URL_MOCK, json={"token": "tok", "return_code": 0})
        tm = _make_manager()
        tm.ensure_fresh_token()
        tm.ensure_fresh_token()
        tm.get_bearer_token()
        assert mock.call_count == 1

    def test_expired_token_triggers_refresh(self, requests_mock):
        mock = requests_mock.post(TOKEN_URL_MOCK, json={"token": "new-tok", "return_code": 0})
        tm = _make_manager()
        tm.access_token = "old-tok"
        tm.expires_at = time.time() + TOKEN_REFRESH_SKEW_SECONDS - 10  # skew 안쪽 → 만료 취급
        assert tm.is_expired() is True
        assert tm.get_bearer_token() == "Bearer new-tok"
        assert mock.call_count == 1

    def test_issue_failure_returns_false(self, requests_mock):
        requests_mock.post(
            TOKEN_URL_MOCK,
            status_code=403,
            json={"return_code": 1, "return_msg": "인증 실패"},
        )
        tm = _make_manager()
        assert tm.ensure_fresh_token() is False
        assert tm.access_token is None

    def test_nonzero_return_code_treated_as_failure(self, requests_mock):
        """HTTP 200이어도 return_code != 0이면 실패로 처리해야 합니다."""
        requests_mock.post(
            TOKEN_URL_MOCK,
            status_code=200,
            json={"token": "should-not-be-used", "return_code": 1, "return_msg": "실패"},
        )
        tm = _make_manager()
        assert tm.ensure_fresh_token() is False
        assert tm.access_token is None

    def test_invalidate_forces_reissue(self, requests_mock):
        mock = requests_mock.post(TOKEN_URL_MOCK, json={"token": "tok2", "return_code": 0})
        tm = _make_manager()
        tm.ensure_fresh_token()
        tm.invalidate()
        assert tm.is_expired() is True
        tm.ensure_fresh_token(force_refresh=True)
        assert mock.call_count == 2

    def test_expires_dt_not_trusted_uses_fixed_ttl(self, requests_mock):
        """expires_dt가 파싱 불가능한 형식이어도 고정 TTL로 만료 시각을 계산해야 합니다."""
        requests_mock.post(
            TOKEN_URL_MOCK,
            json={"token": "tok", "return_code": 0, "expires_dt": "이상한형식"},
        )
        tm = _make_manager()
        before = time.time()
        tm.ensure_fresh_token()
        after = time.time()
        assert tm.expires_at is not None
        assert before + TOKEN_TTL_SECONDS <= tm.expires_at <= after + TOKEN_TTL_SECONDS


class TestFileCache:
    def test_cache_roundtrip(self, requests_mock, tmp_path):
        requests_mock.post(TOKEN_URL_MOCK, json={"token": "cached-tok", "return_code": 0})
        cache_path = tmp_path / "kiwoom_token_test.json"

        tm1 = _make_manager(use_file_cache=True, token_cache_path=cache_path)
        tm1.ensure_fresh_token()
        assert cache_path.exists()

        saved = json.loads(cache_path.read_text(encoding="utf-8"))
        assert saved["access_token"] == "cached-tok"
        # 보안: appkey/secretkey는 캐시에 저장하지 않음
        assert "appkey" not in saved and "appsecret" not in saved and "secretkey" not in saved

        # 새 인스턴스가 파일 캐시에서 토큰 복원 → 재발급 없음
        tm2 = _make_manager(use_file_cache=True, token_cache_path=cache_path)
        assert tm2.access_token == "cached-tok"
        assert tm2.is_expired() is False

    def test_expired_cache_ignored(self, tmp_path):
        cache_path = tmp_path / "kiwoom_token_expired.json"
        cache_path.write_text(
            json.dumps({"access_token": "stale", "expires_at": time.time() - 100}),
            encoding="utf-8",
        )
        tm = _make_manager(use_file_cache=True, token_cache_path=cache_path)
        assert tm.access_token is None


class TestNoApprovalKey:
    def test_token_manager_has_no_approval_key_api(self):
        """키움은 approval_key 개념이 없으므로 관련 API가 없어야 합니다."""
        tm = _make_manager()
        assert not hasattr(tm, "get_approval_key")
        assert not hasattr(tm, "approval_key")
