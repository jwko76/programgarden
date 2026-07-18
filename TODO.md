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

## 다음 작업 후보

- [ ] **키움증권 브로커** — KIS와 동일 패턴으로 별도 브랜치에서 구현 (REST API openapi.kiwoom.com, appkey/secret→토큰 인증이 KIS와 유사. kis/ 패키지·Kis* 노드·kis_executors를 템플릿으로 복제). 사용자 app key 발급 대기 중
- [ ] **조건 플러그인 크로스 트리거 확대 — Phase 2/3** (Phase 0/1은 완료, 아래 "완료됨" 참조)
  - **Phase 2 — 밴드/레벨 터치형**: bollinger_bands(`cross_below_lower`/`cross_above_upper`), vwap, cmf(accumulation/distribution 진입 순간), relative_strength — 밴드는 "가격 vs 밴드값" 비교라 직전 캔들의 밴드·가격 모두 필요
  - **Phase 3 — 모니터링 지표 (선택)**: sharpe_ratio_monitor, sortino_ratio, calmar_ratio, correlation_analysis — 알림 쓰임새 있으면 추가
  - 공통 규칙: 기존 enum 값·기본값 불변(하위호환), 스키마 minor 버전 bump, prev 값 None(데이터 부족) 시 크로스 불통과, 플러그인별 단위테스트(돌파 통과/유지 침묵/부족 데이터)
- [ ] **KIS 확장 (MVP 이후 보류분)** — hashkey 헤더, tr_cont 페이지네이션, KisModifyOrderNode(정정), H0STASP0 실시간 호가, 주문가능조회 노드화, LS식 token-provider 모드
- [ ] **Community 플러그인 추가** — upstream에서 TrailingStop v2.1.0 이후 신규 전략 검토
- [ ] **deep type-aware validation Phase 4+** — upstream 로드맵 추적
- [ ] **미래에셋증권** — 공개 REST 오픈API 미확인으로 보류 (개발자센터 공개 시 재검토)

---

## 완료됨

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
