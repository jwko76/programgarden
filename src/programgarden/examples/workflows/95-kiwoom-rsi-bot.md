# 95. 키움증권 RSI 과매도 자동매수 봇 (모의투자)

## 개요

장중 5분마다 삼성전자 일봉 30개로 RSI(14)를 계산해, 과매도(30 이하) 구간에서
모의투자 시장가 매수를 실행하는 전형적인 지표 기반 자동매매 패턴입니다.

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 워크플로우 시작 |
| broker | KiwoomBrokerNode | 키움 인증 (paper_trading=true — mockapi.kiwoom.com) |
| schedule | ScheduleNode | 평일 09~15시, 5분 간격 실행 |
| account | KiwoomAccountNode | 예수금·잔고 모니터링 (표시용) |
| candles | KiwoomHistoricalDataNode | 일봉 30개 (api-id ka10081) |
| rsi | ConditionNode (RSI) | RSI(14) < 30 판정 |
| throttle | ThrottleNode | 최소 300초 간격 — 중복 주문 방지 |
| buy_order | KiwoomNewOrderNode | 시장가 1주 매수 (api-id kt10000) |

## 흐름

```
start → broker → schedule ─┬→ account
                           └→ candles → rsi → throttle → buy_order
```

- `KiwoomHistoricalDataNode.time_series`는 ConditionNode가 기대하는
  oldest-first `[{symbol, exchange, time_series}]` 형식으로 바로 연결됩니다.
- 통과 시 `{{ item.symbol }}` 바인딩으로 어떤 종목이 조건을 충족했는지
  주문 노드에 전달됩니다.

## 안전장치

- **paper_trading=true** — 모의투자 도메인 접속. 실전 전환 전 충분히 검증하세요.
- **ThrottleNode(300초)** — 같은 시그널로 5분 내 재주문 방지.
- **resilience.fallback.mode=skip** — 주문 실패 시 워크플로우 중단 없이 스킵.
- **KiwoomNewOrderNode 재시도 기본 비활성** — 중복 주문 위험 차단.
- 실행 전 `ProgramGarden.validate_deep()`으로 전체 경로를 가상 실행해 보세요.

## 실전 전환 체크리스트

1. 모의투자에서 주문 접수·체결 통보까지 확인
2. `paper_trading: false` + 실전 appkey로 교체
3. 주문 수량·금액 상한을 IfNode/RiskNode로 게이트
4. 시장가 대신 지정가(`order_type: "limit"`, `price` 지정) 고려
