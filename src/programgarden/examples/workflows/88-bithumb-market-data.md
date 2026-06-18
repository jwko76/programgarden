# 88. 빗썸 코인 현재가 조회

## 개요

빗썸 공개 API로 여러 코인의 현재가를 한 번에 조회합니다.  
`BithumbBrokerNode` 없이 `BithumbMarketDataNode`만으로 동작합니다 (인증 불필요).

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 워크플로우 시작 |
| market | BithumbMarketDataNode | `/v1/ticker` 현재가 조회 |
| display | TableDisplayNode | 현재가 테이블 표시 |

## markets 필드

`markets` 필드에 콤마(`,`)로 구분하여 여러 마켓 코드를 입력합니다:

```
KRW-BTC,KRW-ETH,KRW-XRP,KRW-SOL
```

## 출력 필드 (`values` 배열)

| 필드 | 타입 | 설명 |
|------|------|------|
| market | string | 마켓 코드 (KRW-BTC 등) |
| trade_price | number | 최근 체결가 |
| change | string | 변화 방향 (RISE/EVEN/FALL) |
| signed_change_rate | number | 전일 대비 변화율 (소수점) |
| acc_trade_volume_24h | number | 24시간 누적 거래량 |
| high_price / low_price | number | 당일 고가 / 저가 |

## 활용 예시

- `values` → `IfNode` (`trade_price >= 100000000` → 매도 신호)
- `values` → 여러 `TableDisplayNode` / `LineChartNode` (가격 대시보드)
- `BithumbMarketDataNode` + `ScheduleNode` → 주기적 가격 모니터링
