"""KIS token-provider(LS식 consumer) 모드 테스트.

외부 서버가 토큰 발급을 전담하고 이 클라이언트는 소비만 하는 모드.
appsecret 없이도 동작해야 하며, 자체 발급(POST /oauth2/tokenP) 호출이
절대 발생하지 않아야 한다.
"""

import time

import pytest

from programgarden_finance.kis.config import URLS
from programgarden_finance.kis.token_manager import KisTokenManager

TOKEN_URL_PAPER = f"{URLS.PAPER_URL}{URLS.TOKEN_PATH}"


class TestSyncProvider:
    def test_provider_supplies_token_without_appsecret(self, requests_mock):
        calls = {"n": 0}

        def provider():
            calls["n"] += 1
            return ("provider-tok", time.time() + 3600)

        tm = KisTokenManager(appkey="ak", paper_trading=True, token_provider=provider)

        assert tm.get_bearer_token() == "Bearer provider-tok"
        assert calls["n"] == 1
        # 자체 발급 엔드포인트는 절대 호출되지 않아야 함
        assert requests_mock.call_count == 0

    def test_provider_disables_file_cache(self, tmp_path):
        tm = KisTokenManager(
            appkey="ak",
            paper_trading=True,
            token_provider=lambda: ("t", time.time() + 3600),
            use_file_cache=True,  # provider 모드에서는 자동으로 무시되어야 함
            token_cache_path=tmp_path / "should_not_exist.json",
        )
        tm.ensure_fresh_token()
        assert tm.use_file_cache is False
        assert not (tmp_path / "should_not_exist.json").exists()

    def test_cached_provider_token_not_refetched(self):
        calls = {"n": 0}

        def provider():
            calls["n"] += 1
            return ("tok", time.time() + 3600)

        tm = KisTokenManager(appkey="ak", paper_trading=True, token_provider=provider)
        tm.ensure_fresh_token()
        tm.ensure_fresh_token()  # 아직 만료 전 — 재호출 없어야 함
        assert calls["n"] == 1

    def test_empty_token_from_provider_returns_false(self):
        tm = KisTokenManager(appkey="ak", paper_trading=True, token_provider=lambda: ("", 0))
        assert tm.ensure_fresh_token() is False


class TestAsyncProvider:
    @pytest.mark.asyncio
    async def test_async_provider_supplies_token(self, requests_mock):
        async def provider():
            return ("async-tok", time.time() + 3600)

        tm = KisTokenManager(appkey="ak", paper_trading=True, async_token_provider=provider)
        assert await tm.ensure_fresh_token_async() is True
        assert tm.access_token == "async-tok"
        assert requests_mock.call_count == 0

    @pytest.mark.asyncio
    async def test_sync_ensure_fresh_token_rejects_async_only_provider(self):
        """async_token_provider만 있고 sync 경로로 호출하면 self-issue하지 않고 실패해야 한다."""
        async def provider():
            return ("t", time.time() + 3600)

        tm = KisTokenManager(appkey="ak", appsecret="sk", paper_trading=True, async_token_provider=provider)
        assert tm.ensure_fresh_token() is False
        assert tm.access_token is None


class TestClientIntegration:
    def test_kis_client_accepts_token_provider(self):
        from programgarden_finance import Kis

        kis = Kis(paper_trading=True, token_provider=lambda: ("t", time.time() + 3600))
        assert kis.token_manager.has_provider() is True
