# 92. 한국투자증권 RSI 과매도 자동매수 봇 (모의투자)

## 개요

89번 빗썸 RSI 봇의 KIS 국내주식 버전입니다. 장중 5분마다 삼성전자 일봉 30개로
RSI(14)를 계산하고, 과매도(RSI < 30) 시 모의투자 시장가 매수를 실행합니다.

**흐름**: `KisBrokerNode(모의)` → `ScheduleNode` → `KisHistoricalDataNode` →
`ConditionNode(RSI)` → `ThrottleNode` → `KisNewOrderNode`

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| broker | KisBrokerNode | 모의투자 연결 (paper_trading=true) |
| schedule | ScheduleNode | 평일 09~15시 5분 주기 (`*/5 9-15 * * 1-5`, Asia/Seoul) |
| account | KisAccountNode | 잔고 모니터링 (표시용) |
| candles | KisHistoricalDataNode | 일봉 30개 → `time_series` 포트 |
| rsi | ConditionNode(RSI) | period=14, threshold=30, direction=below |
| throttle | ThrottleNode | 최소 300초 간격 — 중복 주문 방지 |
| buy_order | KisNewOrderNode | 시장가 1주 매수 (모의 VTTC0802U 자동 선택) |

## 핵심 포인트

1. **모의투자 우선**: `paper_trading: true`로 실계좌 없이 전체 플로우 검증.
   실전 전환 시 브로커 노드의 플래그만 변경하면 주문 TR ID(TTTC↔VTTC)가 자동 전환됩니다.
2. **time_series 직결**: `KisHistoricalDataNode.time_series`는 ConditionNode의
   `items.from`에 바로 바인딩됩니다. `extract`에서 `row.date`/`row.close`를 매핑합니다.
3. **ThrottleNode 필수**: 주문 노드는 connection rule로 실시간 소스 직결이 금지되며,
   조건 노드 뒤에도 스로틀을 두어 5분 창 안의 중복 매수를 방지합니다.
4. **resilience.fallback.mode=skip**: 주문 실패(장 마감, 잔고 부족 등) 시
   워크플로우를 중단하지 않고 다음 주기로 넘어갑니다.

## 실행 전 체크리스트

- [ ] KIS Developers에서 모의투자 신청 + 모의투자용 appkey 발급
- [ ] `ProgramGarden.validate_deep()` 통과 확인
- [ ] 모의투자에서 최소 수 일간 동작 검증 후 실전 전환 검토
