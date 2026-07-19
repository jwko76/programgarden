# 94. 키움증권 현재가·일봉 조회

## 개요

키움증권 OpenAPI로 여러 종목의 현재가를 조회하고, 일봉 데이터를 캔들 차트로
표시합니다. 시세 조회에도 브로커 인증이 필요한 점이 빗썸 공개 API와 다릅니다.

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 워크플로우 시작 |
| broker | KiwoomBrokerNode | 키움 OpenAPI 인증 게이트웨이 |
| market | KiwoomMarketDataNode | 현재가 조회 (api-id ka10001) — `005930,000660` |
| candles | KiwoomHistoricalDataNode | 일봉 60개 조회 (api-id ka10081) |
| price_table | TableDisplayNode | 현재가 테이블 |
| candle_chart | CandlestickChartNode | 일봉 캔들 차트 |

## 출력 포트

- `KiwoomMarketDataNode.values` — 종목별 `{symbol, current_price, change,
  change_rate, open_price, high_price, low_price, volume, per, pbr}` 배열
- `KiwoomHistoricalDataNode.values` — 최신→과거 순 OHLCV 캔들 배열
- `KiwoomHistoricalDataNode.time_series` — ConditionNode(RSI/Bollinger 등)에
  직결 가능한 `[{symbol, exchange, time_series}]` 형식 (oldest-first 자동 정렬)

## 참고

- 시세는 모의투자 여부와 무관하게 실전 데이터가 반환됩니다.
- 키움 시세 응답의 가격 필드는 `+`/`-` 부호가 붙을 수 있어 executor가
  절대값으로 정규화합니다.
- RSI 봇 구성은 `95-kiwoom-rsi-bot` 예제를 참고하세요.
