"""
ProgramGarden Core - Bithumb Order Nodes

빗썸 주문 노드:
- BithumbNewOrderNode: 신규 주문 (POST /v2/orders)
- BithumbCancelOrderNode: 주문 취소 (DELETE /v2/order)
"""

import logging
from typing import Any, ClassVar, Dict, List, Literal, Optional, TYPE_CHECKING

from pydantic import Field, model_validator

if TYPE_CHECKING:
    from programgarden_core.models.field_binding import FieldSchema

from programgarden_core.nodes.base import (
    BaseNode,
    NodeCategory,
    InputPort,
    OutputPort,
    ProductScope,
    BrokerProvider,
    RetryableError,
)
from programgarden_core.models.resilience import (
    ResilienceConfig,
    RetryConfig,
    FallbackConfig,
    FallbackMode,
)
from programgarden_core.models.connection_rule import (
    ConnectionRule,
    ConnectionSeverity,
    RateLimitConfig,
    REALTIME_SOURCE_NODE_TYPES,
)

COIN_ORDER_RESULT_FIELDS: List[Dict[str, str]] = [
    {"name": "order_id", "type": "string", "description": "빗썸 주문 ID"},
    {"name": "market", "type": "string", "description": "마켓 코드 (KRW-BTC 등)"},
    {"name": "side", "type": "string", "description": "주문 방향 (bid/ask)"},
    {"name": "order_type", "type": "string", "description": "주문 방식 (limit/price/market)"},
    {"name": "status", "type": "string", "description": "주문 상태"},
    {"name": "created_at", "type": "string", "description": "주문 생성 시각"},
]


class BithumbNewOrderNode(BaseNode):
    """
    빗썸 신규 주문 노드

    빗썸 OpenAPI ``POST /v2/orders`` 로 코인 매수/매도 주문을 실행합니다.

    주문 방향(side):
    - ``bid``: 매수
    - ``ask``: 매도

    주문 방식(order_type):
    - ``limit``: 지정가 (price + volume 필수)
    - ``price``: 시장가 매수 (price = KRW 총액, volume 불필요)
    - ``market``: 시장가 매도 (volume = 수량, price 불필요)

    상위 BithumbBrokerNode 연결 필수.
    """

    type: Literal["BithumbNewOrderNode"] = "BithumbNewOrderNode"
    category: NodeCategory = NodeCategory.ORDER
    description: str = "i18n:nodes.BithumbNewOrderNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB

    _connection_rules: ClassVar[List[ConnectionRule]] = [
        ConnectionRule(
            deny_direct_from=REALTIME_SOURCE_NODE_TYPES,
            required_intermediate="ThrottleNode",
            severity=ConnectionSeverity.ERROR,
            reason="i18n:connection_rules.realtime_to_order.reason",
            suggestion="i18n:connection_rules.realtime_to_order.suggestion",
        ),
    ]

    _rate_limit: ClassVar[Optional[RateLimitConfig]] = RateLimitConfig(
        min_interval_sec=5,
        max_concurrent=1,
        on_throttle="skip",
    )

    connection: Optional[Dict] = Field(
        default=None,
        description="빗썸 연결 정보 (BithumbBrokerNode.connection 바인딩)",
    )

    side: Literal["bid", "ask"] = Field(
        default="bid",
        description="주문 방향 (bid: 매수, ask: 매도)",
    )
    order_type: Literal["limit", "price", "market"] = Field(
        default="limit",
        description="주문 방식 (limit: 지정가, price: 시장가 매수, market: 시장가 매도)",
    )
    order: Any = Field(
        default=None,
        description="주문 정보 {market, volume?, price?}",
    )

    resilience: ResilienceConfig = Field(
        default_factory=lambda: ResilienceConfig(
            retry=RetryConfig(enabled=False, retry_on=[RetryableError.NETWORK_ERROR]),
            fallback=FallbackConfig(mode=FallbackMode.ERROR),
        ),
        description="재시도 및 실패 처리 설정 (주문 노드는 기본 비활성화)",
    )

    @model_validator(mode="after")
    def _clamp_order_retry(self) -> "BithumbNewOrderNode":
        _MAX = 3
        if self.resilience.retry.enabled and self.resilience.retry.max_retries > _MAX:
            logging.getLogger("programgarden_core.order").warning(
                f"BithumbNewOrderNode max_retries → {_MAX}으로 제한 (중복 주문 방지)"
            )
            self.resilience.retry.max_retries = _MAX
        return self

    @classmethod
    def is_tool_enabled(cls) -> bool:
        return True

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "빗썸 코인 신규 매수/매도 주문 실행",
            "RSI 과매도 조건 충족 시 BTC 지정가 매수",
        ],
        "when_not_to_use": [
            "LS증권 주문 — OverseasStockNewOrderNode / KoreaStockNewOrderNode 사용",
        ],
        "typical_scenarios": [
            "ConditionNode (RSI<30) → BithumbNewOrderNode (bid, limit)",
            "BithumbAccountNode.balance → IfNode → BithumbNewOrderNode",
        ],
    }
    _features: ClassVar[List[str]] = [
        "지정가·시장가 매수·매도 지원 (bid/ask × limit/price/market)",
        "기본 재시도 비활성 — 중복 주문 위험 방지",
        "rate-limit: 최소 5초 간격, 동시 실행 1개",
        "is_tool_enabled=True — AI Agent 주문 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "실시간 노드를 ThrottleNode 없이 직접 BithumbNewOrderNode에 연결",
            "reason": "틱마다 주문이 발생하여 API rate-limit이 소진됩니다.",
            "alternative": "실시간 소스와 주문 노드 사이에 ThrottleNode를 삽입하세요.",
        },
        {
            "pattern": "order_type=price(시장가 매수)에 volume을 지정하거나 market(시장가 매도)에 price를 지정",
            "reason": "빗썸 규격상 price 주문은 KRW 총액(price)만, market 주문은 수량(volume)만 받습니다.",
            "alternative": "시장가 매수는 {market, price}, 시장가 매도는 {market, volume}, 지정가는 {market, price, volume}을 사용하세요.",
        },
        {
            "pattern": "주문 노드에 retry.max_retries를 크게 설정",
            "reason": "타임아웃 후 재시도가 중복 주문으로 이어질 수 있습니다.",
            "alternative": "기본값(재시도 비활성)을 유지하고, 실패는 fallback.mode=skip으로 처리하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "RSI 과매도 시장가 매수",
            "description": "RSI(14) 과매도 신호에 50,000 KRW 시장가 매수를 실행합니다.",
            "workflow_snippet": {
                "id": "bithumb-order-rsi-buy",
                "name": "RSI 시장가 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "candles", "type": "BithumbHistoricalDataNode", "market": "KRW-BTC", "count": 30},
                    {"id": "rsi", "type": "ConditionNode", "plugin": "RSI",
                     "items": {"from": "{{ nodes.candles.time_series }}",
                               "extract": {"symbol": "{{ item.symbol }}", "exchange": "{{ item.exchange }}",
                                           "date": "{{ row.candle_date_time_utc }}", "close": "{{ row.trade_price }}"}},
                     "fields": {"period": 14, "threshold": 30, "direction": "below"}},
                    {"id": "throttle", "type": "ThrottleNode", "min_interval_sec": 300},
                    {"id": "buy", "type": "BithumbNewOrderNode", "side": "bid", "order_type": "price",
                     "order": {"market": "{{ item.symbol }}", "price": "50000"},
                     "resilience": {"fallback": {"mode": "skip"}}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "candles"},
                    {"from": "candles", "to": "rsi"},
                    {"from": "rsi", "to": "throttle"},
                    {"from": "throttle", "to": "buy"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "result 포트에 {order_id, market, side, status, ...}가 반환됩니다.",
        },
        {
            "title": "지정가 매수 후 취소",
            "description": "체결 가능성이 낮은 지정가 매수를 넣고 곧바로 취소하는 주문 라이프사이클입니다.",
            "workflow_snippet": {
                "id": "bithumb-order-lifecycle",
                "name": "주문 라이프사이클",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "buy", "type": "BithumbNewOrderNode", "side": "bid", "order_type": "limit",
                     "order": {"market": "KRW-BTC", "volume": "0.0001", "price": "50000000"}},
                    {"id": "cancel", "type": "BithumbCancelOrderNode",
                     "original_order_id": "{{ nodes.buy.result.order_id }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "buy"},
                    {"from": "buy", "to": "cancel"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "매수 주문의 order_id가 취소 노드에 바인딩되어 미체결 주문이 취소됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "side(bid/ask)·order_type(limit/price/market)은 고정값, order는 {market, volume?, price?} 객체 — 바인딩으로 상위 노드 출력을 연결할 수 있습니다.",
        "output_consumption": "result.order_id를 BithumbCancelOrderNode.original_order_id에 바인딩해 취소 라이프사이클을 구성합니다.",
        "common_combinations": [
            "ConditionNode → ThrottleNode → BithumbNewOrderNode (지표 매매)",
            "BithumbNewOrderNode.result.order_id → BithumbCancelOrderNode (주문 취소)",
            "BithumbAccountNode.balance → IfNode → BithumbNewOrderNode (잔고 조건 주문)",
        ],
        "pitfalls": [
            "시장가 매수(price)는 수량이 아니라 KRW 총액을 price에 입력",
            "최소 주문 금액 5,000 KRW 미만은 거절됨",
            "rate-limit: 최소 5초 간격 — 짧은 주기 반복 주문은 on_throttle=skip으로 건너뜀",
            "기본 재시도 비활성 — 중복 주문 방지를 위해 유지 권장",
        ],
    }

    _inputs: List[InputPort] = [
        InputPort(name="trigger", type="signal", description="i18n:ports.order_trigger"),
        InputPort(name="order", type="order", description="i18n:ports.order_input", required=False),
    ]
    _outputs: List[OutputPort] = [
        OutputPort(
            name="result",
            type="order_result",
            description="i18n:ports.order_result",
            fields=COIN_ORDER_RESULT_FIELDS,
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
            "side": FieldSchema(
                name="side",
                type=FieldType.ENUM,
                description="i18n:fields.BithumbNewOrderNode.side",
                default="bid",
                enum_values=["bid", "ask"],
                enum_labels={
                    "bid": "i18n:enums.bithumb_side.bid",
                    "ask": "i18n:enums.bithumb_side.ask",
                },
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.PARAMETERS,
                expected_type="str",
                example="bid",
            ),
            "order_type": FieldSchema(
                name="order_type",
                type=FieldType.ENUM,
                description="i18n:fields.BithumbNewOrderNode.order_type",
                default="limit",
                enum_values=["limit", "price", "market"],
                enum_labels={
                    "limit": "i18n:enums.bithumb_order_type.limit",
                    "price": "i18n:enums.bithumb_order_type.price",
                    "market": "i18n:enums.bithumb_order_type.market",
                },
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.PARAMETERS,
                expected_type="str",
                example="limit",
            ),
            "order": FieldSchema(
                name="order",
                type=FieldType.OBJECT,
                display_name="i18n:fieldNames.BithumbNewOrderNode.order",
                description="i18n:fields.BithumbNewOrderNode.order",
                required=True,
                expression_mode=ExpressionMode.EXPRESSION_ONLY,
                category=FieldCategory.PARAMETERS,
                example={"market": "KRW-BTC", "volume": "0.001", "price": "50000000"},
                example_binding="{{ nodes.sizing.order }}",
                object_schema=[
                    {"name": "market", "type": "STRING", "required": True,
                     "label": "마켓 코드 (KRW-BTC 등)"},
                    {"name": "volume", "type": "STRING", "required": False,
                     "label": "주문 수량 (지정가/시장가 매도 시 필수)"},
                    {"name": "price", "type": "STRING", "required": False,
                     "label": "주문 가격 또는 KRW 총액 (지정가/시장가 매수 시 필수)"},
                ],
                expected_type="{market: str, volume?: str, price?: str}",
            ),
        }


class BithumbCancelOrderNode(BaseNode):
    """
    빗썸 주문 취소 노드

    빗썸 OpenAPI ``DELETE /v2/order`` 로 미체결 주문을 취소합니다.
    ``original_order_id`` 필드에 취소할 주문 ID를 바인딩하세요.

    상위 BithumbBrokerNode 연결 필수.
    """

    type: Literal["BithumbCancelOrderNode"] = "BithumbCancelOrderNode"
    category: NodeCategory = NodeCategory.ORDER
    description: str = "i18n:nodes.BithumbCancelOrderNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB

    _connection_rules: ClassVar[List[ConnectionRule]] = [
        ConnectionRule(
            deny_direct_from=REALTIME_SOURCE_NODE_TYPES,
            required_intermediate="ThrottleNode",
            severity=ConnectionSeverity.ERROR,
            reason="i18n:connection_rules.realtime_to_order.reason",
            suggestion="i18n:connection_rules.realtime_to_order.suggestion",
        ),
    ]

    _rate_limit: ClassVar[Optional[RateLimitConfig]] = RateLimitConfig(
        min_interval_sec=5,
        max_concurrent=1,
        on_throttle="skip",
    )

    connection: Optional[Dict] = Field(
        default=None,
        description="빗썸 연결 정보 (BithumbBrokerNode.connection 바인딩)",
    )

    original_order_id: Any = Field(
        default=None,
        description="취소할 빗썸 주문 ID",
    )

    resilience: ResilienceConfig = Field(
        default_factory=lambda: ResilienceConfig(
            retry=RetryConfig(enabled=False, retry_on=[RetryableError.NETWORK_ERROR]),
            fallback=FallbackConfig(mode=FallbackMode.ERROR),
        ),
        description="재시도 설정 (기본 비활성)",
    )

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "미체결 주문 취소",
            "전략 변경 시 기존 지정가 주문 취소",
        ],
        "when_not_to_use": [
            "이미 체결된 주문 — 취소 불가",
        ],
        "typical_scenarios": [
            "BithumbNewOrderNode.result.order_id → BithumbCancelOrderNode (주문 라이프사이클)",
            "TimerNode → BithumbCancelOrderNode (일정 시간 미체결 시 취소)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "original_order_id 바인딩으로 상위 주문 노드의 order_id를 직접 연결",
        "cancel_result·cancelled_order_id 두 포트 출력 — 후속 로직에서 취소 확인 가능",
        "rate-limit: 최소 5초 간격, 기본 재시도 비활성",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "BithumbBrokerNode 없이 BithumbCancelOrderNode 사용",
            "reason": "DELETE /v2/order 는 Private API — 인증 없이는 호출이 실패합니다.",
            "alternative": "워크플로우 시작부에 BithumbBrokerNode를 배치하세요.",
        },
        {
            "pattern": "주문 직후 지연 없이 즉시 취소",
            "reason": "주문이 거래소에 접수되기 전 취소 요청이 도달하면 '주문 없음' 오류가 날 수 있습니다.",
            "alternative": "DelayNode 등으로 1~2초 간격을 두거나 fallback.mode=skip으로 오류를 흡수하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "지정가 매수 후 취소",
            "description": "체결 가능성이 낮은 지정가 매수를 넣고 order_id를 바인딩해 취소합니다.",
            "workflow_snippet": {
                "id": "bithumb-cancel-lifecycle",
                "name": "주문 취소 라이프사이클",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "buy", "type": "BithumbNewOrderNode", "side": "bid", "order_type": "limit",
                     "order": {"market": "KRW-BTC", "volume": "0.0001", "price": "50000000"}},
                    {"id": "cancel", "type": "BithumbCancelOrderNode",
                     "original_order_id": "{{ nodes.buy.result.order_id }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "buy"},
                    {"from": "buy", "to": "cancel"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "cancel_result 포트에 취소된 주문 정보가, cancelled_order_id에 취소 주문 ID가 반환됩니다.",
        },
        {
            "title": "취소 결과 표시",
            "description": "취소 결과를 요약 카드로 확인합니다.",
            "workflow_snippet": {
                "id": "bithumb-cancel-display",
                "name": "취소 결과 확인",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "buy", "type": "BithumbNewOrderNode", "side": "bid", "order_type": "limit",
                     "order": {"market": "KRW-ETH", "volume": "0.001", "price": "1000000"}},
                    {"id": "cancel", "type": "BithumbCancelOrderNode",
                     "original_order_id": "{{ nodes.buy.result.order_id }}"},
                    {"id": "display", "type": "SummaryDisplayNode", "title": "취소 결과",
                     "data": "{{ nodes.cancel.cancel_result }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "buy"},
                    {"from": "buy", "to": "cancel"},
                    {"from": "cancel", "to": "display"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "취소된 주문의 상태·시각이 요약 카드로 표시됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "original_order_id에 취소할 주문 ID를 입력하거나 상위 주문 노드의 result.order_id를 바인딩합니다.",
        "output_consumption": "cancel_result는 취소 주문 상세 dict, cancelled_order_id는 취소된 주문 ID 문자열입니다.",
        "common_combinations": [
            "BithumbNewOrderNode → BithumbCancelOrderNode (주문 라이프사이클)",
            "BithumbCancelOrderNode → SummaryDisplayNode (취소 결과 확인)",
        ],
        "pitfalls": [
            "이미 전량 체결된 주문은 취소 불가 — 오류 응답",
            "취소도 rate-limit(5초) 적용 — 다건 취소는 간격을 둘 것",
            "부분 체결 주문은 미체결 잔량만 취소됨",
        ],
    }

    _inputs: List[InputPort] = [
        InputPort(name="trigger", type="signal", description="i18n:ports.cancel_trigger"),
        InputPort(name="original_order_id", type="string", description="i18n:ports.original_order_id"),
    ]
    _outputs: List[OutputPort] = [
        OutputPort(
            name="cancel_result",
            type="order_result",
            description="i18n:ports.cancel_result",
            fields=COIN_ORDER_RESULT_FIELDS,
        ),
        OutputPort(
            name="cancelled_order_id",
            type="string",
            description="i18n:ports.cancelled_order_id",
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
            "original_order_id": FieldSchema(
                name="original_order_id",
                type=FieldType.STRING,
                description="i18n:fields.BithumbCancelOrderNode.original_order_id",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="{{ nodes.order.result.order_id }}",
                example="C0101000000001799653",
                example_binding="{{ nodes.order.result.order_id }}",
                expected_type="str",
            ),
        }
