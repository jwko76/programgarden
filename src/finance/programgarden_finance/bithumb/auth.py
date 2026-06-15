"""빗썸(Bithumb) OpenAPI 요청 인증을 위한 JWT 헤더 생성 유틸리티입니다."""

import hashlib
import time
import uuid
from typing import Mapping, Optional
from urllib.parse import urlencode

import jwt

from programgarden_core.exceptions import AppKeyException


def build_authorization_header(
    access_key: Optional[str],
    secret_key: Optional[str],
    query_params: Optional[Mapping[str, object]] = None,
    raw_query_string: Optional[str] = None,
) -> str:
    """빗썸 Private API 호출에 필요한 ``Authorization: Bearer <JWT>`` 헤더 값을 생성합니다.

    LS증권의 OAuth 토큰 발급/갱신과 달리 빗썸은 매 요청마다 access_key, nonce(uuid4),
    timestamp(ms)를 담은 JWT를 HS256으로 서명해 사용합니다. query_params가 주어지면
    ``urlencode(query_params, doseq=True)``로 직렬화한 문자열의 SHA512 해시를
    ``query_hash``로 포함합니다 (GET/DELETE 쿼리, POST JSON body 모두 동일 규칙).

    일부 엔드포인트(예: 다건 주문/취소)는 ``urlencode(doseq=True)``가 아닌 자체 직렬화
    규칙(``batch_orders[0][market]=...``, ``order_ids[]=...`` 등)을 사용한다. 이 경우
    ``raw_query_string``으로 이미 직렬화된 문자열을 직접 전달하면, ``query_params``
    대신 해당 문자열을 그대로 SHA512 해싱한다.
    """

    if not access_key or not secret_key:
        raise AppKeyException("Bithumb access_key/secret_key가 존재하지 않습니다.")

    payload = {
        "access_key": access_key,
        "nonce": str(uuid.uuid4()),
        "timestamp": round(time.time() * 1000),
    }

    if raw_query_string is not None:
        payload["query_hash"] = hashlib.sha512(raw_query_string.encode()).hexdigest()
        payload["query_hash_alg"] = "SHA512"
    elif query_params:
        query_string = urlencode(query_params, doseq=True).encode()
        payload["query_hash"] = hashlib.sha512(query_string).hexdigest()
        payload["query_hash_alg"] = "SHA512"

    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return f"Bearer {token}"
