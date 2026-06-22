# Programgarden Finance — 빗썸(Bithumb) API 가이드

Programgarden Finance는 [빗썸(Bithumb) OpenAPI v2.1.5](https://apidocs.bithumb.com/)를 Python
친화적으로 감싸 시세 조회, 자산/주문 관리, 입출금 관리를 손쉽게 자동화할 수 있게 돕는
모듈입니다. LS증권 모듈(`LS`)과 동일하게 카테고리 → TR(Pydantic 요청/응답 모델) 구조를 따르며,
모든 메서드는 한글 별칭(예: `현재가`, `주문하기`, `다건주문`)으로도 호출할 수 있습니다.

- 사용자 커뮤니티: https://cafe.naver.com/programgarden
- 카카오톡 오픈채팅: https://open.kakao.com/o/gKVObqUh
- 빗썸 공식 API 문서: https://apidocs.bithumb.com/reference

---

## 주요 특징

- **카테고리 기반 인터페이스**: `시세()`(공개) / `계좌()` / `주문()` / `입출금()`(비공개, 로그인 필요) 4개
  카테고리에 총 37개 엔드포인트를 제공합니다.
- **한글 별칭 지원**: 모든 메서드는 영문 메서드명(`ticker`, `order_new`)과 한글 별칭(`현재가`,
  `주문하기`)을 동시에 지원합니다.
- **비동기·동기 동시 지원**: 모든 TR은 동기(`req()`)와 비동기(`req_async()`) 호출을 모두
  제공합니다.
- **타입 안전성**: Pydantic 기반 요청/응답 모델(`XxxInBlock`/`XxxResponse`)로 타입 힌트와
  IDE 자동완성을 지원합니다.
- **요청 속도 제한 내장**: Private API는 기본적으로 `rate_limit_count=120`(초당 120회)으로
  제한되며 `SetupOptions`로 직접 조정할 수 있습니다.
- **풍부한 예제**: `src/finance/example/bithumb/` 폴더에 카테고리별 실행 스크립트가 포함되어
  있습니다.

---

## 요구 사항 및 설치

- Python 3.10 이상
- 빗썸 회원가입 및 [API 관리 페이지](https://www.bithumb.com)에서 발급한 Access Key/Secret Key

```bash
# PyPI 배포본 사용
pip install programgarden-finance

# Poetry 기반 개발 환경
poetry add programgarden-finance
```

---

## 사전 준비

- **API 키 발급**: 빗썸 로그인 후 `마이페이지 → Open API 관리`에서 Access Key/Secret Key를
  발급받습니다. 키 발급 시 사용할 권한(자산조회/주문조회/주문하기/입출금 등)을 범위에 맞게
  선택하세요.
- **IP 허용 목록 등록(중요)**: 빗썸 Private API는 API 키에 등록된 IP에서만 호출할 수
  있습니다. 등록되지 않은 IP로 호출하면 모든 비공개 엔드포인트가
  `NotAllowIP` 에러를 반환합니다 — 라이브 호출 전 API 키 설정에서 현재 서버의 공인 IP를
  허용 목록에 등록하세요.
- **시세(공개) API는 인증 불필요**: `시세()` 카테고리의 모든 메서드는 로그인 없이 호출할 수
  있습니다.
- **샘플 코드**: 카테고리별 예제는
  [GitHub 예제 디렉토리](https://github.com/programgarden/programgarden/tree/main/src/finance/example/bithumb)에서
  확인할 수 있습니다.

---

## 라이브러리 구조 한눈에 보기

```python
from programgarden_finance import Bithumb

bithumb = Bithumb()
bithumb.로그인(accesskey="발급받은 Access Key", secretkey="발급받은 Secret Key")

# 시세 (공개 API, 로그인 불필요)
market = bithumb.시세()
market.거래대상목록()      # 거래 가능한 마켓 목록
market.현재가(...)          # 현재가(스냅샷)
market.호가(...)            # 호가 정보
market.체결내역(...)        # 최근 체결 내역
market.분캔들(...)          # 분(分) 캔들
market.일캔들(...)          # 일(日) 캔들
market.주캔들(...)          # 주(週) 캔들
market.월캔들(...)          # 월(月) 캔들
market.입출금수수료조회(...)  # 화폐별 입출금 수수료

# 계좌 (비공개 API, 로그인 필요)
account = bithumb.계좌()
account.전체자산조회()       # 보유 자산 전체
account.입출금현황()         # 화폐별 입출금 가능 상태
account.입금리스트조회(...)  # 입금 내역
account.출금리스트조회(...)  # 출금 내역
account.API키리스트조회()    # 등록된 API 키 목록/만료일시

# 주문 (비공개 API, 로그인 필요)
order = bithumb.주문()
order.주문가능정보(...)      # 마켓별 주문 가능 정보
order.개별주문조회(...)      # 개별 주문 상세
order.주문리스트조회(...)    # 주문 목록
order.주문하기(...)          # 신규 주문 생성
order.주문취소(...)          # 주문 취소
order.다건주문(...)          # 다건 신규 주문 (최대 20건)
order.다건주문취소(...)      # 다건 주문 취소 (최대 30건)
order.TWAP주문(...)          # TWAP 주문 등록
order.TWAP주문취소(...)      # TWAP 주문 취소
order.TWAP주문조회(...)      # TWAP 주문 목록/상태 조회

# 입출금 관리 (비공개 API, 로그인 필요)
dw = bithumb.입출금()
dw.개별입금주소조회(...)         # 화폐별 입금 주소 조회
dw.전체입금주소조회()           # 전체 입금 주소 조회
dw.입금주소생성요청(...)         # 입금 주소 생성 요청
dw.원화입금리스트조회(...)       # 원화 입금 내역
dw.개별입금조회(...)             # 개별 입금 상세
dw.출금가능정보(...)             # 출금 가능 정보(수수료/한도)
dw.출금허용주소리스트조회()     # 출금 허용 주소 목록
dw.원화출금리스트조회(...)       # 원화 출금 내역
dw.개별출금조회(...)             # 개별 출금 상세

# ⚠️ 실자산 이동(고위험): 원화입금, 가상자산출금요청, 가상자산출금취소, 원화출금요청
# (자세한 내용은 아래 "주의사항" 참고)
```

- **인증**: `bithumb.로그인(accesskey=..., secretkey=...)`을 호출하면 이후 `계좌()`/`주문()`/
  `입출금()` 카테고리에서 자동으로 JWT 인증 헤더를 생성합니다. 로그인 없이 비공개 카테고리를
  호출하면 `LoginException`이 발생합니다.
- **요청 실행**: 모든 TR은 `.req()`(동기) 또는 `await .req_async()`(비동기)로 실행합니다.
  응답은 `error_msg`(성공 시 `None`), `error_name`, `status_code`, 그리고 `block`(단일 결과)
  또는 `blocks`(목록 결과) 필드를 가집니다.

---

## 빠른 시작 튜토리얼

### 1. 인증 설정

```python
import os
from dotenv import load_dotenv
from programgarden_finance import Bithumb

load_dotenv()

bithumb = Bithumb()
bithumb.로그인(
    accesskey=os.getenv("BITHUMB_ACCESS_KEY"),
    secretkey=os.getenv("BITHUMB_SECRET_KEY"),
)
```

### 2. 현재가 조회 (공개 API, 로그인 불필요)

```python
from programgarden_finance import Bithumb, bithumb_ticker

bithumb = Bithumb()

response = bithumb.시세().현재가(
    bithumb_ticker.TickerInBlock(markets="KRW-BTC,KRW-ETH")
).req()

for item in response.blocks or []:
    print(f"{item.market} 현재가: {item.trade_price:,.0f} ({item.signed_change_rate:+.2%})")
```

### 3. 보유 자산 조회

```python
response = bithumb.계좌().전체자산조회().req()

for item in response.blocks or []:
    print(f"{item.currency} | 보유: {item.balance} | 평단가: {item.avg_buy_price}")
```

### 4. 신규 주문 생성 및 취소

```python
from programgarden_finance import bithumb_order_new, bithumb_order_cancel

# 지정가 매수 주문
new_resp = bithumb.주문().주문하기(
    bithumb_order_new.OrderNewInBlock(
        market="KRW-BTC",
        side="bid",
        order_type="limit",
        price="80000000",
        volume="0.00008",
    )
).req()

order_id = new_resp.block.order_id

# 주문 취소
cancel_resp = bithumb.주문().주문취소(
    bithumb_order_cancel.OrderCancelInBlock(order_id=order_id)
).req()
```

### 5. 비동기 호출

```python
import asyncio
from programgarden_finance import bithumb_orderbook

async def fetch_orderbook():
    response = await bithumb.시세().호가(
        bithumb_orderbook.OrderbookInBlock(markets="KRW-BTC")
    ).req_async()
    return response.blocks

asyncio.run(fetch_orderbook())
```

---

## 활용 예시

### 다건 주문 생성 → 조회 → 다건 취소

```python
from programgarden_finance import (
    bithumb_order_new_batch,
    bithumb_order_cancel_batch,
)

# 1. 다건 매수 주문 생성 (최대 20건)
batch_resp = bithumb.주문().다건주문(
    bithumb_order_new_batch.OrderNewBatchInBlock(
        batch_orders=[
            bithumb_order_new_batch.BatchOrderItem(
                market="KRW-BTC", side="bid", order_type="limit",
                price="80000000", volume="0.00008",
            ),
            bithumb_order_new_batch.BatchOrderItem(
                market="KRW-BTC", side="bid", order_type="limit",
                price="75000000", volume="0.00008",
            ),
        ]
    )
).req()

order_ids = [
    item.order_id for item in batch_resp.block.batch_orders_response if item.order_id
]

# 2. 다건 주문 취소 (최대 30건, order_ids 또는 client_order_ids 중 하나 지정)
cancel_resp = bithumb.주문().다건주문취소(
    bithumb_order_cancel_batch.OrderCancelBatchInBlock(order_ids=order_ids)
).req()

for item in cancel_resp.block.success:
    print(f"취소됨: {item.order_id}")
for item in cancel_resp.block.fail:
    print(f"취소 실패: {item.order_id} - {item.error}")
```

전체 동작 예제는 [`run_order_batch.py`](https://github.com/programgarden/programgarden/blob/main/src/finance/example/bithumb/run_order_batch.py)를 참고하세요.

### TWAP(시간가중평균가격) 주문 등록 → 조회 → 취소

TWAP 주문은 등록 즉시 분할 체결이 시작되며 최소 300초(5분) 동안 진행됩니다.

```python
from programgarden_finance import bithumb_twap_new, bithumb_twap_cancel, bithumb_twap_list

# 1. TWAP 주문 등록 (bid는 price 필수, ask는 volume 필수)
new_resp = bithumb.주문().TWAP주문(
    bithumb_twap_new.TwapNewInBlock(
        market="KRW-BTC",
        side="bid",
        duration="300",    # 최소 300초(5분), 최대 43200초(12시간)
        frequency="60",    # 15/20/30/60/120 중 하나
        price="80000000",
    )
).req()

algo_order_id = new_resp.block.algo_order_id

# 2. TWAP 주문 목록/상태 조회 (읽기 전용)
list_resp = bithumb.주문().TWAP주문조회().req()
for o in list_resp.block.orders:
    print(f"{o.uuid} | {o.market} | {o.state} | 진행 {o.progress_count}/{o.total_order_count}")

# 3. TWAP 주문 취소
cancel_resp = bithumb.주문().TWAP주문취소(
    bithumb_twap_cancel.TwapCancelInBlock(algo_order_id=algo_order_id)
).req()
```

전체 동작 예제는 [`run_twap.py`](https://github.com/programgarden/programgarden/blob/main/src/finance/example/bithumb/run_twap.py)를 참고하세요.

### 입출금 정보 조회 (입금 주소, 입출금 내역, 출금 가능 정보)

```python
from programgarden_finance import (
    bithumb_deposit_address,
    bithumb_deposits_krw,
    bithumb_withdraws_chance,
    bithumb_withdraw_coin_addresses,
)

dw = bithumb.입출금()

# 화폐별 입금 주소 조회
addr_resp = dw.개별입금주소조회(
    bithumb_deposit_address.DepositAddressInBlock(currency="BTC", net_type="BTC")
).req()
print(addr_resp.block.deposit_address)

# 원화 입금 내역 조회 (최근 5건)
krw_resp = dw.원화입금리스트조회(
    bithumb_deposits_krw.DepositsKrwInBlock(limit=5)
).req()
for item in krw_resp.blocks or []:
    print(f"{item.state} | {item.amount}원 | {item.created_at}")

# 출금 가능 정보(수수료/한도) 조회
chance_resp = dw.출금가능정보(
    bithumb_withdraws_chance.WithdrawsChanceInBlock(currency="BTC", net_type="BTC")
).req()
print(chance_resp.block.currency.withdraw_fee)

# 출금 허용 주소 목록 조회
addrs_resp = dw.출금허용주소리스트조회().req()
for item in addrs_resp.blocks or []:
    print(f"{item.currency} ({item.network_name}) -> {item.withdraw_address}")
```

읽기 전용 입출금 조회 8종 전체 예제는
[`run_deposit_withdrawal_query.py`](https://github.com/programgarden/programgarden/blob/main/src/finance/example/bithumb/run_deposit_withdrawal_query.py)를
참고하세요.

### 입출금 수수료 비교

```python
from programgarden_finance import bithumb_fee_inout

# 로그인 불필요 (공개 API)
fee_resp = Bithumb().시세().입출금수수료조회(
    bithumb_fee_inout.FeeInoutInBlock(currency="BTC")
).req()

for item in fee_resp.blocks or []:
    for net in item.networks:
        print(f"{item.currency} ({net.net_name}) | 입금수수료: {net.deposit_fee_quantity} | 출금수수료: {net.withdraw_fee_quantity}")
```

### (참고) 고위험 입출금 액션 — 원화입금/원화출금/가상자산출금

`원화입금`, `원화출금요청`, `가상자산출금요청`, `가상자산출금취소`는 실제 자금/자산이
이동하는 고위험 엔드포인트입니다. 사용법은 다음과 같이 동일한 패턴을 따르지만, 실행 전
**반드시 "주의사항" 절을 먼저 읽으세요.**

```python
from programgarden_finance import bithumb_withdraw_coin

dw.가상자산출금요청(
    bithumb_withdraw_coin.WithdrawCoinInBlock(
        currency="BTC",
        net_type="BTC",
        amount="0.01",
        address="등록된 출금 주소",
    )
).req()
```

코드/모델/검증된 mock 테스트가 모두 포함된 실행 가능한 예제(기본적으로 비활성화)는
[`run_deposit_withdrawal_actions.py`](https://github.com/programgarden/programgarden/blob/main/src/finance/example/bithumb/run_deposit_withdrawal_actions.py)를
참고하세요.

---

## 요청 속도 직접 조절(Rate Limiting)

각 TR 요청에는 `SetupOptions`가 정의돼 있어 초당 호출 횟수 제한을 자동으로 준수합니다.
Private API(계좌/주문/입출금)는 기본값이 `rate_limit_count=120`(초당 120회)이고, 공개
시세 API는 `rate_limit_count=130`입니다. 필요 시 `options` 인자로 직접 조정할 수 있습니다.

```python
from programgarden_finance import SetupOptions, bithumb_ticker

options = SetupOptions(
    rate_limit_count=3,
    rate_limit_seconds=1,
    on_rate_limit="wait",
    rate_limit_key="ticker",
)

response = bithumb.시세().현재가(
    bithumb_ticker.TickerInBlock(markets="KRW-BTC"),
    options=options,
).req()
```

- `on_rate_limit="stop"`으로 설정하면 제한 초과 시 즉시 예외가 발생합니다.
- 여러 프로세스에서 같은 TR을 호출할 때 `rate_limit_key`를 공유하면 Redis 등 외부 저장소로
  속도 제한 상태를 공유할 수 있습니다.

---

## 메서드/엔드포인트 참조

### 시세 — `bithumb.시세()` (공개 API, 9개)

| 한글 별칭 | 영문 메서드 | HTTP / URL | 설명 |
|---|---|---|---|
| 거래대상목록 | `market_all` | `GET /v1/market/all` | 거래 가능한 마켓 목록 |
| 현재가 | `ticker` | `GET /v1/ticker` | 마켓 현재가(스냅샷) |
| 호가 | `orderbook` | `GET /v1/orderbook` | 마켓 호가 정보 |
| 체결내역 | `trades_ticks` | `GET /v1/trades/ticks` | 최근 체결 내역 |
| 분캔들 | `candles_minutes` | `GET /v1/candles/minutes/{unit}` | 분(分) 캔들 (1/3/5/10/15/30/60/240) |
| 일캔들 | `candles_days` | `GET /v1/candles/days` | 일(日) 캔들 |
| 주캔들 | `candles_weeks` | `GET /v1/candles/weeks` | 주(週) 캔들 |
| 월캔들 | `candles_months` | `GET /v1/candles/months` | 월(月) 캔들 |
| 입출금수수료조회 | `fee_inout` | `GET /v2/fee/inout/{currency}` | 화폐별 입출금 수수료 *(신규)* |

### 계좌 — `bithumb.계좌()` (비공개 API, 5개)

| 한글 별칭 | 영문 메서드 | HTTP / URL | 설명 |
|---|---|---|---|
| 전체자산조회 | `accounts` | `GET /v1/accounts` | 보유 자산 전체 조회 |
| 입출금현황 | `wallet_status` | `GET /v1/status/wallet` | 화폐별 입출금 가능 상태 |
| 입금리스트조회 | `deposits` | `GET /v1/deposits` | 입금 내역 조회 |
| 출금리스트조회 | `withdraws` | `GET /v1/withdraws` | 출금 내역 조회 |
| API키리스트조회 | `api_keys` | `GET /v1/api_keys` | 등록된 API 키 목록/만료일시 *(신규)* |

### 주문 — `bithumb.주문()` (비공개 API, 10개)

| 한글 별칭 | 영문 메서드 | HTTP / URL | 설명 |
|---|---|---|---|
| 주문가능정보 | `orders_chance` | `GET /v1/orders/chance` | 마켓별 주문 가능 정보(수수료/제약/자산) |
| 개별주문조회 | `order_detail` | `GET /v1/order` | uuid/client_order_id로 개별 주문 상세 |
| 주문리스트조회 | `orders` | `GET /v1/orders` | 주문 목록 조회 |
| 주문하기 | `order_new` | `POST /v2/orders` | 신규 주문(매수/매도) 생성 |
| 주문취소 | `order_cancel` | `DELETE /v2/order` | 주문 취소 |
| 다건주문 | `order_new_batch` | `POST /v2/orders/batch` | 다건 신규 주문 (최대 20건) *(신규)* |
| 다건주문취소 | `order_cancel_batch` | `POST /v2/orders/cancel` | 다건 주문 취소 (최대 30건) *(신규)* |
| TWAP주문 | `twap_new` | `POST /v1/twap` | TWAP(시간가중평균가격) 주문 등록 *(신규)* |
| TWAP주문취소 | `twap_cancel` | `DELETE /v1/twap` | TWAP 주문 취소 *(신규)* |
| TWAP주문조회 | `twap_list` | `GET /v1/twap` | TWAP 주문 목록/상태 조회 *(신규)* |

### 입출금 관리 — `bithumb.입출금()` (비공개 API, 13개, 전체 신규)

| 한글 별칭 | 영문 메서드 | HTTP / URL | 설명 |
|---|---|---|---|
| 입금주소생성요청 | `deposit_address_generate` | `POST /v1/deposits/generate_coin_address` | 입금 주소 생성 요청 |
| 개별입금주소조회 | `deposit_address` | `GET /v1/deposits/coin_address` | 화폐/네트워크별 입금 주소 조회 |
| 전체입금주소조회 | `deposit_addresses` | `GET /v1/deposits/coin_addresses` | 전체 입금 주소 목록 조회 |
| 원화입금 | `deposit_krw` | `POST /v1/deposits/krw` | 원화 입금 요청 ⚠️ 고위험(카카오 2FA) |
| 원화입금리스트조회 | `deposits_krw` | `GET /v1/deposits/krw` | 원화 입금 내역 조회 |
| 개별입금조회 | `deposit_detail` | `GET /v1/deposit` | uuid/txid로 개별 입금 상세 조회 |
| 가상자산출금요청 | `withdraw_coin` | `POST /v1/withdraws/coin` | 가상자산 출금 요청 ⚠️ 고위험(실자산 이동) |
| 가상자산출금취소 | `withdraw_coin_cancel` | `DELETE /v1/withdraws/coin` | 진행 중인 가상자산 출금 취소 ⚠️ 고위험 |
| 원화출금요청 | `withdraw_krw` | `POST /v1/withdraws/krw` | 원화 출금 요청 ⚠️ 고위험(카카오 2FA) |
| 원화출금리스트조회 | `withdraws_krw` | `GET /v1/withdraws/krw` | 원화 출금 내역 조회 |
| 개별출금조회 | `withdraw_detail` | `GET /v1/withdraw` | uuid/txid로 개별 출금 상세 조회 |
| 출금가능정보 | `withdraws_chance` | `GET /v1/withdraws/chance` | 화폐별 출금 가능 정보(수수료/한도/회원등급) |
| 출금허용주소리스트조회 | `withdraw_coin_addresses` | `GET /v1/withdraws/coin_addresses` | 사전 등록된 출금 허용 주소 목록 |

---

## 주의사항

### `NotAllowIP` 에러

Private API(계좌/주문/입출금)는 빗썸 API 키 설정에 등록된 IP에서만 호출할 수 있습니다.
호출 환경(서버/PC)의 공인 IP가 API 키의 IP 허용 목록에 없으면 모든 비공개 엔드포인트가
`error_name="NotAllowIP"`를 반환합니다. 빗썸 `마이페이지 → Open API 관리`에서 현재 IP를
허용 목록에 추가한 뒤 다시 시도하세요.

### 고위험 입출금 엔드포인트 (실자산 이동)

다음 4개 엔드포인트는 **실제 원화/가상자산이 이동**하므로 신중하게 사용해야 합니다.

- **원화입금(`deposit_krw`)**, **원화출금요청(`withdraw_krw`)**: `two_factor_type="kakao"`
  필드가 필수이며, 빗썸 앱의 카카오 2FA 인증을 거쳐야 최종 처리됩니다. 이 인증 단계는
  자동화할 수 없으므로, 호출 후 빗썸 앱에서 인증을 완료해야 입출금이 실제로 진행됩니다.
- **가상자산출금요청(`withdraw_coin`)**: 사전에 빗썸에 등록된 출금 허용 주소
  (`출금허용주소리스트조회`로 확인 가능)로만 출금할 수 있으며, 요청 즉시 코인이 외부 주소로
  전송될 수 있습니다.
- **가상자산출금취소(`withdraw_coin_cancel`)**: 출금이 이미 블록체인에 전파된 이후에는
  취소가 불가능할 수 있습니다.

이 4개 엔드포인트는 모두 코드/모델/예제가 구현되어 있으며 mock 테스트로 검증되었지만,
**실거래 자동 실행은 의도적으로 수행하지 않습니다.** 실제로 사용하려면
[`run_deposit_withdrawal_actions.py`](https://github.com/programgarden/programgarden/blob/main/src/finance/example/bithumb/run_deposit_withdrawal_actions.py)의
`ALLOW_*` 플래그를 직접 `True`로 변경하고, 값(금액/주소/네트워크)을 충분히 검토한 뒤
실행하세요.

### TWAP 주문의 최소 실행 시간

`TWAP주문(twap_new)`은 `duration`(최소 300초/5분 ~ 최대 43200초/12시간) 동안 `frequency`
간격으로 분할 체결됩니다. 등록 즉시 실제 자금으로 체결이 시작되며 최소 5분간 진행되므로,
테스트 시에는 등록 직후 `TWAP주문취소`로 취소하더라도 일부 수량이 이미 체결될 수 있습니다.

### 다건주문 / TWAP 주문 시 자전거래 방지(STP)

`주문하기`/`다건주문`은 동일 회원의 반대 방향 주문과 매칭될 경우 자전거래 방지(STP) 정책에
따라 거부되거나 자동 취소될 수 있습니다 (`stp_type`, `cross_trading` 에러명 참고).

---

## 예제 파일 안내

`src/finance/example/bithumb/`에 카테고리별 실행 스크립트가 포함되어 있습니다.

| 파일 | 내용 |
|---|---|
| `run_market_data.py` | 시세 9종(거래대상목록/현재가/호가/체결내역/캔들 4종/입출금수수료) |
| `run_account.py` | 계좌 5종(전체자산/입출금현황/입금·출금리스트/API키리스트) |
| `run_order_lifecycle.py` | 단일 주문 생성 → 조회 → 취소 |
| `run_order_query.py` | 주문가능정보/개별주문조회/주문리스트조회 |
| `run_order_batch.py` | 다건주문 생성 → 조회 → 다건취소 (`ALLOW_REAL_ORDER` 가드) |
| `run_twap.py` | TWAP 주문 등록 → 조회 → 취소 (`ALLOW_REAL_ORDER` 가드) |
| `run_deposit_withdrawal_query.py` | 입출금 조회 8종 (입금/출금 주소·내역·가능정보, 읽기 전용) |
| `run_deposit_withdrawal_actions.py` | 입출금 액션 5종 (입금주소생성/원화입금/코인출금/코인출금취소/원화출금, `ALLOW_*` 가드, 기본 비활성) |

---

## Import 참조

`programgarden_finance` 패키지에서 다음과 같이 카테고리 클래스와 각 TR의 요청/응답 모델을
가져올 수 있습니다.

```python
from programgarden_finance import (
    Bithumb,
    SetupOptions,

    # 시세
    bithumb_market_all, bithumb_ticker, bithumb_orderbook, bithumb_trades_ticks,
    bithumb_candles_minutes, bithumb_candles_days, bithumb_candles_weeks,
    bithumb_candles_months, bithumb_fee_inout,

    # 계좌
    bithumb_accounts, bithumb_wallet_status, bithumb_deposits, bithumb_withdraws,
    bithumb_api_keys,

    # 주문
    bithumb_orders_chance, bithumb_order_detail, bithumb_orders,
    bithumb_order_new, bithumb_order_cancel,
    bithumb_order_new_batch, bithumb_order_cancel_batch,
    bithumb_twap_new, bithumb_twap_cancel, bithumb_twap_list,

    # 입출금 관리
    bithumb_deposit_address_generate, bithumb_deposit_address, bithumb_deposit_addresses,
    bithumb_deposit_krw, bithumb_deposits_krw, bithumb_deposit_detail,
    bithumb_withdraw_coin, bithumb_withdraw_coin_cancel, bithumb_withdraw_krw,
    bithumb_withdraws_krw, bithumb_withdraw_detail, bithumb_withdraws_chance,
    bithumb_withdraw_coin_addresses,
)
```

각 `bithumb_xxx` 모듈은 `XxxInBlock`(요청 파라미터/본문), `XxxRequest`, `TrXxx`,
`XxxResponse`(및 `XxxOutBlock`)를 노출합니다. 예: `bithumb_ticker.TickerInBlock`,
`bithumb_order_new.OrderNewInBlock`.

---

## 실시간 WebSocket API (BithumbReal)

빗썸 공개 WebSocket(`wss://pubwss.bithumb.com/pub/ws`)으로 실시간 데이터를 수신합니다.
**인증 불필요** — 공개 API입니다.

### 연결 및 구독

```python
from programgarden_finance import Bithumb

bithumb = Bithumb()
real = bithumb.real()          # 싱글톤 — 반복 호출해도 동일 인스턴스
await real.connect()

# 현재가 스트림
ticker = real.ticker()         # 한국어 별칭: real.현재가()
ticker.add_ticker_codes(["KRW-BTC", "KRW-ETH"])

def on_tick(msg):              # sync/async 콜백 모두 지원
    print(msg.code, msg.trade_price, msg.signed_change_rate)

ticker.on_ticker(on_tick)

# 체결 스트림
trade = real.trade()           # 별칭: real.체결()
trade.add_trade_codes(["KRW-BTC"])
trade.on_trade(lambda m: print(m.trade_price, m.trade_volume, m.ask_bid))

# 호가 스트림
orderbook = real.orderbook()   # 별칭: real.호가()
orderbook.add_orderbook_codes(["KRW-BTC"])
orderbook.on_orderbook(lambda m: print(m.orderbook_units[0].ask_price))

# 유지
try:
    while True:
        await asyncio.sleep(1)
finally:
    await real.close()
```

### TickerRealResponse 주요 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `code` | str | 마켓 코드 (KRW-BTC 등) |
| `trade_price` | float | 현재가 |
| `change` | str | RISE / EVEN / FALL |
| `signed_change_rate` | float | 변화율 (소수, 예: 0.025 = +2.5%) |
| `trade_volume` | float | 체결 수량 |
| `acc_trade_volume_24h` | float | 24시간 거래량 |

### 재연결 · 구독 상한

```python
real = bithumb.real(
    max_subscribe_codes=100,   # 종목 수 상한 (기본 100)
    reconnect_delay=5.0,        # 재연결 대기 (초)
    staleness_seconds=60,       # N초 이상 미수신 시 재연결
)
```

---

## BithumbHistoricalDataNode (워크플로우 노드)

`ProgramGarden` 워크플로우에서 일봉 캔들 데이터를 가져와 ConditionNode RSI/Bollinger에 바로 연결합니다.
**인증 불필요** (공개 API).

```json
{
  "id": "candles",
  "type": "BithumbHistoricalDataNode",
  "market": "KRW-BTC",
  "count": 30
}
```

**출력 포트**

| 포트 | 타입 | 설명 |
|------|------|------|
| `time_series` | symbol_series | `[{symbol, exchange, time_series:[...candles]}]` — ConditionNode 직결 포맷 |
| `values` | candle_data | 원본 캔들 배열 (최신→과거 순) |

**ConditionNode 연결 예시**

```json
"items": {
  "from": "{{ nodes.candles.time_series }}",
  "extract": {
    "symbol": "{{ item.symbol }}",
    "exchange": "{{ item.exchange }}",
    "date": "{{ row.candle_date_time_utc }}",
    "close": "{{ row.trade_price }}"
  }
}
```

→ 예제 89번(`89-bithumb-rsi-bot.json`)에서 완전한 RSI 자동매수 봇 구현 참조.

---

## 워크플로우 예제 (87-89)

| 예제 | 파일 | 설명 |
|------|------|------|
| 87 | `87-bithumb-account.json` | 빗썸 계좌 잔고 조회 (BithumbBrokerNode → Account → Display) |
| 88 | `88-bithumb-market-data.json` | 현재가 4종 (공개 API, BithumbBrokerNode 불필요) |
| 89 | `89-bithumb-rsi-bot.json` | RSI 과매도 BTC 자동매수 봇 (ScheduleNode + HistoricalNode + ConditionNode) |

---

*마지막 갱신: 2026-06-23*
