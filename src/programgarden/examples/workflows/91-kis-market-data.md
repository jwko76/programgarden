# 91. 한국투자증권 현재가·일봉 조회

## 개요

KIS API로 여러 종목의 현재가를 조회하고 일봉을 캔들 차트로 표시합니다.
시세 조회도 appkey 인증이 필요하므로(빗썸 공개 API와 다름) `KisBrokerNode`가 필수입니다.

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 워크플로우 시작 |
| broker | KisBrokerNode | KIS API 인증 게이트웨이 |
| market | KisMarketDataNode | 현재가 조회 (FHKST01010100) — `symbols` 콤마 구분 |
| candles | KisHistoricalDataNode | 일봉 조회 (FHKST03010100) — 최대 100건 |
| price_table | TableDisplayNode | 현재가 테이블 |
| candle_chart | CandlestickChartNode | 일봉 캔들 차트 |

## 출력 포트

**`KisMarketDataNode.values`** — 종목별 시세 배열:
`symbol`, `current_price`, `change`, `change_rate`, `open_price`, `high_price`,
`low_price`, `volume`, `trade_amount`, `per`, `pbr`

**`KisHistoricalDataNode`**:
- `values` — 원본 캔들 배열 (최신 먼저): `symbol`, `date`, `open`, `high`, `low`, `close`, `volume`
- `time_series` — ConditionNode 직결 형식 (oldest-first 자동 정렬):
  `[{symbol, exchange: "KRX", time_series: [...]}]`

## 참고

- 종목코드는 6자리 문자열 (앞자리 0 유지 — `005930`)
- 시세 데이터는 모의투자 여부와 무관하게 실전 데이터가 반환됩니다
- KIS rate-limit: 실전 초당 20건, 모의 초당 2건 — SDK가 자동 대기 처리
