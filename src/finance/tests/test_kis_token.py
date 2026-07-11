"""KIS 토큰 관리자(KisTokenManager) 테스트.

- 토큰 발급/캐시/만료 갱신 (requests_mock — 실제 API 호출 없음)
- 파일 캐시 round-trip
- approval_key 발급
"""

import json
import time

import pytest

from programgarden_finance.kis.config import URLS
from programgarden_finance.kis.token_manager import (
    KisTokenManager,
    TOKEN_REFRESH_SKEW_SECONDS,
)

TOKEN_URL_REAL = f"{URLS.REAL_URL}{URLS.TOKEN_PATH}"
TOKEN_URL_PAPER = f"{URLS.PAPER_URL}{URLS.TOKEN_PATH}"
APPROVAL_URL_PAPER = f"{URLS.PAPER_URL}{URLS.APPROVAL_PATH}"


def _make_manager(**kwargs) -> KisTokenManager:
    defaults = dict(
        appkey="test-appkey",
        appsecret="test-appsecret",
        paper_trading=True,
        use_file_cache=False,
    )
    defaults.update(kwargs)
    return KisTokenManager(**defaults)


class TestTokenIssue:
    def test_issue_token_success(self, requests_mock):
        requests_mock.post(
            TOKEN_URL_PAPER,
            json={"access_token": "tok-123", "expires_in": 86400, "token_type": "Bearer"},
        )
        tm = _make_manager()
        assert tm.ensure_fresh_token() is True
        assert tm.access_token == "tok-123"
        assert tm.get_bearer_token() == "Bearer tok-123"
        # 발급 요청 본문 확인
        body = requests_mock.last_request.json()
        assert body["grant_type"] == "client_credentials"
        assert body["appkey"] == "test-appkey"

    def test_paper_flag_selects_paper_domain(self, requests_mock):
        paper = requests_mock.post(
            TOKEN_URL_PAPER, json={"access_token": "p", "expires_in": 86400}
        )
        real = requests_mock.post(
            TOKEN_URL_REAL, json={"access_token": "r", "expires_in": 86400}
        )
        _make_manager(paper_trading=True).ensure_fresh_token()
        assert paper.call_count == 1 and real.call_count == 0

        _make_manager(paper_trading=False).ensure_fresh_token()
        assert real.call_count == 1

    def test_cached_token_skips_reissue(self, requests_mock):
        mock = requests_mock.post(
            TOKEN_URL_PAPER, json={"access_token": "tok", "expires_in": 86400}
        )
        tm = _make_manager()
        tm.ensure_fresh_token()
        tm.ensure_fresh_token()
        tm.get_bearer_token()
        # 유효한 토큰이 있으면 재발급하지 않음 (KIS 분당 1회 제한 회피)
        assert mock.call_count == 1

    def test_expired_token_triggers_refresh(self, requests_mock):
        mock = requests_mock.post(
            TOKEN_URL_PAPER, json={"access_token": "new-tok", "expires_in": 86400}
        )
        tm = _make_manager()
        tm.access_token = "old-tok"
        tm.expires_at = time.time() + TOKEN_REFRESH_SKEW_SECONDS - 10  # skew 안쪽 → 만료 취급
        assert tm.is_expired() is True
        assert tm.get_bearer_token() == "Bearer new-tok"
        assert mock.call_count == 1

    def test_issue_failure_returns_false(self, requests_mock):
        requests_mock.post(
            TOKEN_URL_PAPER,
            status_code=403,
            json={"error_code": "EGW00133", "error_description": "발급 제한"},
        )
        tm = _make_manager()
        assert tm.ensure_fresh_token() is False
        assert tm.access_token is None

    def test_invalidate_forces_reissue(self, requests_mock):
        mock = requests_mock.post(
            TOKEN_URL_PAPER, json={"access_token": "tok2", "expires_in": 86400}
        )
        tm = _make_manager()
        tm.ensure_fresh_token()
        tm.invalidate()
        assert tm.is_expired() is True
        tm.ensure_fresh_token(force_refresh=True)
        assert mock.call_count == 2


class TestFileCache:
    def test_cache_roundtrip(self, requests_mock, tmp_path):
        requests_mock.post(
            TOKEN_URL_PAPER, json={"access_token": "cached-tok", "expires_in": 86400}
        )
        cache_path = tmp_path / "kis_token_test.json"

        tm1 = _make_manager(use_file_cache=True, token_cache_path=cache_path)
        tm1.ensure_fresh_token()
        assert cache_path.exists()

        saved = json.loads(cache_path.read_text(encoding="utf-8"))
        assert saved["access_token"] == "cached-tok"
        # 보안: appkey/appsecret은 캐시에 저장하지 않음
        assert "appkey" not in saved and "appsecret" not in saved

        # 새 인스턴스가 파일 캐시에서 토큰 복원 → 재발급 없음
        tm2 = _make_manager(use_file_cache=True, token_cache_path=cache_path)
        assert tm2.access_token == "cached-tok"
        assert tm2.is_expired() is False

    def test_expired_cache_ignored(self, tmp_path):
        cache_path = tmp_path / "kis_token_expired.json"
        cache_path.write_text(
            json.dumps({"access_token": "stale", "expires_at": time.time() - 100}),
            encoding="utf-8",
        )
        tm = _make_manager(use_file_cache=True, token_cache_path=cache_path)
        assert tm.access_token is None


class TestApprovalKey:
    def test_approval_key_issue_and_cache(self, requests_mock):
        mock = requests_mock.post(
            APPROVAL_URL_PAPER, json={"approval_key": "appr-key-1"}
        )
        tm = _make_manager()
        assert tm.get_approval_key() == "appr-key-1"
        assert tm.get_approval_key() == "appr-key-1"  # 캐시 사용
        assert mock.call_count == 1
        # Approval 요청은 'secretkey' 키를 사용 (tokenP의 'appsecret'과 다름)
        body = mock.last_request.json()
        assert body["secretkey"] == "test-appsecret"

    def test_approval_key_failure_raises(self, requests_mock):
        from programgarden_core.exceptions import TokenNotFoundException

        requests_mock.post(APPROVAL_URL_PAPER, status_code=403, json={})
        tm = _make_manager()
        with pytest.raises(TokenNotFoundException):
            tm.get_approval_key()
