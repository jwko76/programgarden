# 87. 빗썸 계좌 잔고 조회

## 개요

빗썸 OpenAPI를 통해 KRW 잔고와 보유 코인 목록을 조회합니다.  
`BithumbBrokerNode` → `BithumbAccountNode` → 디스플레이 노드의 기본 패턴을 보여줍니다.

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 워크플로우 시작 |
| broker | BithumbBrokerNode | 빗썸 API 인증 게이트웨이 |
| account | BithumbAccountNode | `/v1/accounts` 잔고 조회 |
| balance_display | SummaryDisplayNode | KRW 잔고 요약 표시 |
| positions_display | TableDisplayNode | 보유 코인 목록 표시 |

## 출력 포트

`BithumbAccountNode`는 세 포트를 출력합니다:

- **`balance`** — KRW 잔고 객체
  - `krw_balance`: 주문 가능 원화
  - `krw_locked`: 주문 중 묶인 원화
  - `orderable_amount`: 주문 가능 금액 (= krw_balance)
- **`positions`** — 보유 코인 배열 (KRW 제외)
  - `market`, `currency`, `balance`, `locked`, `avg_buy_price`
- **`held_symbols`** — 보유 마켓 코드 배열 (`[{"market": "KRW-BTC"}]`)

## 인증

빗썸 OpenAPI 콘솔 → API 관리 → `Access Key` / `Secret Key` 발급 후 인증 정보에 입력.

## 활용 예시

- `balance.orderable_amount` → `IfNode` (잔고 >= 100,000 KRW → 주문 허용)
- `positions` → `TableDisplayNode` (포트폴리오 현황 대시보드)
- `held_symbols` → `SymbolFilterNode` (미보유 종목 필터링)
