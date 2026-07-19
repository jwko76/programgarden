# 키움증권(Kiwoom) Finance 가이드

`programgarden_finance.kiwoom` 패키지는 **키움증권 OpenAPI**(REST + WebSocket)를
파이썬 DSL로 래핑합니다. LS증권·빗썸·KIS와 동일한 TR 클래스 패턴을 따르며,
실전투자와 모의투자를 플래그 하나로 전환할 수 있습니다.

> **검증 현황 (2026-07-18, 모의서버 라이브)**: 토큰 발급·현재가(ka10001)·
> 호가(ka10004)·일봉(ka10081)·잔고(kt00018)·WebSocket LOGIN까지 라이브 확인
> 완료. 미검증: 주문 접수/체결(영업일 필요), 잔고 보유종목 항목 필드(보유
> 종목 필요), 주문가능(kt00010 — **모의서버 미지원**, RC7006), 장중 실시간
> 체결 데이터. 실전 서버는 앱의 **지정단말기 인증**(오류 8050) 해제/등록
> 전까지 토큰 발급이 거부됩니다. 남은 미확인 항목은 소스의
> `TODO(실계좌 검증)` 주석 참조.

---

## 1. 준비

1. [키움 OpenAPI](https://openapi.kiwoom.com)에서 앱 등록 → `appkey` / `secretkey` 발급
2. 모의투자를 쓰려면 키움 OpenAPI에서 **모의투자 신청**
3. 계좌번호는 단일 필드(`account_no`)로 사용합니다 (KIS의 CANO+상품코드 2단 구조와 다름)

```bash
pip install programgarden-finance
```

---

## 2. 클라이언트 생성과 로그인

```python
from programgarden_finance import Kiwoom

kiwoom = Kiwoom(paper_trading=True)   # True: 모의투자 서버, False: 실전
kiwoom.login(
    appkey="...",
    appsecretkey="...",
    account_no="12345678",
)
```

### KIS와의 핵심 차이

| 항목 | KIS | 키움 |
|------|-----|------|
| 실전/모의 전환 | tr_id 분기 (TTTC↔VTTC) | **접속 도메인 전환** (`api.kiwoom.com` ↔ `mockapi.kiwoom.com`) |
| TR ID | `tr_id` 헤더, 실전/모의 상이 | `api-id` 헤더, 실전/모의 공용 |
| HTTP 방식 | 조회 GET / 주문 POST | **모든 TR이 POST** (단일 JSON 바디) |
| 응답 봉투 | `rt_cd`/`msg_cd`/`msg1` + output/output1/output2 | `return_code`(0=성공)/`return_msg`, 별도 데이터 봉투 없음 |
| 토큰 발급 필드 | `appsecret` | `secretkey` |
| 계좌 구조 | CANO(8) + 상품코드(2) | 단일 `acnt_no` |

### 토큰 관리

- 토큰은 `~/.programgarden/kiwoom_token_<hash>_<mode>.json` 파일에 캐시됩니다
  (appkey/secretkey는 저장하지 않음).
- **첫 TR 요청 시 지연 발급**. 즉시 발급은 `login(..., issue_token=True)`.
- 만료 응답(HTTP 401) 수신 시 자동으로 1회 재발급 후 재시도합니다.
- 파일 캐시를 끄려면 `Kiwoom(use_token_file_cache=False)`.

---

## 3. TR 목록 (MVP)

| 분류 | 메서드 (한국어 별칭) | api-id | 설명 |
|------|---------------------|--------|------|
| 시세 | `quotations().inquire_price` (`현재가`) | ka10001 | 종목기본정보 (현재가 포함) |
| 시세 | `quotations().inquire_asking_price` (`호가`) | ka10004 | 주식호가 |
| 시세 | `quotations().inquire_daily_itemchartprice` (`일봉`) | ka10081 | 주식일봉차트 |
| 계좌 | `accno().inquire_balance` (`잔고`) | kt00018 | 계좌평가잔고내역 |
| 계좌 | `accno().inquire_psbl_order` (`주문가능`) | kt00010 | 주문인출가능금액 |
| 주문 | `order().order_cash_buy` (`현금매수`) | kt10000 | 주식 현금 매수 |
| 주문 | `order().order_cash_sell` (`현금매도`) | kt10001 | 주식 현금 매도 |
| 주문 | `order().order_modify` (`정정`) | kt10002 | 주식 정정 |
| 주문 | `order().order_cancel` (`취소`) | kt10003 | 주식 취소 |

KIS와 달리 **정정/취소가 별개 api-id**라 SDK도 `order_modify`/`order_cancel`
두 메서드로 분리되어 있습니다. api-id 상수는
`programgarden_finance.kiwoom.config.TR_IDS`에 중앙화되어 있습니다.

---

## 4. 사용 예

### 현재가

```python
from programgarden_finance import kiwoom_inquire_price

resp = kiwoom.시세().현재가(
    kiwoom_inquire_price.InquirePriceInBlock(stk_cd="005930")
).req()
print(resp.block.cur_prc)   # 현재가
```

### 잔고 (계좌번호 자동 채움)

```python
resp = kiwoom.계좌().잔고().req()      # 로그인 시 등록한 계좌 사용
print(resp.block.prsm_dpst_aset_amt)   # 추정예탁자산 (예수금 전용 필드는 kt00018에 없음)
for p in resp.blocks:                  # 보유 종목 (acnt_evlt_remn_indv_tot)
    print(p.stk_cd, p.rmnd_qty, p.evltv_prft)
```

숫자 필드는 `"000000010000000"` 같은 zero-padded 문자열로 오며, 현재가/호가
가격에는 등락 부호(+/-)가 붙습니다 (`float()` 변환은 그대로 동작).

### 주문 → 취소

```python
from programgarden_finance import kiwoom_order_cash, kiwoom_order_rvsecncl

buy = kiwoom.주문().현금매수(
    kiwoom_order_cash.OrderCashBodyBlock(
        acnt_no="", stk_cd="005930",
        ord_qty="10", ord_uv="60000",
        trde_tp="0",  # 지정가로 추정 (TODO(실계좌 검증))
    )
).req()
order_no = buy.block.ord_no

cancel = kiwoom.주문().취소(
    kiwoom_order_rvsecncl.OrderRvsecnclBodyBlock(
        acnt_no="", orig_ord_no=order_no,
        stk_cd="005930",   # 키움 취소는 종목코드 필수 (KIS와 다름)
        ord_qty="0", ord_uv="0",
    )
).req()
```

응답 공통 필드: `return_code`(0=성공), `return_msg`, `error_msg`(성공 시 None).
비동기는 `req()` 대신 `await ....req_async()`.

---

## 5. 실시간 WebSocket

```python
real = kiwoom.실시간()
await real.connect()          # REST 접근토큰을 그대로 재사용 (KIS approval_key 없음)

# 실시간 주식체결 (type 0B)
ccnl = real.체결가()
ccnl.체결가수신(lambda r: print(r.item, r.cur_prc))
ccnl.체결가등록(["005930", "000660"])

# 실시간 주문체결통보 (type 00)
notice = real.체결통보()
notice.체결통보수신(lambda r: print(r))
```

프로토콜 특성 (KIS와의 차이):

- 메시지가 파이프 텍스트가 아닌 **JSON** — 필드명 기반 파싱
- 접속 인증에 REST 접근토큰을 그대로 사용 (approval_key 발급 절차 없음) —
  접속 후 `{"trnm": "LOGIN", "token": ...}` 전송, 응답 `return_code=0` 확인 (라이브 검증됨)
- 주소: 실전 `wss://api.kiwoom.com:10000/api/dostk/websocket` /
  모의 `wss://mockapi.kiwoom.com:10000/api/dostk/websocket` (모의 라이브 접속 확인)
- 체결통보 AES 암호화 없음(으로 추정) — 장중 데이터 수신은 미검증

---

## 6. 워크플로우 노드

| 노드 | 역할 |
|------|------|
| `KiwoomBrokerNode` | 인증 게이트웨이. `credential_id`(broker_kiwoom) + `paper_trading` |
| `KiwoomAccountNode` | 잔고·예수금 조회 → balance/positions/held_symbols |
| `KiwoomMarketDataNode` | 현재가 조회 (`symbols` 콤마 구분) |
| `KiwoomHistoricalDataNode` | 일봉 조회 → `time_series` 포트가 ConditionNode 직결 |
| `KiwoomNewOrderNode` | 현금 매수/매도 (buy/sell × limit/market) |
| `KiwoomCancelOrderNode` | 주문 취소 — **`symbol` 필드 필수** (키움 kt10003 특성) |

credential 타입 `broker_kiwoom`: `appkey`, `appsecret`, `account_no`.

**멀티브로커**: 같은 국내주식 스코프의 LS `KoreaStockBrokerNode`·KIS
`KisBrokerNode`와 한 워크플로우에 공존합니다. 각 노드는 자기 프로바이더의
브로커에 자동 바인딩됩니다 (`(product_scope, broker_provider)` 키).

워크플로우 예제: `93-kiwoom-account`, `94-kiwoom-market-data`, `95-kiwoom-rsi-bot`.
SDK 예제 스크립트: `src/finance/example/kiwoom/`.

---

## 7. Rate-limit

키움 공식 rate-limit 정책이 문서로 확인되지 않아, KIS 실전 기준(초당 20건)을
보수적으로 차용했습니다 (`SetupOptions.for_mode`). 같은 appkey의 모든 TR이
버킷을 공유하며(`rate_limit_key="kiwoom:<appkey>"`), 초과 시 기본 동작은
대기(`on_rate_limit="wait"`)입니다. TODO(실계좌 검증): 정확한 정책 확인 후 조정.

---

## 8. 보안 주의사항

- appkey/secretkey는 환경변수(.env)로 관리하고 코드·로그에 노출하지 마세요
- 토큰 캐시 파일에는 토큰만 저장되며(키 미저장) 사용자 전용 권한(0600)으로 생성됩니다
- 실전 주문 전 반드시 모의투자(`paper_trading=True`)와 `validate_deep()`으로 검증하세요
- 종목코드는 executor에서 `^[0-9A-Z]{6}$` 패턴으로 검증됩니다 (injection 방지)
