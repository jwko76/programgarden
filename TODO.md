# TODO

## 진행 중

- [ ] **feature/kis-broker 브랜치** — 한국투자증권(KIS) 연동 구현 완료, main 머지 대기

## 다음 작업 후보

- [ ] **키움증권 브로커** — KIS와 동일 패턴으로 별도 브랜치에서 구현 (REST API openapi.kiwoom.com, appkey/secret→토큰 인증이 KIS와 유사. kis/ 패키지·Kis* 노드·kis_executors를 템플릿으로 복제)
- [ ] **KIS 확장 (MVP 이후 보류분)** — hashkey 헤더, tr_cont 페이지네이션, KisModifyOrderNode(정정), H0STASP0 실시간 호가, 주문가능조회 노드화, LS식 token-provider 모드
- [ ] **Bithumb 노드 _examples/_node_guide 보완** — test_node_schema_ai_fields shape 테스트 기존 실패 6건 해소 (KIS 노드는 완비됨)
- [ ] **BithumbHistoricalDataNode 분봉 지원** — 현재 일봉만, `/v1/candles/minutes/{unit}` 래핑
- [ ] **Community 플러그인 추가** — upstream에서 TrailingStop v2.1.0 이후 신규 전략 검토
- [ ] **deep type-aware validation Phase 4+** — upstream 로드맵 추적
- [ ] **미래에셋증권** — 공개 REST 오픈API 미확인으로 보류 (개발자센터 공개 시 재검토)

---

## 완료됨

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
