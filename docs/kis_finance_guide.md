# 한국투자증권(KIS) Finance 가이드

`programgarden_finance.kis` 패키지는 한국투자증권 **KIS Developers OpenAPI**(REST + WebSocket)를
파이썬 DSL로 래핑합니다. LS증권·빗썸과 동일한 TR 클래스 패턴을 따르며,
실전투자와 모의투자를 플래그 하나로 전환할 수 있습니다.

---

## 1. 준비

1. [KIS Developers](https://apiportal.koreainvestment.com)에서 앱 등록 → `appkey` / `appsecret` 발급
2. 모의투자를 쓰려면 KIS Developers에서 **모의투자 신청** 후 모의투자용 appkey를 별도로 발급
3. 계좌번호는 앞 8자리(CANO)와 뒤 2자리(계좌상품코드, 보통 `01`)로 나뉩니다

```bash
pip install programgarden-finance  # pycryptodome 포함 (체결통보 AES 복호화)
```

---

## 2. 클라이언트 생성과 로그인

```python
from programgarden_finance import Kis

kis = Kis(paper_trading=True)   # True: 모의투자 서버, False: 실전
kis.login(
    appkey="...",
    appsecretkey="...",
    account_no="12345678",       # CANO 앞 8자리
    account_product_code="01",   # 뒤 2자리
)
```

### 토큰 관리 (중요)

- KIS 접근토큰은 **24시간 유효**하지만 **재발급이 약 1분당 1회로 제한**됩니다.
- SDK는 토큰을 `~/.programgarden/kis_token_<hash>_<mode>.json` 파일에 캐시해
  프로세스를 재시작해도 재발급 없이 재사용합니다 (appkey/appsecret은 저장하지 않음).
- 토큰은 **첫 TR 요청 시 지연 발급**됩니다. 즉시 발급하려면 `login(..., issue_token=True)`.
- 토큰 만료 응답(`EGW00123` 등)을 받으면 자동으로 1회 재발급 후 재시도합니다.
- 파일 캐시를 끄려면 `Kis(use_token_file_cache=False)`.

---

## 3. TR 목록

| 분류 | 메서드 (한국어 별칭) | TR ID (실전/모의) | 설명 |
|------|---------------------|-------------------|------|
| 시세 | `quotations().inquire_price` (`현재가`) | FHKST01010100 | 주식현재가 시세 |
| 시세 | `quotations().inquire_asking_price` (`호가`) | FHKST01010200 | 호가/예상체결 |
| 시세 | `quotations().inquire_daily_itemchartprice` (`일봉`) | FHKST03010100 | 기간별 시세 (일/주/월/년) |
| 계좌 | `accno().inquire_balance` (`잔고`) | TTTC8434R / VTTC8434R | 주식잔고조회 (연속조회 지원) |
| 계좌 | `accno().inquire_psbl_order` (`주문가능`) | TTTC8908R / VTTC8908R | 매수가능조회 |
| 주문 | `order().order_cash_buy` (`현금매수`) | TTTC0802U / VTTC0802U | 주식주문(현금) 매수 |
| 주문 | `order().order_cash_sell` (`현금매도`) | TTTC0801U / VTTC0801U | 주식주문(현금) 매도 |
| 주문 | `order().order_rvsecncl` (`정정취소`) | TTTC0803U / VTTC0803U | 주식주문(정정취소) — RVSE_CNCL_DVSN_CD로 정정(01)/취소(02) 구분 |

주문·계좌 TR ID는 `paper_trading` 플래그에 따라 **자동으로 실전/모의가 분기**됩니다.
TR ID 상수는 `programgarden_finance.kis.config.TR_IDS`에 중앙화되어 있습니다.

### 연속조회 (tr_cont, v1.12.0+)

보유 종목이 한 페이지(약 50건)를 넘으면 KIS가 응답 헤더 `tr_cont`에 `F`/`M`(다음
페이지 있음)을 반환합니다. `inquire_balance()`는 이를 자동 처리하는 헬퍼를 제공합니다:

```python
resp = kis.accno().inquire_balance().req_all(max_pages=10)  # 전체 페이지 자동 수집·병합
# 비동기: await kis.accno().inquire_balance().req_all_async()
```

단일 페이지만 필요하면 기존처럼 `.req()`를 그대로 사용하세요.

### hashkey (POST 본문 위변조 방지, v1.12.0+)

주문 등 POST TR에 KIS 권장 위변조 방지 헤더를 자동 첨부하려면 클라이언트 생성 시
`use_hashkey=True`를 설정합니다. `/uapi/hashkey`로 별도 요청 1회가 추가되며,
발급 실패 시에도 원 요청은 해시 없이 정상 진행됩니다(경고 로그만 남김).

```python
kis = Kis(paper_trading=True, use_hashkey=True)
```

---

## 4. 사용 예

### 현재가

```python
from programgarden_finance import kis_inquire_price

resp = kis.시세().현재가(
    kis_inquire_price.InquirePriceInBlock(fid_input_iscd="005930")
).req()
print(resp.block.stck_prpr)   # 현재가
```

### 잔고 (계좌번호 자동 채움)

```python
resp = kis.계좌().잔고().req()          # 로그인 시 등록한 계좌 사용
print(resp.block2.dnca_tot_amt)         # 예수금
for p in resp.blocks:                   # 보유 종목
    print(p.pdno, p.hldg_qty, p.evlu_pfls_amt)
```

### 주문 → 정정 → 취소

```python
from programgarden_finance import kis_order_cash, kis_order_rvsecncl

buy = kis.주문().현금매수(
    kis_order_cash.OrderCashBodyBlock(
        cano="", pdno="005930", ord_dvsn="00",  # 00 지정가, 01 시장가
        ord_qty="10", ord_unpr="60000",
    )
).req()
order_no = buy.block.odno

# 정정 (RVSE_CNCL_DVSN_CD=01) — 취소와 같은 TR, 구분코드만 다름
modify = kis.주문().정정취소(
    kis_order_rvsecncl.OrderRvsecnclBodyBlock(
        cano="", orgn_odno=order_no,
        rvse_cncl_dvsn_cd="01",   # 01 정정
        ord_dvsn="00", ord_unpr="61000", ord_qty="5",
        qty_all_ord_yn="N",
    )
).req()

# 취소 (RVSE_CNCL_DVSN_CD=02)
cancel = kis.주문().정정취소(
    kis_order_rvsecncl.OrderRvsecnclBodyBlock(
        cano="", orgn_odno=order_no,
        rvse_cncl_dvsn_cd="02",   # 02 취소
        qty_all_ord_yn="Y",       # 잔량 전부
    )
).req()
```

응답 공통 필드: `rt_cd`("0"=성공), `msg_cd`, `msg1`, `error_msg`(성공 시 None).
비동기는 `req()` 대신 `await ....req_async()`.

---

## 5. 실시간 WebSocket

```python
real = kis.실시간()
await real.connect()          # approval_key 자동 발급

# 실시간 체결가 (H0STCNT0)
ccnl = real.체결가()
ccnl.체결가수신(lambda r: print(r.mksc_shrn_iscd, r.stck_prpr))
ccnl.체결가등록(["005930", "000660"])

# 실시간 호가 (H0STASP0, v1.12.0+)
asking = real.호가()
asking.호가수신(lambda r: print(r.askp1, r.bidp1, r.total_askp_rsqn))
asking.호가등록(["005930"])

# 실시간 체결통보 (H0STCNI0 실전 / H0STCNI9 모의 — 자동 선택)
notice = real.체결통보()
notice.체결통보수신(lambda r: print(r.oder_no, r.cntg_yn))
notice.subscribe("나의HTS아이디")   # tr_key는 종목코드가 아닌 HTS ID
```

프로토콜 특성 (SDK가 자동 처리):

- 데이터는 JSON이 아닌 **파이프 구분 텍스트** (`암호화플래그|tr_id|건수|필드^필드^…`)
- **체결통보는 AES-256-CBC 암호화** — 구독 응답의 key/iv로 복호화 (pycryptodome)
- 서버의 `PINGPONG` 프레임을 그대로 에코해야 연결 유지
- 재연결 시 이전 구독 자동 복원, key/iv 수신 전 도착한 암호 프레임은 버퍼링

---

## 6. 워크플로우 노드

| 노드 | 역할 |
|------|------|
| `KisBrokerNode` | 인증 게이트웨이. `credential_id`(broker_kis) + `paper_trading` |
| `KisAccountNode` | 잔고·예수금 조회 → balance/positions/held_symbols |
| `KisOrderableAmountNode` | 매수가능조회 → orderable {orderable_cash, max_buy_quantity, nrcvb_buy_quantity, ...} (v1.19.0+) |
| `KisMarketDataNode` | 현재가 조회 (`symbols` 콤마 구분) |
| `KisHistoricalDataNode` | 일봉 조회 → `time_series` 포트가 ConditionNode 직결 |
| `KisNewOrderNode` | 현금 매수/매도 (buy/sell × limit/market) |
| `KisModifyOrderNode` | 주문 정정 — 가격·수량 변경 (v1.19.0+) |
| `KisCancelOrderNode` | 주문 취소 (전량/일부) |

credential 타입 `broker_kis`: `appkey`, `appsecret`, `account_no`, `account_product_code`.

**멀티브로커**: 같은 국내주식 스코프의 LS `KoreaStockBrokerNode`와 한 워크플로우에
공존합니다. 각 노드는 자기 프로바이더의 브로커에 자동 바인딩됩니다.

워크플로우 예제: `90-kis-account`, `91-kis-market-data`, `92-kis-rsi-bot`.
SDK 예제 스크립트: `src/finance/example/kis/`.

---

## 7. Rate-limit

| 모드 | 제한 | SDK 기본값 |
|------|------|-----------|
| 실전 | 초당 20건 | `rate_limit_count=20, seconds=1` |
| 모의 | 초당 2건 | `rate_limit_count=2, seconds=1` |

같은 appkey의 모든 TR이 rate-limit 버킷을 공유하며(`rate_limit_key="kis:<appkey>"`),
초과 시 기본 동작은 대기(`on_rate_limit="wait"`)입니다.

---

## 8. Token-provider 모드 (LS식 consumer, v1.12.0+)

여러 프로세스가 하나의 KIS 앱키를 공유할 때, 토큰 발급을 중앙 서버가 전담하고
각 프로세스는 발급된 토큰을 소비만 하도록 구성할 수 있습니다 (KIS 재발급이
분당 1회로 제한되므로 다중 프로세스가 각자 발급을 시도하면 충돌합니다).

```python
def fetch_token_from_central_server():
    # 중앙 서버에서 (access_token, expires_at_epoch_seconds) 조회
    return access_token, expires_at

kis = Kis(paper_trading=True, token_provider=fetch_token_from_central_server)
# 또는 비동기: Kis(async_token_provider=async_fetch_token)
```

- `token_provider` 설정 시 파일 캐시는 자동 비활성화되고, 클라이언트는 절대
  자체 발급(`/oauth2/tokenP`)을 호출하지 않습니다.
- appkey/appsecret은 여전히 모든 TR 헤더에 필요합니다 (KIS는 LS와 달리 토큰
  발급뿐 아니라 모든 요청에 appkey/appsecret 헤더를 요구하기 때문) — provider는
  **토큰 발급만** 위임합니다.

---

## 9. 보안 주의사항

- appkey/appsecret은 환경변수(.env)로 관리하고 코드·로그에 노출하지 마세요
- 토큰 캐시 파일에는 토큰만 저장되며(키 미저장) 사용자 전용 권한(0600)으로 생성됩니다
- 실전 주문 전 반드시 모의투자(`paper_trading=True`)와 `validate_deep()`으로 검증하세요
- 종목코드는 SDK/executor에서 `^[0-9A-Z]{6}$` 패턴으로 검증됩니다 (injection 방지)
