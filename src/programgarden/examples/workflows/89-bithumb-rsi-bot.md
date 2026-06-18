# 89. 빗썸 RSI 과매도 BTC 자동매수 봇

## 개요

5분마다 BTC/KRW 일봉 캔들 30개를 빗썸 공개 API로 가져와 RSI(14)를 계산합니다.  
RSI가 30 이하(과매도) 진입 시 시장가 50,000 KRW 소액 매수를 실행합니다.  
`ThrottleNode`로 5분 이내 중복 주문을 방지합니다.

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 시작 |
| broker | BithumbBrokerNode | 빗썸 인증 게이트웨이 |
| schedule | ScheduleNode | 5분 간격 트리거 (`*/5 * * * *`) |
| account | BithumbAccountNode | 잔고 모니터링 (표시용) |
| candles | HTTPRequestNode | `/v1/candles/days?market=KRW-BTC&count=30` 일봉 조회 |
| rsi | ConditionNode (RSI) | RSI(14) 계산 → 과매도 30 이하 필터 |
| throttle | ThrottleNode | 최소 300초 간격 주문 제한 |
| buy_order | BithumbNewOrderNode | 시장가 50,000 KRW 매수 (`bid`, `price`) |

## 전략 흐름

```
ScheduleNode (5분마다)
  ├─ BithumbAccountNode      : 잔고 확인 (모니터링용)
  └─ HTTPRequestNode (캔들)
       └─ ConditionNode (RSI < 30)
            └─ ThrottleNode (300초)
                 └─ BithumbNewOrderNode (시장가 매수 50,000 KRW)
```

## RSI 캔들 데이터 구조

`HTTPRequestNode`가 빗썸 공개 API를 호출하여 일봉 30개를 반환합니다.  
`ConditionNode`의 `items.from`에 인라인 래퍼로 묶어 RSI 플러그인에 전달합니다:

```json
"items": {
  "from": [{"symbol": "KRW-BTC", "exchange": "BITHUMB",
            "time_series": "{{ nodes.candles.response }}"}],
  "extract": {"date": "{{ row.candle_date_time_utc }}", "close": "{{ row.trade_price }}"}
}
```

## 주문 설정

- `side`: `bid` (매수)
- `order_type`: `price` (시장가 매수 — KRW 총액 지정)
- `order.price`: `"50000"` (50,000 KRW)
- `resilience.fallback.mode`: `skip` (주문 실패 시 조용히 넘어감)

## 파라미터 조정

| 항목 | 현재값 | 변경 방법 |
|------|--------|-----------|
| RSI 임계값 | 30 | `rsi.fields.threshold` |
| RSI 기간 | 14 | `rsi.fields.period` |
| 매수 금액 | 50,000 KRW | `buy_order.order.price` |
| 스케줄 | 5분 | `schedule.cron` |
| 주문 쿨다운 | 300초 | `throttle.min_interval_sec` |

## 주의사항

- **실 계좌**: BithumbBrokerNode에 Access Key / Secret Key 입력 필수
- **검증 먼저**: `ProgramGarden.validate_deep(workflow)` 로 사전 검증 권장
- **소액 테스트**: 처음엔 `order.price`를 최소 주문 금액(5,000 KRW 이상)으로 설정 후 테스트
- **단일 종목**: 현재는 KRW-BTC만 지원 (다종목 확장 시 WatchlistNode + auto-iterate 패턴 참고)
