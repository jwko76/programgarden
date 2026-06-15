"""빗썸(Bithumb) 계좌(Account, 비공개 API) 테스트입니다.

- ``Test*Mock`` 클래스: ``requests_mock`` + 더미 access_key/secret_key로 요청 헤더(JWT)/
  쿼리 파라미터/응답 파싱을 검증합니다 (실제 API 키 불필요).
- ``TestAccountLive`` 클래스: ``.env``에 ``BITHUMB_ACCESS_KEY``/``BITHUMB_SECRET_KEY``가
  설정되어 있으면 실제 계좌 API를 호출합니다 (없으면 skip).
"""

import os

import jwt
import pytest
from dotenv import load_dotenv

from programgarden_core.exceptions import LoginException
from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.account.deposits import DepositsInBlock
from programgarden_finance.bithumb.account.withdraws import WithdrawsInBlock

load_dotenv()

ACCESS_KEY = "test-access-key"
SECRET_KEY = "test-secret-key-0123456789abcdef0123456789abcdef"


def _account():
    bithumb = Bithumb()
    bithumb.로그인(accesskey=ACCESS_KEY, secretkey=SECRET_KEY)
    return bithumb.계좌()


def _assert_valid_auth_header(request) -> dict:
    auth = request.headers["Authorization"]
    assert auth.startswith("Bearer ")
    payload = jwt.decode(auth.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])
    assert payload["access_key"] == ACCESS_KEY
    assert "nonce" in payload
    assert "timestamp" in payload
    return payload


# ---------------------------------------------------------------------------
# Mock tests
# ---------------------------------------------------------------------------


class TestAccountLoginGate:
    def test_account_requires_login(self):
        with pytest.raises(LoginException):
            Bithumb().계좌()


class TestAccountsMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(
            URLS.ACCOUNTS_URL,
            json=[
                {
                    "currency": "BTC",
                    "balance": "2.0",
                    "locked": "0.0",
                    "avg_buy_price": "95000000",
                    "avg_buy_price_modified": False,
                    "unit_currency": "KRW",
                }
            ],
        )

        response = _account().전체자산조회().req()

        assert response.error_msg is None
        assert response.blocks[0].currency == "BTC"
        _assert_valid_auth_header(requests_mock.last_request)

    def test_error_envelope(self, requests_mock):
        requests_mock.get(
            URLS.ACCOUNTS_URL,
            status_code=401,
            json={"error": {"name": "invalid_access_key", "message": "No Authorization Key"}},
        )

        response = _account().전체자산조회().req()

        assert response.blocks is None
        assert response.error_name == "invalid_access_key"
        assert response.error_msg == "No Authorization Key"
        assert response.status_code == 401


class TestWalletStatusMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(
            URLS.WALLET_STATUS_URL,
            json=[
                {
                    "currency": "BTC",
                    "wallet_state": "working",
                    "block_state": "normal",
                    "block_height": 860000,
                    "block_updated_at": "2026-06-14T11:00:00+09:00",
                    "block_elapsed_minutes": 5,
                    "net_type": "BTC",
                }
            ],
        )

        response = _account().입출금현황().req()

        assert response.error_msg is None
        assert response.blocks[0].wallet_state == "working"
        _assert_valid_auth_header(requests_mock.last_request)


class TestDepositsMock:
    def test_request_with_params(self, requests_mock):
        requests_mock.get(
            URLS.DEPOSITS_URL,
            json=[
                {
                    "type": "deposit",
                    "uuid": "94332e99-3a87-4a35-ad98-28b0c969f830",
                    "currency": "BTC",
                    "net_type": "BTC",
                    "txid": "abc123",
                    "state": "done",
                    "created_at": "2026-06-10T12:30:00+09:00",
                    "done_at": "2026-06-10T12:40:00+09:00",
                    "amount": "1.0",
                    "fee": "0.0",
                    "transaction_type": "default",
                }
            ],
        )

        response = _account().입금리스트조회(DepositsInBlock(currency="BTC", limit=5)).req()

        assert response.error_msg is None
        assert response.blocks[0].state == "done"

        payload = _assert_valid_auth_header(requests_mock.last_request)
        assert "query_hash" in payload
        assert payload["query_hash_alg"] == "SHA512"
        assert "currency=BTC" in requests_mock.last_request.url
        assert "limit=5" in requests_mock.last_request.url

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.DEPOSITS_URL, json=[])

        response = _account().입금리스트조회().req()

        assert response.error_msg is None
        assert response.blocks == []


class TestWithdrawsMock:
    def test_request_with_params(self, requests_mock):
        requests_mock.get(
            URLS.WITHDRAWS_URL,
            json=[
                {
                    "type": "withdraw",
                    "uuid": "94332e99-3a87-4a35-ad98-28b0c969f830",
                    "currency": "BTC",
                    "net_type": "BTC",
                    "txid": "abc123",
                    "state": "done",
                    "created_at": "2026-06-10T12:30:00+09:00",
                    "done_at": "2026-06-10T12:40:00+09:00",
                    "amount": "1.0",
                    "fee": "0.0005",
                    "transaction_type": "default",
                }
            ],
        )

        response = _account().출금리스트조회(WithdrawsInBlock(currency="BTC", limit=5)).req()

        assert response.error_msg is None
        assert response.blocks[0].fee == "0.0005"
        _assert_valid_auth_header(requests_mock.last_request)

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.WITHDRAWS_URL, json=[])

        response = _account().출금리스트조회().req()

        assert response.error_msg is None
        assert response.blocks == []


class TestApiKeysMock:
    def test_request_and_parse(self, requests_mock):
        requests_mock.get(
            URLS.API_KEYS_URL,
            json=[
                {
                    "access_key": "59683c90185742d69fd8fa1bc0cf27785c392afaa56ece",
                    "expire_at": "2026-12-11T09:00:00+09:00",
                }
            ],
        )

        response = _account().API키리스트조회().req()

        assert response.error_msg is None
        assert response.blocks[0].access_key == "59683c90185742d69fd8fa1bc0cf27785c392afaa56ece"
        assert response.blocks[0].expire_at == "2026-12-11T09:00:00+09:00"
        _assert_valid_auth_header(requests_mock.last_request)

    def test_error_envelope(self, requests_mock):
        requests_mock.get(
            URLS.API_KEYS_URL,
            status_code=401,
            json={"error": {"name": "invalid_access_key", "message": "No Authorization Key"}},
        )

        response = _account().API키리스트조회().req()

        assert response.blocks is None
        assert response.error_name == "invalid_access_key"
        assert response.error_msg == "No Authorization Key"


# ---------------------------------------------------------------------------
# Live tests (.env의 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY 필요, 없으면 skip)
# ---------------------------------------------------------------------------

_HAS_CREDENTIALS = bool(os.getenv("BITHUMB_ACCESS_KEY")) and bool(os.getenv("BITHUMB_SECRET_KEY"))


@pytest.mark.skipif(not _HAS_CREDENTIALS, reason="BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY가 설정되지 않았습니다.")
class TestAccountLive:
    @pytest.fixture
    def live_account(self):
        bithumb = Bithumb()
        bithumb.로그인(
            accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
            secretkey=os.getenv("BITHUMB_SECRET_KEY"),
        )
        return bithumb.계좌()

    def test_accounts(self, live_account):
        response = live_account.전체자산조회().req()
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_wallet_status(self, live_account):
        response = live_account.입출금현황().req()
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_deposits(self, live_account):
        response = live_account.입금리스트조회().req()
        if response.error_name == "out_of_scope":
            pytest.skip("API 키에 입출금 조회 권한이 없습니다 (out_of_scope).")
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_withdraws(self, live_account):
        response = live_account.출금리스트조회().req()
        if response.error_name == "out_of_scope":
            pytest.skip("API 키에 입출금 조회 권한이 없습니다 (out_of_scope).")
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_api_keys(self, live_account):
        response = live_account.API키리스트조회().req()
        if response.error_name == "NotAllowIP":
            pytest.skip("API 키의 IP 허용 목록에 현재 클라이언트 IP가 등록되어 있지 않습니다 (NotAllowIP).")
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None
