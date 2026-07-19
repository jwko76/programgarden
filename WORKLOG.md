# WORKLOG

작업 완료 시마다 Claude가 이 파일에 항목을 추가한다.
최신 항목이 맨 위에 온다.

---

## 2026-07-19 — OCI 개발서버 프로비저닝 (infra/oci-dev, Terraform)

**작업자**: Claude (jwko76 요청 — 키움/빗썸 IP 화이트리스트가 OCI 운영서버 기준이라
로컬 검증 불가 → 고정 IP를 가진 OCI 개발서버 신설)

### 배경
- 키움 8050(지정단말기)·빗썸 "not allowed client IP"는 로컬 PC IP가 미등록이라 발생 —
  사용자가 등록한 IP는 MonitoringLSStock OCI 운영서버 공인 IP (해당 프로젝트 WORKLOG 7/18 확인)
- MonitoringLSStock docs/DEPLOYMENT.md의 OCI 구축 절차 참고, 단 콘솔 수동 대신 **Terraform**으로 코드화

### 프로비저닝 (oci-vm 스킬 + ~/.oci 기존 자격증명 재사용)
- 테넌시 현황 실측: 홈 리전 ap-osaka-1 단일 구독, 기존 A1.Flex 1/6(운영)+E2.1.Micro 1대
  → **Always Free A1 잔여 3 OCPU/18GB 확인**
- `infra/oci-dev/`: VCN/서브넷/IGW/보안목록 + **A1.Flex 2 OCPU/12GB, Ubuntu 24.04(aarch64, Python 3.12)**
  — Always Free 한도 내 ₩0. SSH ingress는 내 IP/32만 허용
- **Reserved(고정) IP** 부여 — 브로커 화이트리스트 등록용, 인스턴스 재생성에도 유지
  (Ubuntu 22.04→24.04 재생성으로 실증: IP 불변. 22.04는 Python 3.10이라 교체, 24.04 부트볼륨 50GB 필요로 -replace 사용)
- 서버 구성: 코드 rsync(.git/.env 제외) + .env scp 이식(chmod 600, 내용 미열람) +
  venv(core/finance editable + pytest 등)
- **검증**: 서버에서 키움 모의 시세 전체(현재가/호가/일봉 600건) 라이브 통과 — 환경 배선 확인
- 보안: tfvars/tfstate gitignore, OCID·IP는 로그 마스킹, 키 파일은 경로 참조만

### 남은 것 (사용자 액션)
개발서버 고정 IP를 키움 지정단말기·빗썸 허용 IP에 **추가** 등록 → 키움 실전/빗썸 검증 재개

---

## 2026-07-18 (2) — 키움 모의서버 1차 라이브 검증 + 응답 필드 교정 (feature/kiwoom-broker)

**작업자**: Claude (jwko76이 .env에 키움 app key 등록 — 키 값은 열람·표출하지 않고 검증만 수행)

### .env 키 구조
실전 `KIWOOM_APPKEY/APPSECRET/ACCOUNT_NO` + 모의 `KIWOOM_MOCK_*` 분리 구조로 등록됨 —
예제 공용 헬퍼 `example/kiwoom/_env.py` 신설, `KIWOOM_PAPER=1`(기본)이면 MOCK_* 키 자동 선택.

### 모의서버(mockapi.kiwoom.com) 검증 결과
- **토큰 발급 성공** (24h TTL, 파일캐시 복원 동작 확인)
- **현재가 ka10001**: 추정 필드 11개 전부 실제 응답과 일치. 가격 필드에 등락 부호(+/-)
  확인 → executor의 abs() 처리 적중. eps/roe/bps 등 재무 필드도 다수 수신
- **호가 ka10004**: 최우선호가 필드가 `sel_fpr_bid`/`buy_fpr_bid`(fpr=first price)로 확인
  → blocks 교정 (추정했던 `*_1th_pre_req_pric`은 없음). 2~10차는 `sel_2th_pre_bid` 형식
- **일봉 ka10081**: 리스트 키 `stk_dt_pole_chart_qry`로 확인 → 교정 (추정 `stk_dt_pole` ✗).
  캔들 내부 필드명은 전부 적중, 600건 수신, 일봉 가격에는 부호 없음
- **잔고 kt00018**: 리스트 키 `acnt_evlt_remn_indv_tot`, 요약에 예수금(entr) 없음 →
  `prsm_dpst_aset_amt`(추정예탁자산)로 교정, 손익률은 `tot_prft_rt`. 숫자는 zero-padded
  문자열("000000010000000") — _to_float 정상 처리. 보유종목 0건이라 항목 내부 필드는 미확인
- **주문가능 kt00010**: 모의서버 미지원 확인 (return_code=20, RC7006) — blocks 주석 반영
- **주문 kt10000**: 주말이라 RC4010(모의투자 영업일이 아닙니다) — 요청 형식은 서버가
  정상 해석, 접수 검증은 다음 영업일로 이월
- **WebSocket**: 주소를 실전/모의 분리 + `/api/dostk/websocket` 경로로 교정 후
  접속·LOGIN(return_code=0, REST 토큰 재사용)·REG 등록까지 성공. 데이터 프레임은 장중 확인 필요

### 실전 서버
토큰 발급이 `[8050:지정단말기 인증에 실패했습니다]`로 거부 — 코드가 아닌 계정 설정 이슈.
사용자가 키움 OpenAPI 사이트에서 지정단말기 등록(또는 인증 해제) 후 재시도 필요.

### 테스트
finance 키움 59건을 확정 필드명 기반 fixture로 갱신 후 전부 통과.
잔여 검증 항목은 TODO.md "보류 중" 갱신.

---

## 2026-07-18 — 키움증권 브로커 전체 연동 (feature/kiwoom-broker) — v1.11.0/v1.18.0/v1.28.0

**작업자**: Claude (jwko76 요청 — TODO.md "키움증권 브로커" 진행. KIS 패턴 복제)

### finance SDK `kiwoom/` (커밋 af78fd8)
TR 9종(현재가 ka10001 / 호가 ka10004 / 일봉 ka10081 / 잔고 kt00018 / 주문가능 kt00010 /
현금매수 kt10000 / 현금매도 kt10001 / 정정 kt10002 / 취소 kt10003) + 실시간 2종
(체결 0B / 주문체결통보 00), 단위테스트 59건. KIS와의 구조 차이를 반영:
실전/모의가 tr_id 분기가 아닌 **도메인 전환**(api ↔ mockapi.kiwoom.com), 모든 TR이
POST 단일 JSON 바디, 응답 봉투 return_code/return_msg, 토큰 발급 필드 secretkey.
공식 문서 미확인 필드는 `TODO(실계좌 검증)` 주석으로 표시.

### core 노드 6종 (커밋 9b84acc)
`Kiwoom{Broker,Account,MarketData,HistoricalData,NewOrder,CancelOrder}Node` +
`BrokerProvider.KIWOOM`, 레지스트리 등록, i18n(ko/en), AI 메타데이터
(_usage/_features/_anti_patterns/_examples/_node_guide) 완비, 노드 테스트 322줄.
멀티브로커 `(scope, provider)` 키로 LS·KIS와 국내주식 3사 공존.

### executor 레이어 + 예제 + 문서 (이번 커밋)
- `kiwoom_executors.py` 6종 (kis_executors 패턴) + executor.py `_init_kiwoom_executors` 등록
- deep_fixtures: `kiwoom_account/market_data/historical_fixture`(KIS shape 재사용) +
  `broker_connection_fixture` Kiwoom 분기 — deep_validate에서 클라이언트 생성 금지 보장
- **KiwoomCancelOrderNode에 `symbol` 필드 추가** — 키움 취소 api-id(kt10003)는 KIS와
  달리 종목코드(stk_cd) 필수인데 노드에 필드가 없던 불일치를 executor 구현 중 발견,
  field_schema/i18n/입력포트/예제 스니펫까지 반영
- finance `__init__.py`에 Kiwoom 최상위 export 추가 (`Kiwoom`, `kiwoom_*` 모듈 별칭,
  `KiwoomReal` 등 — KIS 이름과 충돌하는 실시간 클래스는 `Kiwoom*` prefix로 별칭)
- 워크플로우 예제 93-kiwoom-account / 94-kiwoom-market-data / 95-kiwoom-rsi-bot
  (+.md) — deep_validate 3건 모두 통과, examples_validation 9건 통과
- SDK 예제 `src/finance/example/kiwoom/` 4종 (quotations/balance/order_lifecycle/real_ccnl)
- `docs/kiwoom_finance_guide.md` 신규, 00-workflow-guide 키움 섹션(스코프 표·출력 포트·멀티브로커) 추가
- 테스트: deep_validate 키움 6건 신규 (fixture shape 3, no-real-api-call, 3사 멀티브로커,
  account deep) — 전체 test_deep_validate 73 passed, core 키움 895 passed(스키마 완전성 포함)
- 버전: finance 1.10.0→**1.11.0**, core 1.17.0→**1.18.0**, programgarden 1.27.0→**1.28.0**

### 남은 것 (블로킹: 사용자 키움 app key 발급 대기)
라이브 검증 전까지 `TODO(실계좌 검증)` 항목 유지 — 응답 필드명(잔고/현재가/일봉),
trde_tp 코드값(지정가 0/시장가 3 추정), 전량취소 규칙, WebSocket 주소/메시지 구조,
rate-limit 정책. 검증 시 blocks.py 필드명 교정만으로 대응 가능하도록 설계됨.

---

## 2026-07-13 — 조건 플러그인 크로스 트리거 확대 (Phase 0/1) + MACD·MA Cross·WilliamsR 버그 수정 (feature/signal-cross-trigger)

**작업자**: Claude (jwko76 요청 — TODO.md "조건 플러그인 크로스 트리거 확대" 진행)

### Phase 0 — 기존 크로스형 플러그인 8종 검증
aroon/coppock_curve/trix/vortex_indicator/parabolic_sar/squeeze_momentum은 정상
(직전 vs 현재 비교로 돌파 순간에만 통과). **MACD·MovingAverageCross는 버그** 발견:
`time_series`의 signal 마킹은 돌파 기준으로 맞게 구현했지만, 실제 통과 여부
(`passed_symbols`/`result`)는 `histogram>0`/`is_bullish` 같은 **레벨 체크**였음 —
이름은 "cross"인데 양수/불리시 구간 내내 반복 통과해 알림 중복을 그대로 유발하던
버그. 사용자 확인 후 기존 enum 값(`bullish_cross`/`golden` 등) 그대로 진짜 크로스로
수정 (MACD v3.1.0, MovingAverageCross v3.1.0). `prev_histogram`/`prev_short_ma`/
`prev_long_ma` 필드 추가, 신규 테스트 `test_macd_cross_trigger.py`/
`test_ma_cross_plugin.py` 각 4건.

### Phase 1 — 오실레이터 크로스 트리거 확대
RSI v3.1.0 패턴을 WilliamsR/CCI/MFI/ConnorsRSI/UltimateOscillator/ZScore/
MeanReversion 7종에 복제 (모두 v1.1.0) — `direction` enum에 `cross_oversold`/
`cross_overbought`(또는 `cross_below`/`cross_above`) 추가, `prev_*` 필드,
플러그인별 단위테스트 4건씩. Stochastic은 조사 결과 기존 `oversold`/`overbought`가
이미 %K/%D 교차 기준 엣지 트리거라 판명 — 코드 변경 없이 회귀 테스트만 추가
(`test_stochastic_cross_verification.py`).

부수 발견: **WilliamsR `overbought_threshold` 공식 버그** — `threshold+100`
(기본 -80 → +20, %R 범위 -100~0을 벗어나 도달 불가능)를 `-100-threshold`(→ -20)로
수정. 사용자 확인 후 함께 고침.

### 문서/버전
- community v1.14.0 → **v1.15.0**, CHANGELOG.md 갱신
- `docs/signal_dedup_migration_guide.md` §2/§7 갱신 — 지표별 크로스 enum 표,
  MACD/MA Cross 버그 수정으로 인한 알림 빈도 감소 경고 추가
- 전체 테스트: community 1159 passed (파일 파서 관련 기존 실패 108건은 무관 —
  openpyxl/pypdf/python-docx venv 미설치, 건드리지 않음)

---

## 2026-07-13 — KIS 실전 주문 라이브 검증 시도 → APBK0919로 블로킹

**작업자**: Claude (jwko76 요청 — TODO.md 예정 작업 진행)

### 내용
- `run_order_lifecycle_live.py` 실행 (WSL, `KIS_LIVE_ORDER_CONFIRM=YES`): 토큰 발급·현재가 조회(088350, 4,355원/하한가 3,255원) 정상
- 하한가 지정가 1주 매수 요청에서 KIS 서버가 `rt_cd=1, msg_cd=APBK0919, msg1="장운영일자가 주문일과 상이합니다"`로 거부 — 주문 미접수, 이후 취소 단계 미실행 (계좌에 실제로 걸린 주문 없음)
- 코드 점검(`tr_helpers.py`의 헤더 구성, `order/__init__.py`의 계좌번호 자동 채움) 상 이상 없음. 같은 계좌로 잔고·매수가능조회는 2026-07-11에 이미 성공한 이력
- 사용자 확인: 이 계좌로 HTS/MTS 수동 매매 경험 있음 → "API 최초 이용 계좌라 라우팅 미활성화" 가설 배제
- 웹 검색으로 `APBK0919` 자체 문서는 못 찾음. KIS는 app key 발급과 별개로 홈페이지/앱 [트레이딩]→[Open API]→[KIS Developers]에서 "오픈API 서비스 신청"(약관동의+계좌연결) 절차가 있다는 정보 확인 — 유력 후보로 사용자에게 확인 요청, 결과 대기 중 보류
- TODO.md "보류 중" 섹션에 재개 조건 기록. 실시간 체결가(`run_real_ccnl.py`)는 주문과 무관하니 별도 진행 가능

---

## 2026-07-12 — 시그널 알림 중복 방지: RSI 크로스 트리거 + Throttle 상한 확대 (feature/signal-cross-trigger)

**작업자**: Claude (jwko76 요청 — "텔레그램 포착 시그널이 너무 많아")

### 배경
조건 플러그인이 레벨 트리거(조건 유지 중 매 평가마다 시그널)뿐이고 ThrottleNode
상한이 300초라, 스케줄 폴링 + 텔레그램 조합에서 같은 알림이 반복 발생.

### 내용
- **RSI v3.1.0 크로스 트리거** (community v1.14.0): `direction`에 `cross_below`/`cross_above` 추가
  - 직전 캔들 RSI와 비교해 임계값 돌파 순간에만 1회 통과, `symbol_results.prev_rsi` 추가
  - time_series signal 마킹도 돌파 캔들 1개에만, 데이터 부족 시 크로스 불통과
  - `test_rsi_plugin.py` 신규 10건 (레벨 vs 크로스 대비 검증)
- **ThrottleNode v1.1.0** (core): `interval_sec` 상한 300 → 86,400초(24h)
  - pydantic Field + FieldSchema 양쪽, 기본값 5초 불변 (기존 워크플로우 무영향)
  - pitfalls에 "긴 Throttle은 새 이벤트도 차단 — 시그널 알림은 크로스 트리거 권장" 명시
  - `test_throttle_node.py` 신규 4건
- **00-workflow-guide.md §14.4.1**: 시그널 알림 중복 방지 권장 패턴 문서화

---

## 2026-07-12 — 빗썸 노드 AI 메타데이터 완비 + 분봉 지원 (feature/bithumb-node-polish)

**작업자**: Claude (jwko76 요청)

### 내용

**Task 1 — 빗썸 노드 6종 AI 메타데이터 보완 (기존 실패 6건 해소)**
- Broker/Account/MarketData/Historical/NewOrder/CancelOrder에 누락된 `_anti_patterns`/`_examples`/`_node_guide` 추가
  (CancelOrder는 `_features`도 누락이었음, 존재하지 않는 BithumbOpenOrdersNode 언급 제거)
- 예제 스니펫 12개 전부 `WorkflowExecutor.validate()` 통과 확인
- `test_node_schema_ai_fields` shape 테스트 6건 실패 → 0건, core 전체 1546 passed

**Task 2 — BithumbHistoricalDataNode 분봉/주봉/월봉 지원 (v1.1.0)**
- 노드: `interval` 필드 추가 (day/week/month/1m/3m/5m/10m/15m/30m/60m/240m, 기본 day) + ENUM FieldSchema
- executor: interval → SDK 분기 (candles_minutes(unit)/days/weeks/months), 허용 외 값은 day 폴백 + 경고
- finance SDK는 이미 4종 캔들 전부 래핑돼 있어 변경 없음
- i18n: **기존 누락이던 BithumbHistoricalDataNode 노드/필드 키 전체** + interval enum 라벨 11종 (ko/en)
- 라이브 검증: 엔진 전체 경로(ProgramGarden.run)로 5m/day/week/month 공개 API 실호출 확인

---

## 2026-07-11 — KIS 실전 API 검증 + 현재가 응답 필드 수정 (main)

**작업자**: Claude (jwko76 요청)

### 내용
- 사용자 발급 실전투자 app key(.env, git-ignored)로 첫 라이브 검증 수행
  - 토큰 발급 → 현재가(FHKST01010100)·호가(FHKST01010200)·일봉(FHKST03010100) 모두 정상 응답 확인
  - 예제 기본값이 모의투자(KIS_PAPER=1)라 실전 키용으로 `.env`에 `KIS_PAPER=0` 추가
- **버그 수정**: `InquirePriceOutBlock.hts_kor_isnm` — 실제 API 응답(80개 필드)에 없는 필드였음
  - `bstp_kor_isnm`(업종 한글 종목명)으로 교체 (실응답 존재 확인), 예제·테스트 갱신
  - 일봉 TR의 `hts_kor_isnm`은 실응답에 존재하므로 유지
- 보안: 키 값 미열람(변수명만 grep), `.env`는 `.gitignore` `.env*` 규칙으로 미추적 확인, 토큰 캐시는 `~/.programgarden/` chmod 600
- 테스트: KIS 관련 59개 전부 통과

### 남은 라이브 검증
- 잔고(TTTC8434R)·매수가능(TTTC8908R) 라이브 확인 완료 (보유종목 0, 현금만 보유 상태)
- 주문/실시간 예제는 미실행 (주문=실주문 발생, 실시간=주말 장 마감) — 거래일에 사용자 판단 하에 진행

---

## 2026-07-11 — 한국투자증권(KIS) 연동 + 멀티브로커 프레임워크 (feature/kis-broker)

**작업자**: Claude (jwko76 요청)
**커밋**: feat(resolver) → feat(core) → feat(kis) → feat(executor) → docs/release

### 내용

**Phase A — 엔진 멀티브로커 지원**
- `resolver.py` 브로커 중복 검증 키를 `product_scope` 단독 → `(product_scope, broker_provider)` 조합으로 확장
- `available_brokers`를 `Dict[scope, Set[provider]]`로 변경 (기존 덮어쓰기 버그 해결)
- 에러 메시지 scope 라벨 버그 수정 (KOREA_STOCK/COIN이 overseas_futures로 오표기)
- `_auto_inject_connection`은 이미 scope+provider 매칭 — 변경 불필요 확인
- 같은 국내주식 스코프에 LS `KoreaStockBrokerNode` + `KisBrokerNode` 공존 가능

**Phase B — finance SDK `kis/` 패키지 (v1.10.0)**
- `KisTokenManager`: 접근토큰 24h 파일 캐시(`~/.programgarden/kis_token_*.json`, 재발급 분당 1회 제한 대응), approval_key 관리
- `GenericKisTR`: tr_id (실전, 모의) 튜플 자동 분기, rt_cd 봉투 파싱, 토큰 만료 시 1회 재발급 재시도
- TR 7종: 현재가/호가/일봉, 잔고/매수가능, 현금매수·매도/정정취소
- `KisRealBase`: 파이프 구분 프레임, PINGPONG 에코, AES-256-CBC 체결통보 복호화(key/iv 레이스 버퍼링), 재연결 자동 재구독
- 실시간 2종: 체결가 H0STCNT0, 체결통보 H0STCNI0/H0STCNI9
- pycryptodome 의존성 추가, 예제 스크립트 4종

**Phase C — core 노드 6종 (v1.16.0)**
- `BrokerProvider.KIS = "koreainvestment.com"` 추가
- KisBrokerNode(paper_trading 필드) / KisAccountNode / KisMarketDataNode / KisHistoricalDataNode / KisNewOrderNode / KisCancelOrderNode
- 전 노드 `_examples`(스니펫 12종 검증 통과)·`_node_guide` 완비, i18n en/ko
- `test_registry_node_count` 기준선 69→81 (기존 실패 수정)

**Phase D — 엔진 executor (v1.26.0)**
- `kis_executors.py` 6종 — deep_validate에서 Kis 클라이언트 절대 미생성(토큰 발급=라이브 호출)
- `deep_fixtures.py` Kis 분기 + fixture 3종
- deep_validate 테스트 6종 (무 API 호출 검증, LS+KIS 멀티브로커 통과)

**Phase E — 예제·문서**
- 워크플로우 예제 90(계좌)/91(시세)/92(RSI 봇, 89번의 KIS 버전) — 전부 deep_validate 가상 풀-실행 통과
- `00-workflow-guide.md` KIS 섹션 + 멀티브로커 바인딩 규칙, `docs/kis_finance_guide.md` 신규

### 테스트

- finance: KIS 신규 57 passed (tr_id 실전/모의 매트릭스, AES 테스트벡터, 토큰 캐시), 전체 1638 passed
- core: 809 passed (Bithumb 메타데이터 shape 기존 실패 6건은 TODO로 이관)
- programgarden: deep_validate 47 passed, split 16 passed, 예제 검증 회귀 없음

### 참고

- 미래에셋증권은 공개 REST 오픈API 미확인으로 보류
- 키움증권은 다음 브랜치에서 동일 패턴으로 진행 예정
- 남은 기존 실패는 전부 main에서도 동일 (venv community 미설치 22건, LS field metadata 164건, Bithumb shape 6건)

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
