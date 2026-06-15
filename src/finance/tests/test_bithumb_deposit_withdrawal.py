"""빗썸(Bithumb) 입출금 관리(deposit_withdrawal) 13개 엔드포인트 테스트입니다.

- ``Test*Mock`` 클래스: ``requests_mock``으로 요청 본문/쿼리 파라미터, JWT
  Authorization 헤더, 응답 파싱을 검증합니다 (실거래 없음).
- ``Test*Live`` 클래스: ``.env``에 ``BITHUMB_ACCESS_KEY``/``BITHUMB_SECRET_KEY``가
  설정되어 있으면 조회성 엔드포인트를 실제로 호출합니다 (없으면 skip).

[!] 고위험 엔드포인트(원화입금/원화출금/가상자산출금요청/가상자산출금취소,
입금주소생성요청)는 실제 자금 이동 또는 2차 인증(카카오)이 필요하여
mock 테스트로만 검증합니다 (실거래 테스트 없음).
"""

import os

import jwt
import pytest
from dotenv import load_dotenv

from programgarden_finance import Bithumb
from programgarden_finance.bithumb.config import URLS
from programgarden_finance.bithumb.deposit_withdrawal.deposit_address_generate import DepositAddressGenerateInBlock
from programgarden_finance.bithumb.deposit_withdrawal.deposit_address import DepositAddressInBlock
from programgarden_finance.bithumb.deposit_withdrawal.deposit_addresses import DepositAddressesInBlock
from programgarden_finance.bithumb.deposit_withdrawal.deposit_krw import DepositKrwInBlock
from programgarden_finance.bithumb.deposit_withdrawal.deposits_krw import DepositsKrwInBlock
from programgarden_finance.bithumb.deposit_withdrawal.deposit_detail import DepositDetailInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraw_coin import WithdrawCoinInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraw_coin_cancel import WithdrawCoinCancelInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraw_krw import WithdrawKrwInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraws_krw import WithdrawsKrwInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraw_detail import WithdrawDetailInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraws_chance import WithdrawsChanceInBlock
from programgarden_finance.bithumb.deposit_withdrawal.withdraw_coin_addresses import WithdrawCoinAddressesInBlock

load_dotenv()

ACCESS_KEY = "test-access-key"
SECRET_KEY = "test-secret-key-0123456789abcdef0123456789abcdef"


def _dw():
    bithumb = Bithumb()
    bithumb.로그인(accesskey=ACCESS_KEY, secretkey=SECRET_KEY)
    return bithumb.입출금()


def _decode_auth(request) -> dict:
    auth = request.headers["Authorization"]
    assert auth.startswith("Bearer ")
    return jwt.decode(auth.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])


# ---------------------------------------------------------------------------
# #6 입금 주소 생성 요청 (POST /v1/deposits/generate_coin_address)
# ---------------------------------------------------------------------------

class TestDepositAddressGenerateMock:
    def test_request(self, requests_mock):
        requests_mock.post(
            URLS.DEPOSIT_ADDRESS_GENERATE_URL,
            status_code=201,
            json={"currency": "BTC", "net_type": "BTC", "deposit_address": None, "secondary_address": None},
        )

        response = _dw().입금주소생성요청(
            DepositAddressGenerateInBlock(currency="BTC", net_type="BTC")
        ).req()

        assert response.error_msg is None
        assert response.block.currency == "BTC"
        assert response.block.deposit_address is None

        sent_body = requests_mock.last_request.json()
        assert sent_body == {"currency": "BTC", "net_type": "BTC"}

        payload = _decode_auth(requests_mock.last_request)
        assert payload["query_hash_alg"] == "SHA512"

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.DEPOSIT_ADDRESS_GENERATE_URL,
            status_code=400,
            json={"error": {"name": "validation_error", "message": "currency는 필수입니다."}},
        )

        response = _dw().입금주소생성요청(DepositAddressGenerateInBlock(currency="BTC", net_type="BTC")).req()

        assert response.block is None
        assert response.error_name == "validation_error"


# ---------------------------------------------------------------------------
# #7 개별 입금 주소 조회 (GET /v1/deposits/coin_address)
# ---------------------------------------------------------------------------

class TestDepositAddressMock:
    def test_request(self, requests_mock):
        requests_mock.get(
            URLS.DEPOSIT_ADDRESS_URL,
            json={"currency": "BTC", "net_type": "BTC", "deposit_address": "3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "secondary_address": None},
        )

        response = _dw().개별입금주소조회(DepositAddressInBlock(currency="BTC", net_type="BTC")).req()

        assert response.error_msg is None
        assert response.block.deposit_address == "3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        assert "currency=BTC" in requests_mock.last_request.url
        assert "net_type=BTC" in requests_mock.last_request.url


# ---------------------------------------------------------------------------
# #8 전체 입금 주소 조회 (GET /v1/deposits/coin_addresses)
# ---------------------------------------------------------------------------

class TestDepositAddressesMock:
    def test_request(self, requests_mock):
        requests_mock.get(
            URLS.DEPOSIT_ADDRESSES_URL,
            json=[{"currency": "BTC", "net_type": "BTC", "deposit_address": "3xxx", "secondary_address": None}],
        )

        response = _dw().전체입금주소조회().req()

        assert response.error_msg is None
        assert response.blocks[0].currency == "BTC"

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.DEPOSIT_ADDRESSES_URL, json=[])

        response = _dw().전체입금주소조회(DepositAddressesInBlock()).req()

        assert response.error_msg is None
        assert response.blocks == []


# ---------------------------------------------------------------------------
# #9 원화 입금 (POST /v1/deposits/krw) - 고위험, mock only
# ---------------------------------------------------------------------------

class TestDepositKrwMock:
    def test_request(self, requests_mock):
        requests_mock.post(
            URLS.DEPOSITS_KRW_URL,
            status_code=201,
            json={
                "type": "deposit",
                "uuid": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                "currency": "KRW",
                "net_type": None,
                "txid": "12345",
                "state": "processing",
                "created_at": "2026-06-14T12:00:00+09:00",
                "done_at": None,
                "amount": "60000",
                "fee": "0",
                "transaction_type": "default",
            },
        )

        response = _dw().원화입금(DepositKrwInBlock(amount="60000", two_factor_type="kakao")).req()

        assert response.error_msg is None
        assert response.block.uuid == "9f432943-54e0-40b7-825f-b6fec382c4cb"
        assert response.block.state == "processing"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {"amount": "60000", "two_factor_type": "kakao"}

        payload = _decode_auth(requests_mock.last_request)
        assert payload["query_hash_alg"] == "SHA512"

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.DEPOSITS_KRW_URL,
            status_code=400,
            json={"error": {"name": "two_factor_auth_required", "message": "2차 인증이 필요합니다."}},
        )

        response = _dw().원화입금(DepositKrwInBlock(amount="60000", two_factor_type="kakao")).req()

        assert response.block is None
        assert response.error_name == "two_factor_auth_required"


# ---------------------------------------------------------------------------
# #10 원화 입금 리스트 조회 (GET /v1/deposits/krw)
# ---------------------------------------------------------------------------

class TestDepositsKrwMock:
    def test_request_with_params(self, requests_mock):
        requests_mock.get(
            URLS.DEPOSITS_KRW_URL,
            json=[
                {
                    "type": "deposit",
                    "uuid": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                    "currency": "KRW",
                    "txid": "12345",
                    "state": "ACCEPTED",
                    "created_at": "2026-06-10T12:00:00+09:00",
                    "done_at": "2026-06-10T12:01:00+09:00",
                    "amount": "60000",
                    "fee": "0",
                    "transaction_type": "default",
                }
            ],
        )

        response = _dw().원화입금리스트조회(DepositsKrwInBlock(state="ACCEPTED", limit=10)).req()

        assert response.error_msg is None
        assert response.blocks[0].state == "ACCEPTED"
        assert "state=ACCEPTED" in requests_mock.last_request.url
        assert "limit=10" in requests_mock.last_request.url

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.DEPOSITS_KRW_URL, json=[])

        response = _dw().원화입금리스트조회().req()

        assert response.error_msg is None
        assert response.blocks == []


# ---------------------------------------------------------------------------
# #11 개별 입금 조회 (GET /v1/deposit)
# ---------------------------------------------------------------------------

class TestDepositDetailMock:
    def test_request(self, requests_mock):
        requests_mock.get(
            URLS.DEPOSIT_DETAIL_URL,
            json={
                "type": "deposit",
                "uuid": "94332e99-3a87-4a35-ad98-28b0c969f830",
                "currency": "BTC",
                "net_type": "BTC",
                "txid": "abcd1234",
                "state": "done",
                "created_at": "2026-06-10T12:00:00+09:00",
                "done_at": "2026-06-10T12:10:00+09:00",
                "amount": "1.0",
                "fee": "0.0",
                "transaction_type": "default",
            },
        )

        response = _dw().개별입금조회(
            DepositDetailInBlock(currency="BTC", uuid="94332e99-3a87-4a35-ad98-28b0c969f830")
        ).req()

        assert response.error_msg is None
        assert response.block.state == "done"
        assert "currency=BTC" in requests_mock.last_request.url
        assert "uuid=94332e99-3a87-4a35-ad98-28b0c969f830" in requests_mock.last_request.url


# ---------------------------------------------------------------------------
# #12 가상자산 출금 요청 (POST /v1/withdraws/coin) - 고위험, mock only
# ---------------------------------------------------------------------------

class TestWithdrawCoinMock:
    def test_request(self, requests_mock):
        requests_mock.post(
            URLS.WITHDRAWS_COIN_URL,
            status_code=201,
            json={
                "type": "withdraw",
                "uuid": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                "currency": "BTC",
                "net_type": "BTC",
                "state": "PROCESSING",
                "created_at": "2026-06-14T12:00:00+09:00",
                "done_at": None,
                "amount": "0.01",
                "fee": "0.0005",
                "krw_amount": "1000000",
                "transaction_type": "default",
                "txid": None,
            },
        )

        response = _dw().가상자산출금요청(
            WithdrawCoinInBlock(
                currency="BTC",
                net_type="BTC",
                amount="0.01",
                address="3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            )
        ).req()

        assert response.error_msg is None
        assert response.block.state == "PROCESSING"
        assert response.block.krw_amount == "1000000"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {
            "currency": "BTC",
            "net_type": "BTC",
            "amount": "0.01",
            "address": "3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        }

        payload = _decode_auth(requests_mock.last_request)
        assert payload["query_hash_alg"] == "SHA512"

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.WITHDRAWS_COIN_URL,
            status_code=400,
            json={"error": {"name": "withdraw_address_not_registered", "message": "등록되지 않은 출금 주소입니다."}},
        )

        response = _dw().가상자산출금요청(
            WithdrawCoinInBlock(currency="BTC", net_type="BTC", amount="0.01", address="unregistered")
        ).req()

        assert response.block is None
        assert response.error_name == "withdraw_address_not_registered"


# ---------------------------------------------------------------------------
# #13 가상자산 출금 취소 (DELETE /v1/withdraws/coin) - 고위험, mock only
# ---------------------------------------------------------------------------

class TestWithdrawCoinCancelMock:
    def test_request(self, requests_mock):
        requests_mock.delete(
            URLS.WITHDRAWS_COIN_URL,
            json={
                "type": "withdraw",
                "withdrawal_id": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                "currency": "BTC",
                "net_type": "BTC",
                "state": "CANCELLED",
                "created_at": "2026-06-14T12:00:00+09:00",
                "amount": "0.01",
                "fee": "0.0005",
                "krw_amount": "1000000",
            },
        )

        response = _dw().가상자산출금취소(
            WithdrawCoinCancelInBlock(withdrawal_id="9f432943-54e0-40b7-825f-b6fec382c4cb")
        ).req()

        assert response.error_msg is None
        assert response.block.state == "CANCELLED"
        assert "withdrawal_id=9f432943-54e0-40b7-825f-b6fec382c4cb" in requests_mock.last_request.url

    def test_error_envelope(self, requests_mock):
        requests_mock.delete(
            URLS.WITHDRAWS_COIN_URL,
            status_code=400,
            json={"error": {"name": "withdraw_not_found", "message": "출금 내역을 찾을 수 없습니다."}},
        )

        response = _dw().가상자산출금취소(WithdrawCoinCancelInBlock(withdrawal_id="non-existent")).req()

        assert response.block is None
        assert response.error_name == "withdraw_not_found"


# ---------------------------------------------------------------------------
# #14 원화 출금 요청 (POST /v1/withdraws/krw) - 고위험, mock only
# ---------------------------------------------------------------------------

class TestWithdrawKrwMock:
    def test_request(self, requests_mock):
        requests_mock.post(
            URLS.WITHDRAWS_KRW_URL,
            status_code=201,
            json={
                "type": "withdraw",
                "uuid": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                "currency": "KRW",
                "net_type": None,
                "txid": None,
                "state": "PROCESSING",
                "created_at": "2026-06-14T12:00:00+09:00",
                "done_at": None,
                "amount": "6000",
                "fee": "1000",
                "transaction_type": "default",
            },
        )

        response = _dw().원화출금요청(WithdrawKrwInBlock(amount="6000", two_factor_type="kakao")).req()

        assert response.error_msg is None
        assert response.block.state == "PROCESSING"

        sent_body = requests_mock.last_request.json()
        assert sent_body == {"amount": "6000", "two_factor_type": "kakao"}

        payload = _decode_auth(requests_mock.last_request)
        assert payload["query_hash_alg"] == "SHA512"

    def test_error_envelope(self, requests_mock):
        requests_mock.post(
            URLS.WITHDRAWS_KRW_URL,
            status_code=400,
            json={"error": {"name": "two_factor_auth_required", "message": "2차 인증이 필요합니다."}},
        )

        response = _dw().원화출금요청(WithdrawKrwInBlock(amount="6000", two_factor_type="kakao")).req()

        assert response.block is None
        assert response.error_name == "two_factor_auth_required"


# ---------------------------------------------------------------------------
# #15 원화 출금 리스트 조회 (GET /v1/withdraws/krw)
# ---------------------------------------------------------------------------

class TestWithdrawsKrwMock:
    def test_request_with_params(self, requests_mock):
        requests_mock.get(
            URLS.WITHDRAWS_KRW_URL,
            json=[
                {
                    "type": "withdraw",
                    "uuid": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                    "currency": "KRW",
                    "net_type": None,
                    "txid": "55667788",
                    "state": "DONE",
                    "created_at": "2026-06-10T12:00:00+09:00",
                    "done_at": "2026-06-10T12:01:00+09:00",
                    "amount": "6000",
                    "fee": "1000",
                    "transaction_type": "default",
                }
            ],
        )

        response = _dw().원화출금리스트조회(WithdrawsKrwInBlock(state="DONE", order_by="asc")).req()

        assert response.error_msg is None
        assert response.blocks[0].state == "DONE"
        assert "state=DONE" in requests_mock.last_request.url
        assert "order_by=asc" in requests_mock.last_request.url

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.WITHDRAWS_KRW_URL, json=[])

        response = _dw().원화출금리스트조회().req()

        assert response.error_msg is None
        assert response.blocks == []


# ---------------------------------------------------------------------------
# #16 개별 출금 조회 (GET /v1/withdraw)
# ---------------------------------------------------------------------------

class TestWithdrawDetailMock:
    def test_request(self, requests_mock):
        requests_mock.get(
            URLS.WITHDRAW_DETAIL_URL,
            json={
                "type": "withdraw",
                "uuid": "9f432943-54e0-40b7-825f-b6fec382c4cb",
                "currency": "BTC",
                "net_type": "BTC",
                "txid": "abcd1234",
                "state": "DONE",
                "created_at": "2026-06-10T12:00:00+09:00",
                "done_at": "2026-06-10T12:10:00+09:00",
                "amount": "0.01",
                "fee": "0.0005",
                "transaction_type": "default",
            },
        )

        response = _dw().개별출금조회(
            WithdrawDetailInBlock(currency="BTC", uuid="9f432943-54e0-40b7-825f-b6fec382c4cb")
        ).req()

        assert response.error_msg is None
        assert response.block.state == "DONE"
        assert "currency=BTC" in requests_mock.last_request.url
        assert "uuid=9f432943-54e0-40b7-825f-b6fec382c4cb" in requests_mock.last_request.url


# ---------------------------------------------------------------------------
# #17 출금 가능 정보 (GET /v1/withdraws/chance)
# ---------------------------------------------------------------------------

_WITHDRAWS_CHANCE_SAMPLE = {
    "member_level": {
        "security_level": 3,
        "fee_level": 0,
        "email_verified": True,
        "identity_auth_verified": True,
        "bank_account_verified": True,
        "two_factor_auth_verified": True,
        "locked": False,
        "wallet_locked": False,
    },
    "currency": {
        "code": "BTC",
        "withdraw_fee": "0.0005",
        "is_coin": True,
        "wallet_state": "working",
        "wallet_support": ["deposit", "withdraw"],
    },
    "account": {
        "currency": "BTC",
        "balance": "1.0",
        "locked": "0.0",
        "avg_buy_price": "95000000",
        "avg_buy_price_modified": False,
        "unit_currency": "KRW",
    },
    "withdraw_limit": {
        "currency": "BTC",
        "onetime": "5",
        "daily": "10",
        "remaining_daily": "10",
        "remaining_daily_fiat": None,
        "fiat_currency": None,
        "minimum": "0.001",
        "fixed": 8,
        "withdraw_delayed_fiat": None,
        "can_withdraw": True,
        "remaining_daily_krw": None,
    },
}


class TestWithdrawsChanceMock:
    def test_request(self, requests_mock):
        requests_mock.get(URLS.WITHDRAWS_CHANCE_URL, json=_WITHDRAWS_CHANCE_SAMPLE)

        response = _dw().출금가능정보(WithdrawsChanceInBlock(currency="BTC", net_type="BTC")).req()

        assert response.error_msg is None
        assert response.block.currency.code == "BTC"
        assert response.block.withdraw_limit.can_withdraw is True
        assert response.block.member_level.two_factor_auth_verified is True
        assert "currency=BTC" in requests_mock.last_request.url
        assert "net_type=BTC" in requests_mock.last_request.url


# ---------------------------------------------------------------------------
# #18 출금 허용 주소 리스트 조회 (GET /v1/withdraws/coin_addresses)
# ---------------------------------------------------------------------------

class TestWithdrawCoinAddressesMock:
    def test_request(self, requests_mock):
        requests_mock.get(
            URLS.WITHDRAW_COIN_ADDRESSES_URL,
            json=[
                {
                    "currency": "BTC",
                    "net_type": "BTC",
                    "network_name": "Bitcoin",
                    "withdraw_address": "3xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "secondary_address": None,
                    "exchange_name": "MyExchange",
                    "owner_type": "personal",
                    "owner_ko_name": "홍길동",
                    "owner_en_name": "Hong Gildong",
                    "owner_corp_ko_name": None,
                    "owner_corp_en_name": None,
                }
            ],
        )

        response = _dw().출금허용주소리스트조회().req()

        assert response.error_msg is None
        assert response.blocks[0].owner_type == "personal"

    def test_empty_result(self, requests_mock):
        requests_mock.get(URLS.WITHDRAW_COIN_ADDRESSES_URL, json=[])

        response = _dw().출금허용주소리스트조회(WithdrawCoinAddressesInBlock()).req()

        assert response.error_msg is None
        assert response.blocks == []


# ---------------------------------------------------------------------------
# Live tests (.env의 BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY 필요, 없으면 skip)
# 조회성 엔드포인트(#7,#8,#10,#11,#15,#16,#17,#18)만 라이브로 호출합니다.
# #6/#9/#12/#13/#14(고위험/2FA 필요)는 라이브 테스트가 없습니다.
# ---------------------------------------------------------------------------

_HAS_CREDENTIALS = bool(os.getenv("BITHUMB_ACCESS_KEY")) and bool(os.getenv("BITHUMB_SECRET_KEY"))


def _skip_if_known_error(response):
    if response.error_name == "out_of_scope":
        pytest.skip("API 키에 해당 조회 권한이 없습니다 (out_of_scope).")
    if response.error_name == "NotAllowIP":
        pytest.skip("API 키의 IP 허용 목록에 현재 클라이언트 IP가 등록되어 있지 않습니다 (NotAllowIP).")


@pytest.mark.skipif(not _HAS_CREDENTIALS, reason="BITHUMB_ACCESS_KEY/BITHUMB_SECRET_KEY가 설정되지 않았습니다.")
class TestDepositWithdrawalLive:
    @pytest.fixture
    def live_dw(self):
        bithumb = Bithumb()
        bithumb.로그인(
            accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
            secretkey=os.getenv("BITHUMB_SECRET_KEY"),
        )
        return bithumb.입출금()

    def test_deposit_address(self, live_dw):
        response = live_dw.개별입금주소조회(DepositAddressInBlock(currency="BTC", net_type="BTC")).req()
        _skip_if_known_error(response)
        if response.error_name == "coin_address_not_found":
            pytest.skip("BTC 입금 주소가 아직 생성되지 않았습니다.")
        assert response.error_msg is None, response.error_msg
        assert response.block is not None

    def test_deposit_addresses(self, live_dw):
        response = live_dw.전체입금주소조회().req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_deposits_krw(self, live_dw):
        response = live_dw.원화입금리스트조회().req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_deposit_detail(self, live_dw):
        deposits_resp = live_dw.원화입금리스트조회().req()
        _skip_if_known_error(deposits_resp)
        if not deposits_resp.blocks:
            pytest.skip("조회할 원화 입금 내역이 없습니다.")

        first = deposits_resp.blocks[0]
        response = live_dw.개별입금조회(DepositDetailInBlock(currency=first.currency, uuid=first.uuid)).req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.block is not None

    def test_withdraws_krw(self, live_dw):
        response = live_dw.원화출금리스트조회().req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None

    def test_withdraw_detail(self, live_dw):
        withdraws_resp = live_dw.원화출금리스트조회().req()
        _skip_if_known_error(withdraws_resp)
        if not withdraws_resp.blocks:
            pytest.skip("조회할 원화 출금 내역이 없습니다.")

        first = withdraws_resp.blocks[0]
        response = live_dw.개별출금조회(WithdrawDetailInBlock(currency=first.currency, uuid=first.uuid)).req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.block is not None

    def test_withdraws_chance(self, live_dw):
        response = live_dw.출금가능정보(WithdrawsChanceInBlock(currency="BTC", net_type="BTC")).req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.block is not None

    def test_withdraw_coin_addresses(self, live_dw):
        response = live_dw.출금허용주소리스트조회().req()
        _skip_if_known_error(response)
        assert response.error_msg is None, response.error_msg
        assert response.blocks is not None
