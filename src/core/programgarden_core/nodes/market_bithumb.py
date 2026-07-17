"""
ProgramGarden Core - Bithumb Market Data Node

빗썸 시세 조회:
- BithumbMarketDataNode: 현재가 (ticker) REST 1회 조회
"""

from typing import Any, ClassVar, Dict, List, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from programgarden_core.models.field_binding import FieldSchema

from programgarden_core.nodes.base import (
    BaseNode,
    NodeCategory,
    InputPort,
    OutputPort,
    ProductScope,
    BrokerProvider,
)

COIN_TICKER_FIELDS: List[Dict[str, str]] = [
    {"name": "market", "type": "string", "description": "마켓 코드 (KRW-BTC 등)"},
    {"name": "trade_price", "type": "number", "description": "현재가 (최근 체결가)"},
    {"name": "change", "type": "string", "description": "변화 방향 (RISE/EVEN/FALL)"},
    {"name": "signed_change_rate", "type": "number", "description": "부호 있는 변화율"},
    {"name": "acc_trade_volume_24h", "type": "number", "description": "24시간 누적 거래량"},
    {"name": "acc_trade_price_24h", "type": "number", "description": "24시간 누적 거래금액(KRW)"},
    {"name": "high_price", "type": "number", "description": "당일 고가"},
    {"name": "low_price", "type": "number", "description": "당일 저가"},
    {"name": "opening_price", "type": "number", "description": "당일 시가"},
    {"name": "prev_closing_price", "type": "number", "description": "전일 종가"},
]


class BithumbMarketDataNode(BaseNode):
    """
    빗썸 현재가 REST 1회 조회 노드

    빗썸 OpenAPI ``GET /v1/ticker`` 로 현재가를 조회합니다.
    인증이 필요 없는 공개 API 이므로 BithumbBrokerNode 없이도 사용 가능하지만,
    워크플로우에 BithumbBrokerNode가 있으면 자동으로 연결됩니다.

    ``markets`` 필드에 마켓 코드를 콤마 구분으로 입력하세요 (ex. ``KRW-BTC,KRW-ETH``).
    여러 마켓 코드를 입력하면 각 마켓에 대한 현재가가 반환됩니다.
    """

    type: Literal["BithumbMarketDataNode"] = "BithumbMarketDataNode"
    category: NodeCategory = NodeCategory.MARKET
    description: str = "i18n:nodes.BithumbMarketDataNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB

    markets: str = ""

    # 공개 API — BithumbBrokerNode 없이도 동작하므로 브로커 필수 검증에서 제외
    _requires_broker: ClassVar[bool] = False

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "빗썸 코인 현재가 조회",
            "RSI/Bollinger 등 조건 노드에 데이터 공급 전 현재가 확인",
        ],
        "when_not_to_use": [
            "연속 실시간 업데이트 — BithumbRealMarketDataNode 사용 (미구현)",
        ],
        "typical_scenarios": [
            "BithumbMarketDataNode → IfNode (trade_price >= 100000000 → 매도)",
            "BithumbMarketDataNode → TableDisplayNode (현재가 대시보드)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "공개 API — 인증 불필요",
        "여러 마켓 코드 동시 조회 (콤마 구분)",
        "is_tool_enabled=True — AI Agent가 현재가 조회 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "RSI 등 지표 계산용 캔들 소스로 사용",
            "reason": "ticker는 현재가 스냅샷 1건만 반환 — 시계열(OHLCV)이 아닙니다.",
            "alternative": "지표 계산에는 BithumbHistoricalDataNode의 time_series 포트를 사용하세요.",
        },
        {
            "pattern": "짧은 주기 ScheduleNode로 초단위 폴링",
            "reason": "공개 API도 rate-limit이 있어 IP 차단 위험이 있습니다.",
            "alternative": "폴링 주기는 분 단위로 제한하거나 ThrottleNode를 병행하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "코인 현재가 대시보드",
            "description": "BTC·ETH 현재가를 테이블로 표시합니다. 브로커 없이 동작합니다.",
            "workflow_snippet": {
                "id": "bithumb-market-dashboard",
                "name": "빗썸 현재가 대시보드",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "market", "type": "BithumbMarketDataNode", "markets": "KRW-BTC,KRW-ETH"},
                    {"id": "display", "type": "TableDisplayNode", "title": "현재가",
                     "columns": ["market", "trade_price", "signed_change_rate", "acc_trade_volume_24h"],
                     "data": "{{ nodes.market.values }}"},
                ],
                "edges": [
                    {"from": "start", "to": "market"},
                    {"from": "market", "to": "display"},
                ],
            },
            "expected_output": "values 포트에 마켓별 {market, trade_price, ...} 배열이 반환되고 테이블에 표시됩니다.",
        },
        {
            "title": "가격 조건 매수 트리거",
            "description": "BTC 현재가가 목표가 이하로 내려오면 시장가 매수합니다.",
            "workflow_snippet": {
                "id": "bithumb-market-price-trigger",
                "name": "가격 조건 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "market", "type": "BithumbMarketDataNode", "markets": "KRW-BTC"},
                    {"id": "gate", "type": "IfNode",
                     "condition": "{{ nodes.market.values[0].trade_price <= 100000000 }}"},
                    {"id": "buy", "type": "BithumbNewOrderNode", "side": "bid", "order_type": "price",
                     "order": {"market": "KRW-BTC", "price": "50000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "market"},
                    {"from": "market", "to": "gate"},
                    {"from": "gate", "to": "buy", "condition": "true"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "BTC 현재가가 1억원 이하면 50,000 KRW 시장가 매수가 실행됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "markets 필드에 마켓 코드를 콤마 구분으로 입력합니다 (KRW-BTC,KRW-ETH). 공개 API라 브로커 연결이 필수는 아닙니다.",
        "output_consumption": "values 포트는 마켓별 ticker dict 배열 — values[0].trade_price 형태로 참조합니다. 입력 순서가 유지됩니다.",
        "common_combinations": [
            "BithumbMarketDataNode → TableDisplayNode (현재가 대시보드)",
            "BithumbMarketDataNode → IfNode → BithumbNewOrderNode (가격 조건 주문)",
            "ScheduleNode → BithumbMarketDataNode (주기적 시세 수집)",
        ],
        "pitfalls": [
            "현재가 스냅샷 1건 — 지표 계산용 시계열은 BithumbHistoricalDataNode 사용",
            "마켓 코드는 KRW-BTC 형식 (BTC_KRW 아님) — 빗썸 v1 API 규격",
            "change는 문자열(RISE/EVEN/FALL) — 수치 비교에는 signed_change_rate 사용",
        ],
    }

    @classmethod
    def is_tool_enabled(cls) -> bool:
        return True

    _inputs: List[InputPort] = [
        InputPort(name="trigger", type="signal", description="i18n:ports.trigger", required=False),
    ]
    _outputs: List[OutputPort] = [
        OutputPort(
            name="values",
            type="market_data",
            description="i18n:ports.values",
            fields=COIN_TICKER_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-11"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        from programgarden_core.models.field_binding import (
            FieldSchema, FieldType, FieldCategory, ExpressionMode
        )
        return {
            "markets": FieldSchema(
                name="markets",
                type=FieldType.STRING,
                description="i18n:fields.BithumbMarketDataNode.markets",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="KRW-BTC,KRW-ETH",
                example="KRW-BTC,KRW-ETH",
                help_text="콤마(,)로 구분하여 여러 마켓을 입력할 수 있습니다.",
            ),
        }
