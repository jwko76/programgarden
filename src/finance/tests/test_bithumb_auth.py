"""빗썸(Bithumb) JWT 인증 헤더 생성(``auth.py``)에 대한 단위 테스트입니다.

API 키 없이 더미 access_key/secret_key로 JWT payload 구조
(access_key/nonce/timestamp/query_hash)를 검증합니다.
"""

import hashlib
from urllib.parse import urlencode

import jwt
import pytest

from programgarden_core.exceptions import AppKeyException
from programgarden_finance.bithumb.auth import build_authorization_header
from programgarden_finance.bithumb.models import BithumbCredentials, SetupOptions
from programgarden_finance.bithumb.tr_helpers import _serialize_query_params

ACCESS_KEY = "test-access-key"
SECRET_KEY = "test-secret-key-0123456789abcdef0123456789abcdef"


class TestBuildAuthorizationHeader:
    def test_missing_keys_raises(self):
        with pytest.raises(AppKeyException):
            build_authorization_header(None, None)

    def test_missing_secret_raises(self):
        with pytest.raises(AppKeyException):
            build_authorization_header(ACCESS_KEY, None)

    def test_missing_access_key_raises(self):
        with pytest.raises(AppKeyException):
            build_authorization_header("", SECRET_KEY)

    def test_returns_bearer_token(self):
        header = build_authorization_header(ACCESS_KEY, SECRET_KEY)
        assert header.startswith("Bearer ")

    def test_payload_without_query_params(self):
        header = build_authorization_header(ACCESS_KEY, SECRET_KEY)
        token = header.removeprefix("Bearer ")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        assert payload["access_key"] == ACCESS_KEY
        assert "nonce" in payload
        assert "timestamp" in payload
        assert "query_hash" not in payload
        assert "query_hash_alg" not in payload

    def test_payload_with_query_params(self):
        query_params = {"market": "KRW-BTC", "states": ["wait", "watch"]}
        header = build_authorization_header(ACCESS_KEY, SECRET_KEY, query_params)
        token = header.removeprefix("Bearer ")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        expected_hash = hashlib.sha512(
            urlencode(query_params, doseq=True).encode()
        ).hexdigest()

        assert payload["query_hash"] == expected_hash
        assert payload["query_hash_alg"] == "SHA512"

    def test_nonce_is_unique_per_call(self):
        header1 = build_authorization_header(ACCESS_KEY, SECRET_KEY)
        header2 = build_authorization_header(ACCESS_KEY, SECRET_KEY)

        payload1 = jwt.decode(header1.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])
        payload2 = jwt.decode(header2.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])

        assert payload1["nonce"] != payload2["nonce"]

    def test_invalid_signature_rejected(self):
        header = build_authorization_header(ACCESS_KEY, SECRET_KEY)
        token = header.removeprefix("Bearer ")
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, "wrong-secret-0123456789abcdef0123456789abcdef", algorithms=["HS256"])


class TestBithumbCredentials:
    def test_is_available_false_when_empty(self):
        creds = BithumbCredentials()
        assert creds.is_available() is False

    def test_is_available_false_when_partial(self):
        creds = BithumbCredentials(access_key=ACCESS_KEY)
        assert creds.is_available() is False

    def test_is_available_true_when_both_set(self):
        creds = BithumbCredentials(access_key=ACCESS_KEY, secret_key=SECRET_KEY)
        assert creds.is_available() is True

    def test_get_authorization_header_delegates(self):
        creds = BithumbCredentials(access_key=ACCESS_KEY, secret_key=SECRET_KEY)
        header = creds.get_authorization_header({"market": "KRW-BTC"})

        assert header.startswith("Bearer ")
        payload = jwt.decode(header.removeprefix("Bearer "), SECRET_KEY, algorithms=["HS256"])
        assert payload["access_key"] == ACCESS_KEY
        assert "query_hash" in payload

    def test_get_authorization_header_raises_without_keys(self):
        creds = BithumbCredentials()
        with pytest.raises(AppKeyException):
            creds.get_authorization_header()


class TestSerializeQueryParams:
    def test_bool_converted_to_lowercase_string(self):
        assert _serialize_query_params({"isDetails": True}) == {"isDetails": "true"}
        assert _serialize_query_params({"isDetails": False}) == {"isDetails": "false"}

    def test_non_bool_values_unchanged(self):
        assert _serialize_query_params({"market": "KRW-BTC", "count": 5}) == {"market": "KRW-BTC", "count": 5}

    def test_bool_in_list_converted(self):
        result = _serialize_query_params({"flags": [True, False]})
        assert result == {"flags": ["true", "false"]}


class TestSetupOptionsDefaults:
    def test_public_defaults(self):
        options = SetupOptions()
        assert options.rate_limit_count == 130
        assert options.rate_limit_seconds == 1
        assert options.on_rate_limit == "wait"
        assert options.credentials is None

    def test_credentials_excluded_from_dump(self):
        options = SetupOptions(credentials=BithumbCredentials(access_key=ACCESS_KEY, secret_key=SECRET_KEY))
        assert "credentials" not in options.model_dump()
