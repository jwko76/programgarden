# TODO

## 진행 중

- [ ] **KIS 실전 주문 라이브 검증 — 재시도 대기 (다음 개장일 장중)**
  - 2026-07-13 시도: `run_order_lifecycle_live.py` 실행 → 토큰 발급/현재가 조회 정상, 매수 주문에서
    `장운영일자가 주문일과 상이합니다 (APBK0919)` 거부 (주문 미접수, 취소 단계 미실행 — 계좌에 걸린 주문 없음)
  - 코드(`tr_helpers.py`/`order/__init__.py`) 헤더·계좌번호 채움 로직 정상 확인, 같은 계좌로 잔고·매수가능 조회는 7/11 기성공
  - 사용자 확인: 이 계좌로 HTS/MTS 수동 매매 이력 있음 → "API 최초 이용 라우팅 미활성화" 가설 배제
  - **2026-07-18: 사용자가 KIS 홈페이지/앱에서 "오픈API 서비스 신청"(약관동의+계좌연결) 완료** — 원인으로 지목했던
    항목 해소, 다음 개장일 장중에 재시도 예정 (자동 예약은 보안/환경 제약으로 보류 — 장중에 사용자가 직접 요청)
  - 재시도 명령: `KIS_LIVE_ORDER_CONFIRM=YES .venv-bithumb/bin/python src/finance/example/kis/run_order_lifecycle_live.py` (WSL)
  - 실시간 체결가(`run_real_ccnl.py`, H0STCNT0)는 주문 이슈와 무관하니 별도로 먼저 검증 가능
  - 완료 기준: REST 7종 + 실시간 전부 라이브 검증 → CLAUDE.md/WORKLOG 갱신

## 보류 중

- [ ] **키움증권 라이브 검증 — 잔여분** (2026-07-18 모의서버 1차 검증 완료, 아래 "완료됨" 참조)
  - [ ] **주문 접수/체결** — 모의서버가 주말 거부(RC4010: 모의투자 영업일이 아닙니다). **다음 영업일 장중**
    `KIWOOM_PAPER=1 .venv-bithumb/bin/python src/finance/example/kiwoom/run_order_lifecycle.py` (WSL) 재시도.
    trde_tp 코드값(지정가 "0"/시장가 "3" 추정)·취소 전량 규칙(ord_qty="0" 추정)·주문 응답 필드 확인
  - [ ] **장중 실시간 체결 데이터** — WS 접속·LOGIN·REG는 성공, 실제 0B 데이터 프레임 구조는 장중에만 확인 가능
    (`run_real_ccnl.py`). 체결통보(00)는 주문과 함께 검증
  - [ ] **잔고 보유종목 항목 필드** — 모의계좌에 보유 종목이 없어 `acnt_evlt_remn_indv_tot` 항목 내부 필드명 미확인.
    모의 매수 체결 후 `run_balance.py`로 확인
  - [x] ~~실전 서버 + 빗썸 개인 API IP 화이트리스트~~ — 2026-07-19 해소: OCI 개발서버 고정 IP 등록 후
    키움 실전 토큰·시세(현재가/호가/일봉)·잔고(kt00018 요약) + 빗썸 전체자산조회 라이브 통과
  - [ ] **주문가능(kt00010) trde_tp 코드 확인** — 실전에서 TR 실행은 확인됐으나 uv=255000, trde_tp="1"(매수로 추정)에
    "매도가격이 하한가보다 낮습니다" 반환 → **trde_tp 1이 매도일 가능성**. 영업일 장중 재확인 후 blocks.py 주석 교정
  - [ ] rate-limit 정책 실측 (현재 KIS 기준 초당 20건 차용)

## 다음 작업 후보
- [ ] **조건 플러그인 크로스 트리거 확대 — Phase 3 (선택)** (Phase 0/1/2는 완료, 아래 "완료됨" 참조)
  - **모니터링 지표**: sharpe_ratio_monitor, sortino_ratio, calmar_ratio, correlation_analysis — 알림 쓰임새 있으면 추가
  - 공통 규칙: 기존 enum 값·기본값 불변(하위호환), 스키마 minor 버전 bump, prev 값 None(데이터 부족) 시 크로스 불통과, 플러그인별 단위테스트(돌파 통과/유지 침묵/부족 데이터)
- [ ] **Community 플러그인 추가** — upstream에서 TrailingStop v2.1.0 이후 신규 전략 검토
- [ ] **deep type-aware validation Phase 4+** — upstream 로드맵 추적
- [ ] **미래에셋증권** — 공개 REST 오픈API 미확인으로 보류 (개발자센터 공개 시 재검토)

---

## 완료됨

- [x] **조건 플러그인 크로스 트리거 확대 — Phase 2 (밴드/레벨 터치형)** (2026-07-19, main, community v1.16.0)
  - bollinger_bands(`cross_below_lower`/`cross_above_upper`, v3.1.0), vwap(`cross_above`/`cross_below`, v1.1.0),
    cmf(`cross_accumulation`/`cross_distribution`, v1.1.0), relative_strength(`cross_above`/`cross_below`, v1.1.0) 4종 추가
  - RelativeStrength는 population(벤치마크 포함) 전체 랭킹이 매 봉 재계산되는 구조라 "직전 값"이 따로 없음 —
    전체를 한 봉 이전 시점으로 다시 랭킹매기는 `_rank_relative_strength` 헬퍼 신설(trim 파라미터로 최근 N봉 제외)
  - 볼린저는 표준 2-std 밴드가 선형 하락/상승으로는 수학적으로 거의 돌파되지 않음을 확인(평균 지연 2d vs 2-std 폭 2.83d) —
    테스트 데이터는 std_dev=1.0으로 설계(스키마 허용 범위 내)
  - `symbol_results`에 `prev_*` 필드 추가, 기존 enum·기본값 불변. 단위테스트 4파일 18건 신규,
    community 전체 1257 passed(기존 파일 파서 28건 실패는 openpyxl 미설치로 무관), 회귀 0건
  - docs/signal_dedup_migration_guide.md §7 갱신. Phase 3(모니터링)은 위 "다음 작업 후보"로 이월

- [x] **KIS 확장 (MVP 이후 보류분)** (2026-07-19, feature/kis-extensions) — finance 1.12.0 / core 1.19.0 / programgarden 1.29.0
  - hashkey 헤더: `/uapi/hashkey` 발급 + POST 주문 TR 자동 첨부 (`use_hashkey` 옵션, 발급 실패해도 주문은 진행)
  - tr_cont 연속조회: `inquire_balance().req_all()`/`req_all_async()` — 여러 페이지 자동 수집·병합, executor도 전환
  - LS식 token-provider 모드: 외부 서버가 토큰 발급 전담, 클라이언트는 소비만 (`Kis(token_provider=...)`).
    KIS는 모든 TR에 appkey/appsecret 헤더가 필요해 LS와 달리 provider는 토큰 발급만 위임(appkey/appsecret은 여전히 필요)
  - H0STASP0 실시간 호가: `real/asking_price/` 신규 모듈, `kis.실시간().호가()`
  - `KisModifyOrderNode`(정정, RVSE_CNCL_DVSN_CD=01) + `KisOrderableAmountNode`(매수가능조회) core 노드 신규 —
    i18n(ko/en)·executor·deep fixture 완비. 정정 시 주문번호가 바뀌므로 modified_order_no 사용 필요(문서화)
  - 테스트: finance 신규 4개 파일(hashkey/pagination/token_provider/real_asking_price) + 기존 파일 보강,
    core 노드 개수 87→89 갱신, deep_validate 신규 3건 — 회귀 없음(finance 전체 3300+ passed, KIS 관련 실패 0)
  - 라이브 검증 미실시(코드 레벨만) — 다음 KIS 실전 주문 검증 시 hashkey/정정/연속조회 함께 확인 권장

- [x] **키움증권 모의서버 1차 라이브 검증** (2026-07-18, feature/kiwoom-broker)
  - 토큰 발급(24h TTL, 파일캐시 복원) / 현재가 ka10001(추정 필드 전부 적중, 가격 등락부호 확인) /
    호가 ka10004(최우선호가는 `sel_fpr_bid`/`buy_fpr_bid`로 교정) /
    일봉 ka10081(리스트 키 `stk_dt_pole_chart_qry`로 교정, 600건 수신) /
    잔고 kt00018(리스트 키 `acnt_evlt_remn_indv_tot`, 예수금 없음 → `prsm_dpst_aset_amt`로 교정)
  - WebSocket: `wss://mockapi.kiwoom.com:10000/api/dostk/websocket` 접속 + LOGIN return_code=0 + REG 정상
    (실전/모의 호스트 분리, 경로 확정 — config.py 교정)
  - .env 키 구조: 실전 `KIWOOM_*` / 모의 `KIWOOM_MOCK_*` 분리 — 예제 공용 `_env.py`로 자동 선택
  - finance 키움 테스트 59건 확정 필드명으로 갱신 후 통과

- [x] **키움증권 브로커 전체 연동** (2026-07-18, feature/kiwoom-broker) — v1.11.0/v1.18.0/v1.28.0
  - finance SDK kiwoom/: TR 9종 + 실시간 2종 (도메인 전환식 실전/모의, POST 단일 바디, 토큰 파일캐시)
  - core 노드 6종 (Kiwoom*) + BrokerProvider.KIWOOM + i18n + AI 메타데이터
  - kiwoom_executors 6종 + deep fixtures — KiwoomCancelOrderNode symbol 필드 추가 (kt10003 종목코드 필수)
  - 워크플로우 예제 93-95 (deep_validate 통과), SDK 예제 4종, docs/kiwoom_finance_guide.md
  - 라이브 검증은 "보류 중" 참조 (app key 대기)

- [x] **조건 플러그인 크로스 트리거 확대 — Phase 0/1** (2026-07-13, feature/signal-cross-trigger, community v1.15.0)
  - Phase 0 검증: aroon/coppock/trix/vortex/parabolic_sar/squeeze_momentum 정상.
    **MACD·MA Cross는 버그** 발견(이름은 cross인데 실제 통과 판정은 레벨 체크) —
    기존 enum 값 그대로 진짜 크로스로 수정 (v3.1.0)
  - Phase 1: williams_r/cci/mfi/connors_rsi/ultimate_oscillator/z_score/mean_reversion
    7종에 cross_oversold·cross_overbought(또는 cross_below·cross_above) 추가 (각 v1.1.0).
    Stochastic은 기존 oversold/overbought가 이미 %K/%D 교차 기반이라 변경 불요(회귀 테스트만 추가)
  - 부수 수정: WilliamsR `overbought_threshold` 공식 버그(-80+100=20 → 도달 불가능을 -100-threshold=-20으로)
  - docs/signal_dedup_migration_guide.md §7 지표별 크로스 enum 표 갱신
  - Phase 2(밴드형)/3(모니터링)은 위 "다음 작업 후보"로 이월

- [x] **시그널 알림 중복 방지** (2026-07-12, feature/signal-cross-trigger)
  - RSI v3.1.0: cross_below/cross_above 크로스 트리거 (community v1.14.0)
  - ThrottleNode v1.1.0: interval_sec 상한 300 → 86,400초
  - 00-workflow-guide §14.4.1 권장 패턴 문서화

- [x] **빗썸 노드 AI 메타데이터 완비 + 분봉 지원** (2026-07-12, feature/bithumb-node-polish)
  - 노드 6종 _anti_patterns/_examples/_node_guide 보완 — shape 테스트 실패 6건 해소, 스니펫 12개 validate 통과
  - BithumbHistoricalDataNode v1.1.0: interval 필드 (day/week/month/1m~240m), executor 4-way 분기, i18n 누락 키 보강
  - 엔진 전체 경로로 5m/day/week/month 공개 API 라이브 검증

- [x] **한국투자증권(KIS) 연동 전체** (2026-07-11, feature/kis-broker) — v1.10.0/v1.16.0/v1.26.0
  - 멀티브로커: resolver 검증 키 (scope, provider) 확장 — LS+KIS 국내주식 공존
  - finance SDK kis/: TR 7종 + WebSocket 2종 (토큰 파일캐시, 실전/모의 자동 분기, AES 체결통보)
  - core 노드 6종 (Kis*) + i18n + _examples 완비
  - kis_executors 6종 + deep fixtures, 워크플로우 예제 90-92

- [x] **upstream merge v1.24.1 → v1.25.0** (2026-06-23)
  - deep type-aware validation Phase 1-3, order-error-mapping, TrailingStop v2.1.0 통합
  - finance v1.9.0 유지 (TR 200개+, 빗썸 완성)
  - 워크플로우 91개 (upstream 88 + bithumb 87-89)
- [x] **형상관리 재구성** (2026-06-23) — upstream(pull) / jwko76(push) 분리
  - jwko76/programgarden 레포 신규 생성
  - LONG_RUNNING_WORKFLOWS/KNOWN_MOCK_FRAGILE 정리 — 308 passed
- [x] **빗썸 API 가이드** 문서 보완 (2026-06-23)
- [x] **BithumbHistoricalDataNode** (2026-06-22) — /v1/candles/days, RSI 직결
- [x] **SECURE_CODING.md** 8개 섹션 보안 규칙 문서 (2026-06-22)
- [x] **LS TR RES 전수 비교 + 신규 TR 63개** (2026-06-21) — v1.8.0
- [x] **t8408/t8409/t8429** 업종차트 신규 구현 + 버그 4건 수정 (2026-06-21)
- [x] **빗썸 전체 릴리즈** — 워크플로우 87-89 + 버전 v1.7.0/v1.14.6/v1.23.2 (2026-06-19)
- [x] **빗썸 노드 5종** — BithumbBrokerNode 외 4개, executor, i18n (2026-06-19)
- [x] **Bithumb 실시간 WebSocket** — ticker/trade/orderbook, 47 PASS (2026-06-19)
- [x] **Bithumb REST API** 37개 엔드포인트 (2026-06-13)
- [x] **국내주식 Finance API** 88개 TR (v1.6.5 이전)
- [x] **HKEX 해외선물 모의투자 예제** 5종 81-85 (2026-06-01)
- [x] **deep workflow validation** Phase 1.5 (v1.23.0)
