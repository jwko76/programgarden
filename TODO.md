# TODO

## 진행 중

없음.

## 빗썸 (Bithumb) — 코인 지원

- [x] **Bithumb 실시간 WebSocket 구현** (2026-06-19, 미커밋)
  - `real_base.py`, `real/ticker/`, `real/trade/`, `real/orderbook/`
  - `Bithumb().real()` 싱글톤 메서드
  - `tests/test_bithumb_real.py` 47 PASS
  - `example/bithumb/run_real_ticker.py`

## 워크플로우 — 코인 노드

- [x] **빗썸 노드 5종 추가** (2026-06-19, 미커밋)
  - `BithumbBrokerNode`, `BithumbAccountNode`, `BithumbMarketDataNode`, `BithumbNewOrderNode`, `BithumbCancelOrderNode`
  - `ProductScope.COIN`, `BrokerProvider.BITHUMB` 추가
  - executor 5개 (`bithumb_executors.py`)
  - deep_validate 픽스처 추가
  - i18n ko/en 키 추가
- [x] **빗썸 워크플로우 예제** (`src/programgarden/examples/workflows/`) (2026-06-19, 커밋 완료)
  - `87-bithumb-account` — 계좌 잔고 조회
  - `88-bithumb-market-data` — 현재가 조회 (공개 API)
  - `89-bithumb-rsi-bot` — RSI 기반 BTC 자동매수 봇

## LS TR 변경사항 대응

- [x] **t8408/t8409/t8429 구현** — 2026-06-21 커밋, RES 스펙 기반
- [x] **o3121 ticktype 추가** (2026-06-20 커밋)
- [x] **신규 TR 63개 전체 추가** (2026-06-21, v1.8.0)

## 문서

- [ ] **빗썸 API 가이드** 문서 보완 (README 또는 gitbook)
- [x] **00-workflow-guide.md** §14 Bithumb 코인 섹션 추가 (2026-06-20, 커밋 완료)
  - §8 Product Scope 표 업데이트
  - §9 Bithumb 노드 포트 레퍼런스 추가
  - §14 신규 섹션 (인증·노드흐름·주문방식·실시간WebSocket·예제)

## 유지보수

- [x] deep_validate 커버리지 확장 — 빗썸 노드 5개 테스트 추가 (2026-06-20, 커밋 완료)
- [x] finance 버전 업 v1.7.0 (2026-06-19, 커밋 완료)

---

## 완료됨

- [x] 빗썸 워크플로우 노드 5종 — BithumbBrokerNode 외 4개, executor, i18n (2026-06-19, 미커밋)
- [x] Bithumb 실시간 WebSocket 구현 — ticker/trade/orderbook, 47 테스트 PASS (2026-06-19, 미커밋)
- [x] Bithumb REST API 래퍼 37개 엔드포인트 전체 구현 (v1.6.10 → 224ba03, 2026-06-13)
- [x] deep_validate 정적 바인딩 스캔 강화 (v1.23.1, 2026-06-13)
- [x] deep workflow validation Phase 1.5 (v1.23.0, 2026-06-13)
- [x] LS token_provider opt-in wiring (v1.22.4, 2026-06-06)
- [x] HKEX 해외선물 모의투자 예제 5종 81-85 (v1.22.3, 2026-06-01)
- [x] 국내주식 Finance API 88개 TR (v1.6.5 이전)
