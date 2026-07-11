# 90. 한국투자증권 계좌 잔고 대시보드

## 개요

한국투자증권(KIS Developers) OpenAPI를 통해 예수금·보유 종목·평가손익을 조회합니다.
`KisBrokerNode` → `KisAccountNode` → 디스플레이 노드의 기본 패턴을 보여줍니다.

## 노드 구성

| 노드 | 타입 | 역할 |
|------|------|------|
| start | StartNode | 워크플로우 시작 |
| broker | KisBrokerNode | KIS API 인증 게이트웨이 (paper_trading=true — 모의투자) |
| account | KisAccountNode | 주식잔고조회 (실전 TTTC8434R / 모의 VTTC8434R) |
| balance_display | SummaryDisplayNode | 예수금·평가금액 요약 표시 |
| positions_display | TableDisplayNode | 보유 종목 목록 표시 |

## 출력 포트

`KisAccountNode`는 세 포트를 출력합니다:

- **`balance`** — 계좌 요약 객체
  - `deposit`: 예수금 총액
  - `orderable_amount`: 주문 가능 현금 (D+2 정산금액)
  - `total_evaluation`: 총 평가 금액
  - `total_purchase`: 매입 금액 합계
  - `total_profit_loss`: 평가 손익 합계
- **`positions`** — 보유 종목 배열
  - `symbol`, `symbol_name`, `quantity`, `orderable_quantity`, `avg_buy_price`,
    `current_price`, `evaluation_amount`, `profit_loss`, `profit_loss_rate`
- **`held_symbols`** — 보유 종목코드 배열 (`[{"symbol": "005930"}]`)

## 인증 (broker_kis)

[KIS Developers](https://apiportal.koreainvestment.com)에서 앱 등록 후 발급:

| 키 | 설명 |
|----|------|
| `appkey` | 앱 키 |
| `appsecret` | 앱 시크릿 |
| `account_no` | 종합계좌번호 앞 8자리 (CANO) |
| `account_product_code` | 계좌상품코드 뒤 2자리 (기본 `01`) |

모의투자는 KIS Developers에서 별도 신청 후 모의투자용 appkey를 사용합니다.

## 멀티브로커

같은 국내주식 스코프의 LS `KoreaStockBrokerNode`와 한 워크플로우에 공존할 수 있습니다.
`Kis*` 노드는 KIS 연결에, `KoreaStock*` 노드는 LS 연결에 각각 자동 바인딩됩니다.

## 활용 예시

- `balance.orderable_amount` → `IfNode` (잔고 >= 1,000,000원 → 주문 허용)
- `positions` → `TableDisplayNode` (포트폴리오 현황 대시보드)
- `held_symbols` → `SymbolFilterNode` (미보유 종목 필터링)
