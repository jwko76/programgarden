# WORKLOG

작업 완료 시마다 Claude가 이 파일에 항목을 추가한다.
최신 항목이 맨 위에 온다.

---

## 2026-06-19 — 빗썸 전체 릴리즈 (v1.7.0 / v1.14.6 / v1.23.2)

**작업자**: Claude (jwko76 요청)
**커밋**: feat(bithumb): 빗썸 워크플로우 예제 3종 + 버전 범프 릴리즈

### 내용

**워크플로우 예제 3종 추가** (`src/programgarden/examples/workflows/`):
- `87-bithumb-account.json/.md` — 빗썸 계좌 잔고 조회 (BithumbBrokerNode → BithumbAccountNode → TableDisplayNode)
- `88-bithumb-market-data.json/.md` — 빗썸 현재가 조회 (BithumbMarketDataNode 단독, 인증 불필요)
- `89-bithumb-rsi-bot.json/.md` — RSI 과매도 BTC 자동매수 봇 (ScheduleNode + HTTPRequestNode + ConditionNode(RSI))

**버그 수정:**
- `bithumb_executors.py`: `BithumbAccountNodeExecutor`, `BithumbMarketDataNodeExecutor` dry_run 시 fixture 반환 (실제 API 미호출) — dry_run 테스트 호환성 확보
- `resolver.py`: `MISSING_REQUIRED_BROKER` 검증 로직에 COIN 스코프 → BithumbBrokerNode 매핑 추가, `_requires_broker=False` 플래그 지원
- `nodes/market_bithumb.py`: `BithumbMarketDataNode._requires_broker = False` 추가 (공개 API)
- `registry/node_registry.py`: 빗썸 노드 5종 `NodeTypeRegistry` 등록 누락 수정

**버전 범프:**
- finance: `v1.6.10` → `v1.7.0` (빗썸 실시간 WebSocket 추가 반영)
- core: `v1.14.5` → `v1.14.6` (빗썸 노드 5종 + 레지스트리 등록)
- programgarden: `v1.23.1` → `v1.23.2` (빗썸 executor + 예제 + resolver 수정)

**테스트:**
- `test_examples_validation.py`: 워크플로우 수 86→89, `KNOWN_MOCK_FRAGILE`에 89 추가
- 정적 검증 179 PASS, dry_run 87·88 PASS, 89 xfailed (예상)

---

## 2026-06-19 — 빗썸 워크플로우 노드 5종 구현 (미커밋)

**작업자**: Claude (jwko76 요청)
**커밋**: 없음 (커밋 대기)

### 내용

**core 패키지:**
- `nodes/base.py`: `ProductScope.COIN = "coin"`, `BrokerProvider.BITHUMB = "bithumb.com"` 추가
- `nodes/broker_bithumb.py`: `BithumbBrokerNode` (infra, credential 인증 게이트웨이)
- `nodes/account_bithumb.py`: `BithumbAccountNode` (REST 1회 계좌 조회)
- `nodes/market_bithumb.py`: `BithumbMarketDataNode` (공개 REST 현재가 조회)
- `nodes/order_bithumb.py`: `BithumbNewOrderNode`, `BithumbCancelOrderNode` (주문/취소)
- `nodes/__init__.py`: 5개 노드 export 추가
- `i18n/locales/ko.json` / `en.json`: 노드·필드·열거값 i18n 키 추가

**programgarden 패키지:**
- `bithumb_executors.py`: 5개 executor 신규 구현
  - `BithumbBrokerNodeExecutor` — credential inject → connection dict 출력
  - `BithumbAccountNodeExecutor` — GET /v1/accounts
  - `BithumbMarketDataNodeExecutor` — GET /v1/ticker
  - `BithumbNewOrderNodeExecutor` — POST /v2/orders (dry_run 지원)
  - `BithumbCancelOrderNodeExecutor` — DELETE /v2/order
  - 순환 참조 방지: `NodeExecutorBase` 대신 `_BithumbExecutorBase` 인라인 정의, `evaluate_all_bindings` lazy import
- `deep_fixtures.py`: `bithumb_account_fixture()`, `bithumb_market_data_fixture()`, `broker_connection_fixture` Bithumb 분기 추가
- `executor.py`: `_init_bithumb_executors()` lazy 등록 메서드 + `_init_executors()`에 `**self._init_bithumb_executors()` 추가

### 검증
- core 노드 import OK, ProductScope/BrokerProvider enum 확인
- executor 5개 WorkflowExecutor에 정상 등록 확인
- 기존 test_bithumb_real.py 47 PASS (회귀 없음)

---

## 2026-06-19 — Bithumb 실시간 WebSocket 구현 (미커밋)

**작업자**: Claude (jwko76 요청)
**커밋**: 없음 (커밋 대기)

### 내용
- **`bithumb/real_base.py`** — `BithumbRealBase`: 재연결·자동재구독·구독 cap·staleness 감지
  - LS `RealRequestAbstract`와 동일한 생명주기 (ref-count, exponential backoff)
  - LS와 달리 인증 불필요 (공개 WebSocket `wss://pubwss.bithumb.com/pub/ws`)
  - 구독 방식: 스트림 타입별 전체 코드 목록 재전송 (`{"type": "ticker", "codes": [...]}`)
  - `BithumbSubscriptionLimitExceeded` 예외 (기본 cap=15, <=0이면 무제한)
- **`bithumb/real/ticker/blocks.py`** — `TickerRealResponse` (실시간 현재가 push)
- **`bithumb/real/trade/blocks.py`** — `TradeRealResponse` (체결 틱 push)
- **`bithumb/real/orderbook/blocks.py`** — `OrderbookRealResponse` + `OrderbookRealUnit`
- **각 stream client** — `RealTicker`, `RealTrade`, `RealOrderbook` (add/remove/on_xxx)
- **`bithumb/real/__init__.py`** — `BithumbReal` + 한국어 별칭 (현재가/체결/호가)
- **`bithumb/client.py`** — `Bithumb.real()` 싱글톤 메서드, `_real_instances` 캐시
- **`bithumb/config.py`** — `WSS_URL` 상수 추가
- **`bithumb/__init__.py`** + **`programgarden_finance/__init__.py`** — real 심볼 export
- **`example/bithumb/run_real_ticker.py`** — 3개 스트림 동시 구독 예제
- **`tests/test_bithumb_real.py`** — 47개 테스트 47 PASS

### 테스트 결과
```
47 passed in 32.93s (Python 3.12, pytest 9.1.0)
```

---

## 2026-06-19 — CLAUDE.md / TODO.md / WORKLOG.md 초기 생성

**작업자**: Claude (jwko76 요청)
**커밋**: 없음 (문서 파일 신규)

### 내용
- `CLAUDE.md`: 프로젝트 개요, 현재 상태, 다음 작업 후보, 빠른 레퍼런스 정리
- `TODO.md`: 빗썸 실시간 WebSocket, 코인 워크플로우 노드, 문서 할 일 목록 작성
- `WORKLOG.md`: 이 파일 신규 생성 (이후 작업 기록용)

### 현재 상태 스냅샷
- `programgarden` v1.23.1 (main, clean)
- Bithumb REST 37개 엔드포인트 완성, 실시간 WebSocket 미구현
- 86개 워크플로우 예제 all deep-valid

---

## 2026-06-13 — Bithumb REST API 래퍼 완성 (224ba03)

**작업자**: Claude
**커밋**: `224ba03 feat(bithumb): add 20 remaining REST endpoints, deposit/withdrawal category, and docs`

### 내용
- Bithumb REST 엔드포인트 20개 추가 (기존 17 → 37개 전체)
- 카테고리 신설: `deposit_withdrawal/` (입출금 KRW·코인)
- 예제 스크립트: `run_deposit_withdrawal_actions.py`, `run_deposit_withdrawal_query.py`
- 테스트: `test_bithumb_deposit_withdrawal.py`

---

## 2026-06-13 — deep_validate 정적 바인딩 스캔 강화 (035e1f4)

**작업자**: Claude
**커밋**: `035e1f4 release: programgarden v1.23.1 + core v1.14.5`

### 내용
- `DisplayNode`·`TableDisplayNode`·`Fundamental`·`Backtest`·`Portfolio`·`LLM`·`AIAgent`·`SQLite` 등
  `evaluate_all_bindings` 를 호출하지 않는 노드도 `{{ }}` config 표현식 정적 스캔
- 반복 컨텍스트 가드(C1): `{{ item.* }}` / `{{ row.* }}` 는 false-reject 방지
- 86개 예제 회귀 0

---

## 2026-06-13 — deep workflow validation (6acb8ff)

**작업자**: Claude
**커밋**: `6acb8ff release: programgarden v1.23.0 + core v1.14.4`

### 내용
- `ProgramGarden.validate_deep()` — 가상 풀-실행(never-raise, 15초 타임박스)
- `deep_fixtures.py` — 스키마-shaped 기본 fixture 라이브러리
- 예제 8종 런타임 정합 재작성 (86/86 deep-valid)
- sync 래퍼가 호출자 이벤트루프 파괴하던 회귀 수정

---

## 2026-06-06 — LS token_provider opt-in (e9538ee)

**작업자**: Claude
**커밋**: `e9538ee release: v1.22.4`

### 내용
- `executor.set_ls_token_provider(provider)` — 서버 발급 토큰으로 브로커 로그인 라우팅
- finance `set_token_provider()` — sync/async provider 콜백 지원

---

## 2026-06-01 — HKEX 해외선물 예제 5종 (5032199)

**작업자**: Claude
**커밋**: `5072296 release: v1.22.3`

### 내용
- 예제 81: HMHM26/HMCEM26 다종목 RSI AND Bollinger 복합 진입
- 예제 82: 실시간 tick 손절 청산
- 예제 83: AI 리스크 리포트 (gpt-4o) + Telegram
- 예제 84: 백테스트 RSI/Bollinger 비교 + 아침 리포트
- 예제 85: 4월물 스크리너 → ATR breakout 진입
- LogicNode 다종목 auto-iterate AND 교집합 버그 수정
