# WORKLOG

작업 완료 시마다 Claude가 이 파일에 항목을 추가한다.
최신 항목이 맨 위에 온다.

---

## 2026-06-23 — upstream merge v1.24.1 + 형상관리 재구성

**작업자**: Claude (jwko76 요청)
**커밋**: merge, fix, test, docs

### 내용

**형상관리 재구성**
- `upstream` = `programgarden/programgarden.git` (fetch only, pull 전용)
- `origin` = `jwko76/programgarden.git` (SSH push 전용)
- `jwko76/programgarden` GitHub 레포 신규 생성 + 전체 히스토리 push
- 릴리즈 태그 (v1.23.2/v1.23.3, core/finance 버전별) 로컬 생성

**upstream v1.24.1 merge → v1.25.0**
- deep type-aware validation Phase 1-3 (cross-port type check, R1~R4 semantic layer)
- order-error-mapping: 주문 거부 진단 + 빈주문 사유 구분
- TrailingStop v2.1.0: trail_percent 고정 % 모드 + HWM 자가 갱신
- 예제 86/86b (NASDAQ 추세매수 HWM trailing stop, 동전주 변종)
- schedule_tick 사이클 격리 버그픽스
- executor list-of-dict symbol 바인딩 버그픽스
- ai_agent_fixture in deep_fixtures.py
- t1511/t1633 OutBlock 필드 10.2 반영 (LS 공지)

**버전 결정 (충돌 해결)**
- core: 1.14.7(jwko) + 1.15.1(upstream) → **1.15.2**
- finance: **1.9.0** 유지 (upstream 1.6.11보다 TR 대폭 많음)
- programgarden: 1.23.3(jwko) + 1.24.1(upstream) → **1.25.0**

**테스트**
- programgarden: 308 passed, 3 xfailed (LONG_RUNNING/KNOWN_MOCK_FRAGILE 정리)
- MonitoringLSStock: 150 passed
- EC2 배포 완료: v1.9.0, LS WS + SC1 + H1_ + Coin 모두 정상

---

## 2026-06-21 — finance v1.8.0 릴리즈

**작업자**: Claude (jwko76 요청)
**커밋**: release: finance v1.8.0 — LS TR 63개 추가 + RES 기반 버그 수정

### 변경 내역 (v1.7.0 → v1.8.0)

**신규 TR 63개 (LS xingAPI RES 스펙 기반)**
- 업종 차트: t8408/t8409/t8429 (6/29 기존 t8417/18/19 대체)
- 국내 선물/옵션: t2210/t2301/t8402~t8406/t8427/t8434/t2541/t2545/t0441
- ELW: t1950~t1988 (15종)
- 주식 거래원: t1752/t1764/t1771
- 주식 투자정보: t3202/t3341/t3401/t3518/t3521/t8428
- 주식 종목검색: t1825/t1857
- 업종 시세: t1485/t1514/t8424/t8425
- 기타: t8410/t8411/t8412/t1411/t1921/t1926/t1902/t1906/t1489/t1492/t1615/t1716/t1717/t1533/t4203/t8417/t8418/t8419

**버그 수정**
- o3121 OutBlock `ticktype` 필드 누락 (2026.1.31 LS 공지)
- t8452/t8453 OutBlock `jiclosev` → `jiclose` (전일종가 오타)
- t1422 InBlock `jshex` 필드 누락
- t1617 InBlock `gubun4` 필드 누락

**config.py 신규 URL**
- KOREA_STOCK_EXCHANGE_URL / INVESTINFO_URL / ITEM_SEARCH_URL / ELW_URL
- DOMESTIC_FO_MARKET_URL / FO_INVESTOR_URL / FO_ACCNO_URL

---

## 2026-06-21 — 미구현 TR 60개 전체 추가 (RES 자동생성)

**작업자**: Claude (jwko76 요청)
**커밋**: feat(ls): 나머지 미구현 TR 60개 전체 추가 (RES 스펙 기반 자동생성)

### 내용

xingAPI RES 파일 329개 파싱 → 미구현 63개 중 60개 구현 (t8408/t8409/t8429는 이전 커밋)

신규 카테고리 8개 + 기존 카테고리 보완:
- `futureoption/market/`: 국내선물옵션 시세 9종
- `futureoption/investor/`: 국내선물 투자자 2종
- `futureoption/accno/`: 국내선물 계좌 1종
- `korea_stock/elw/`: ELW 15종
- `korea_stock/exchange/`: 거래원 3종
- `korea_stock/investinfo/`: 투자정보 6종
- `korea_stock/item_search/`: 종목검색 2종
- `korea_stock/indtp/`: 업종 시세 4종
- 기존 카테고리: chart/etc/etf/ranking/investor/frgr_itt/sector/indtp_chart 보완

config.py: 7개 URL 상수 추가 (EXCHANGE, INVESTINFO, ITEM_SEARCH, ELW, DOMESTIC_FO_*)

---

## 2026-06-21 — LS RES 파일 전수 비교 + TR 수정 (t8408/t8409/t8429 신규, 버그 4건)

**작업자**: Claude (jwko76 요청)
**커밋**: feat(ls): t8408/t8409/t8429 업종차트 신규 구현 + RES 기반 버그 4건 수정

### 내용

**RES 파일 전수 비교 (329개 파일, 129개 TR 파싱)**
- RES: XingAPI 스펙 파일, REST OpenAPI와 동일 OutBlock 필드
- 코드베이스 매칭 TR: 66개, 미구현: 63개

**신규 TR 3종 구현 (6/29 마감)**
- `t8408` — (API용)업종차트(틱/n틱): `/indtp/chart`, float 10.2
- `t8409` — (API용)업종차트(분): `/indtp/chart`, float 10.2
- `t8429` — (API용)업종차트(일/주/월): `/indtp/chart`, float 10.2
- `ls/korea_stock/indtp_chart/` 신규 패키지, config.py INDTP_CHART_URL 추가

**버그 수정 (RES 비교로 발견)**
- `t8452/t8453 OutBlock.jiclose`: `jiclosev` → `jiclose` (오타 수정, 이 필드 없으면 전일종가 소실)
- `t1422 InBlock.jshex`: 장외종목포함여부 필드 추가
- `t1617 InBlock.gubun4`: 구분4 필드 추가

---

## 2026-06-20 — LS TR 변경사항 전수 조사 + o3121 ticktype 수정

**작업자**: Claude (jwko76 요청)
**커밋**: fix(o3121): ticktype 필드 추가 (2026.1.31 LS 공지 반영)

### 내용

**공지사항 전수 조사 (43개):**
- LS OpenAPI 공지사항 REST API (`/api/forums/.../posts`) 직접 호출로 전체 파악
- Playwright 없이 curl + python으로 SPA 우회 성공

**발견된 주요 변경사항:**
- ✅ 이미 반영됨: t1702, CSPAQ12200/22200, t1636, t1482, t1511, t1633, t1901/03/04
- 🔴 즉시 수정 (이번 커밋): o3121 OutBlock `ticktype` 필드 추가 (2026.1.31 적용)
- 🔴 6/29 마감: t8408/t8409/t8429 (업종 차트 신규 TR) — 스펙 확인 후 구현 예정
- 🟡 신규 발견 미구현: [업종] 시세 일부(t1485 등), [주식] 투자정보/거래원/종목검색/ELW, ETF(t1902/t1906)

**o3121 수정 상세:**
- `ticktype` 필드 (`OptMinBaseOrcPrc` 뒤에 추가)
- ticktype='1': NQ 스타일 (≤5→0.05, ≤100→0.25, ≤500→0.50, >500→1.00)
- ticktype='2': ES 스타일 (≤5→0.05, ≤20→0.10, ≤100→0.25, >100→0.50)

---

## 2026-06-20 — 빗썸 문서·딥검증 테스트 보완

**작업자**: Claude (jwko76 요청)
**커밋**: docs(bithumb): 워크플로우 가이드 §14 + deep_validate 빗썸 테스트 5종

### 내용

**00-workflow-guide.md 업데이트:**
- §8 Product Scope 표: `BithumbBrokerNode` 행 추가 + `BithumbMarketDataNode` 공개 API 주석
- §9 Bithumb 노드 포트 레퍼런스 테이블 신규 추가 (9개 포트)
- §14 Bithumb Coin Trading 신규 섹션:
  - 14.1 인증 방식 (Access Key/Secret Key, JWT HS256)
  - 14.2 기본 노드 흐름
  - 14.3 BithumbMarketDataNode 공개 API
  - 14.4 BithumbNewOrderNode 주문 방식 (limit/price/market)
  - 14.5 실시간 WebSocket Python API
  - 14.6 예제 87-89 표

**test_deep_validate.py — 빗썸 테스트 5종 추가 (전부 PASS):**
- `test_bithumb_account_deep_validate_passes` — Broker→Account 플로우
- `test_bithumb_market_data_standalone_deep_validate` — MarketData 단독 (브로커 없음)
- `test_bithumb_order_deep_validate_no_real_api_call` — 주문 플로우 + API 미호출 검증
- `test_bithumb_account_fixture_shape` — 계좌 fixture 필드 검증
- `test_bithumb_market_data_fixture_shape` — 현재가 fixture 2마켓 검증

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
