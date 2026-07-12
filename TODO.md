# TODO

## 진행 중

- [ ] **KIS 실전 라이브 검증 마무리 — 2026-07-13(월) 장중 (09:00~15:30 KST)**
  - [ ] 주문 라이프사이클: `run_order_lifecycle_live.py` — 한화생명(088350) 하한가 지정가 1주 매수 → 즉시 취소
    - 실행: WSL에서 `KIS_LIVE_ORDER_CONFIRM=YES .venv-bithumb/bin/python src/finance/example/kis/run_order_lifecycle_live.py`
    - 취소 실패 시 HTS/MTS에서 수동 취소 (주문번호 로그에 출력됨)
  - [ ] 실시간 체결가: `run_real_ccnl.py` (H0STCNT0, 60초 수신) — 주문 실행과 병행하면 체결통보(H0STCNI0)도 확인 가능
  - 완료 기준: REST 7종 + 실시간 전부 라이브 검증 → CLAUDE.md/WORKLOG 갱신

## 다음 작업 후보

- [ ] **키움증권 브로커** — KIS와 동일 패턴으로 별도 브랜치에서 구현 (REST API openapi.kiwoom.com, appkey/secret→토큰 인증이 KIS와 유사. kis/ 패키지·Kis* 노드·kis_executors를 템플릿으로 복제). 사용자 app key 발급 대기 중
- [ ] **조건 플러그인 크로스 트리거 확대** — RSI v3.1.0 패턴(직전 캔들 지표값 비교 + prev_* 필드 + 돌파 캔들만 signal 마킹)을 다른 레벨형 플러그인에 복제. 알림 중복 방지 (docs/signal_dedup_migration_guide.md 참조)
  - **Phase 1 — 오실레이터 (RSI와 동일 구조, 임계값 1개)**: stochastic(`cross_oversold`/`cross_overbought`), williams_r, cci, mfi, connors_rsi, ultimate_oscillator, z_score, mean_reversion — 각각 direction enum 2종 추가 + prev 지표값 + 테스트 (RSI test_rsi_plugin.py 템플릿)
  - **Phase 2 — 밴드/레벨 터치형**: bollinger_bands(`cross_below_lower`/`cross_above_upper`), vwap, cmf(accumulation/distribution 진입 순간), relative_strength — 밴드는 "가격 vs 밴드값" 비교라 직전 캔들의 밴드·가격 모두 필요
  - **Phase 3 — 모니터링 지표 (선택)**: sharpe_ratio_monitor, sortino_ratio, calmar_ratio, correlation_analysis — 알림 쓰임새 있으면 추가
  - **Phase 0 (선행 검증)**: 기존 크로스형 플러그인들(macd bullish_cross, ma_cross, aroon cross_up, coppock zero_cross, trix, vortex, parabolic_sar reversal, squeeze fire)이 실제로 "돌파 캔들에서만 통과"인지 테스트로 확인 — 레벨처럼 동작하는 놈이 있으면 함께 수정
  - 공통 규칙: 기존 enum 값·기본값 불변(하위호환), 스키마 minor 버전 bump, prev 값 None(데이터 부족) 시 크로스 불통과, 플러그인별 단위테스트(돌파 통과/유지 침묵/부족 데이터)
  - 예상 규모: Phase 1이 플러그인당 ~30분 (계산 함수는 기존 것 재사용, 조건 평가부와 스키마만 수정)
- [ ] **KIS 확장 (MVP 이후 보류분)** — hashkey 헤더, tr_cont 페이지네이션, KisModifyOrderNode(정정), H0STASP0 실시간 호가, 주문가능조회 노드화, LS식 token-provider 모드
- [ ] **Community 플러그인 추가** — upstream에서 TrailingStop v2.1.0 이후 신규 전략 검토
- [ ] **deep type-aware validation Phase 4+** — upstream 로드맵 추적
- [ ] **미래에셋증권** — 공개 REST 오픈API 미확인으로 보류 (개발자센터 공개 시 재검토)

---

## 완료됨

- [x] **시그널 알림 중복 방지** (2026-07-12, feature/signal-cross-trigger)
  - RSI v3.1.0: cross_below/cross_above 크로스 트리거 (community v1.14.0)
  - ThrottleNode v1.1.0: interval_sec 상한 300 → 86,400초
  - 00-workflow-guide §14.4.1 권장 패턴 문서화
  - 후속 후보: 다른 조건 플러그인(Bollinger, MACD 등)에도 크로스 모드 확대

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
