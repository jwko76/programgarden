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
    ]

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
    _updated_at: ClassVar[str] = "2026-06-19"
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
            "전략 변경 시 기존 지정가 주문 일괄 취소",
        ],
        "when_not_to_use": [
            "이미 체결된 주문 — 취소 불가",
        ],
        "typical_scenarios": [
            "BithumbOpenOrdersNode → BithumbCancelOrderNode (일괄 취소)",
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
    _updated_at: ClassVar[str] = "2026-06-19"
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
