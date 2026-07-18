"""
ProgramGarden Core - Kiwoom Order Nodes

키움증권 주문 노드:
- KiwoomNewOrderNode: 현금 신규 주문 (api-id kt10000 매수 / kt10001 매도)
- KiwoomCancelOrderNode: 주문 취소 (api-id kt10003)

KIS와 달리 키움은 정정(kt10002)과 취소(kt10003)가 별개 api-id로 분리되어
있습니다. 이 레이어는 KIS와 동일하게 취소 전용 노드만 제공합니다(정정
노드는 MVP 범위 밖).
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

KIWOOM_ORDER_RESULT_FIELDS: List[Dict[str, str]] = [
    {"name": "order_no", "type": "string", "description": "키움 주문번호"},
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리)"},
    {"name": "side", "type": "string", "description": "주문 방향 (buy/sell)"},
    {"name": "order_type", "type": "string", "description": "주문 방식 (limit/market)"},
    {"name": "quantity", "type": "number", "description": "주문 수량"},
    {"name": "price", "type": "number", "description": "주문 가격(원, 시장가는 0)"},
    {"name": "order_time", "type": "string", "description": "주문 시각 (HHMMSS)"},
    {"name": "paper_trading", "type": "boolean", "description": "모의투자 여부"},
]


class KiwoomNewOrderNode(BaseNode):
    """
    키움증권 현금 신규 주문 노드

    키움 주식 현금매수(api-id kt10000)/현금매도(api-id kt10001) TR로
    국내주식 매수/매도 주문을 실행합니다. 키움은 KIS의 TTTC/VTTC 같은
    tr_id 분기가 아니라, 브로커의 paper_trading 설정에 따라 접속
    도메인(api.kiwoom.com / mockapi.kiwoom.com) 자체가 전환됩니다 —
    api-id는 실전/모의 공용입니다.

    주문 방향(side):
    - ``buy``: 매수
    - ``sell``: 매도

    주문 방식(order_type):
    - ``limit``: 지정가 (price 필수)
    - ``market``: 시장가 (price 불필요)

    상위 KiwoomBrokerNode 연결 필수.
    """

    type: Literal["KiwoomNewOrderNode"] = "KiwoomNewOrderNode"
    category: NodeCategory = NodeCategory.ORDER
    description: str = "i18n:nodes.KiwoomNewOrderNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIWOOM

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
        description="키움 연결 정보 (KiwoomBrokerNode.connection 바인딩)",
    )

    side: Literal["buy", "sell"] = Field(
        default="buy",
        description="주문 방향 (buy: 매수, sell: 매도)",
    )
    order_type: Literal["limit", "market"] = Field(
        default="limit",
        description="주문 방식 (limit: 지정가, market: 시장가)",
    )
    order: Any = Field(
        default=None,
        description="주문 정보 {symbol, quantity, price?}",
    )

    resilience: ResilienceConfig = Field(
        default_factory=lambda: ResilienceConfig(
            retry=RetryConfig(enabled=False, retry_on=[RetryableError.NETWORK_ERROR]),
            fallback=FallbackConfig(mode=FallbackMode.ERROR),
        ),
        description="재시도 및 실패 처리 설정 (주문 노드는 기본 비활성화)",
    )

    @model_validator(mode="after")
    def _clamp_order_retry(self) -> "KiwoomNewOrderNode":
        _MAX = 3
        if self.resilience.retry.enabled and self.resilience.retry.max_retries > _MAX:
            logging.getLogger("programgarden_core.order").warning(
                f"KiwoomNewOrderNode max_retries → {_MAX}으로 제한 (중복 주문 방지)"
            )
            self.resilience.retry.max_retries = _MAX
        return self

    @classmethod
    def is_tool_enabled(cls) -> bool:
        return True

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "키움증권 계정으로 국내주식 신규 매수/매도 주문 실행",
            "RSI 과매도 조건 충족 시 지정가 매수",
        ],
        "when_not_to_use": [
            "LS증권 주문 — KoreaStockNewOrderNode 사용",
            "한국투자증권 주문 — KisNewOrderNode 사용",
            "빗썸 코인 주문 — BithumbNewOrderNode 사용",
        ],
        "typical_scenarios": [
            "ConditionNode (RSI<30) → ThrottleNode → KiwoomNewOrderNode (buy, limit)",
            "KiwoomAccountNode.balance → IfNode → KiwoomNewOrderNode",
        ],
    }
    _features: ClassVar[List[str]] = [
        "지정가·시장가 매수·매도 지원 (buy/sell × limit/market)",
        "브로커 paper_trading에 따라 접속 도메인이 자동 전환 (api-id는 실전/모의 공용, KIS의 TTTC↔VTTC 분기와 다름)",
        "기본 재시도 비활성 — 중복 주문 위험 방지",
        "rate-limit: 최소 5초 간격, 동시 실행 1개",
        "is_tool_enabled=True — AI Agent 주문 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "실시간 노드를 ThrottleNode 없이 직접 KiwoomNewOrderNode에 연결",
            "reason": "틱마다 주문이 발생하여 API rate-limit이 소진됩니다.",
            "alternative": "실시간 소스와 주문 노드 사이에 ThrottleNode를 삽입하세요.",
        },
        {
            "pattern": "검증되지 않은 전략을 paper_trading=False 브로커로 실행",
            "reason": "실계좌에 실제 주문이 전송됩니다.",
            "alternative": "KiwoomBrokerNode의 paper_trading=True로 모의투자에서 먼저 검증하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "모의투자 지정가 매수",
            "description": "모의투자 서버에서 삼성전자 10주를 지정가로 매수합니다.",
            "workflow_snippet": {
                "id": "kiwoom-order-paper-buy",
                "name": "키움 모의 지정가 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "order", "type": "KiwoomNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "60000"}},
                    {"id": "display", "type": "SummaryDisplayNode", "title": "주문 결과", "data": "{{ nodes.order.result }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "order"},
                    {"from": "order", "to": "display"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "result 포트에 {order_no, symbol, side, quantity, price, paper_trading: true} 주문 접수 결과가 반환됩니다.",
        },
        {
            "title": "가격 조건 시장가 매도",
            "description": "현재가가 손절 기준 이하로 내려오면 시장가로 매도합니다.",
            "workflow_snippet": {
                "id": "kiwoom-order-stop-sell",
                "name": "키움 손절 매도",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "market", "type": "KiwoomMarketDataNode", "symbols": "005930"},
                    {"id": "gate", "type": "IfNode", "condition": "{{ nodes.market.values[0].current_price <= 55000 }}"},
                    {"id": "sell", "type": "KiwoomNewOrderNode", "side": "sell", "order_type": "market",
                     "order": {"symbol": "005930", "quantity": "10"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "market"},
                    {"from": "market", "to": "gate"},
                    {"from": "gate", "to": "sell", "condition": "true"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "현재가가 55,000원 이하일 때만 시장가 매도 주문이 실행됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "side(buy/sell), order_type(limit/market), order({symbol, quantity, price?})를 설정합니다. 시장가는 price를 생략합니다. 브로커 연결은 자동 주입됩니다.",
        "output_consumption": "result.order_no를 KiwoomCancelOrderNode의 original_order_no에 바인딩해 취소 흐름을 구성합니다.",
        "common_combinations": [
            "ConditionNode → ThrottleNode → KiwoomNewOrderNode (지표 기반 매매)",
            "KiwoomAccountNode.balance → IfNode → KiwoomNewOrderNode (잔고 게이트)",
            "KiwoomNewOrderNode.result.order_no → KiwoomCancelOrderNode (주문 후 조건부 취소)",
        ],
        "pitfalls": [
            "실전/모의는 접속 도메인 전환으로 처리되며 api-id(kt10000/kt10001)는 그대로 사용됨 — KIS의 TTTC/VTTC 수동 지정과 혼동하지 말 것",
            "재시도 기본 비활성 — 활성화해도 중복 주문 방지를 위해 max_retries는 3으로 제한됨",
            "지정가 주문의 price는 호가단위에 맞아야 함",
            "실시간 소스에서 직접 연결 금지 — ThrottleNode 필수 (connection rule로 강제됨)",
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
            fields=KIWOOM_ORDER_RESULT_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-18"
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
                description="i18n:fields.KiwoomNewOrderNode.side",
                default="buy",
                enum_values=["buy", "sell"],
                enum_labels={
                    "buy": "i18n:enums.kiwoom_side.buy",
                    "sell": "i18n:enums.kiwoom_side.sell",
                },
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.PARAMETERS,
                expected_type="str",
                example="buy",
            ),
            "order_type": FieldSchema(
                name="order_type",
                type=FieldType.ENUM,
                description="i18n:fields.KiwoomNewOrderNode.order_type",
                default="limit",
                enum_values=["limit", "market"],
                enum_labels={
                    "limit": "i18n:enums.kiwoom_order_type.limit",
                    "market": "i18n:enums.kiwoom_order_type.market",
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
                display_name="i18n:fieldNames.KiwoomNewOrderNode.order",
                description="i18n:fields.KiwoomNewOrderNode.order",
                required=True,
                expression_mode=ExpressionMode.EXPRESSION_ONLY,
                category=FieldCategory.PARAMETERS,
                example={"symbol": "005930", "quantity": "10", "price": "60000"},
                example_binding="{{ nodes.sizing.order }}",
                object_schema=[
                    {"name": "symbol", "type": "STRING", "required": True,
                     "label": "종목코드 6자리 (005930 등)"},
                    {"name": "quantity", "type": "STRING", "required": True,
                     "label": "주문 수량"},
                    {"name": "price", "type": "STRING", "required": False,
                     "label": "주문 가격(원) — 지정가 필수, 시장가 생략"},
                ],
                expected_type="{symbol: str, quantity: str, price?: str}",
            ),
        }


class KiwoomCancelOrderNode(BaseNode):
    """
    키움증권 주문 취소 노드

    키움 주식 정정취소 api-id 중 취소 전용(kt10003)으로 미체결 주문을
    전량 취소합니다. KIS는 하나의 정정취소 TR을 플래그로 구분하지만,
    키움은 정정(kt10002)과 취소(kt10003)가 서로 다른 api-id로 분리되어
    있습니다 — 이 노드는 KIS의 KisCancelOrderNode와 동일하게 취소
    전용 범위만 제공하며, 정정 노드는 MVP 범위 밖입니다.

    ``original_order_no`` 필드에 취소할 주문번호를 바인딩하세요.

    상위 KiwoomBrokerNode 연결 필수. (정정 기능은 미지원 — 취소 전용)
    """

    type: Literal["KiwoomCancelOrderNode"] = "KiwoomCancelOrderNode"
    category: NodeCategory = NodeCategory.ORDER
    description: str = "i18n:nodes.KiwoomCancelOrderNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIWOOM

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
        description="키움 연결 정보 (KiwoomBrokerNode.connection 바인딩)",
    )

    original_order_no: Any = Field(
        default=None,
        description="취소할 키움 주문번호",
    )
    quantity: Any = Field(
        default=None,
        description="취소 수량 (생략 시 전량 취소)",
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
            "주문 수량·가격 변경 — 정정(kt10002)은 이 레이어에서 미지원, 취소 후 재주문하세요",
        ],
        "typical_scenarios": [
            "KiwoomNewOrderNode.result.order_no → KiwoomCancelOrderNode (조건부 취소)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "취소 전용 api-id(kt10003) 사용 — 키움은 정정(kt10002)과 취소가 분리되어 있음",
        "quantity 생략 시 잔량 전부 취소",
        "기본 재시도 비활성 — 이미 취소된 주문에 대한 중복 취소 방지",
        "rate-limit: 최소 5초 간격, 동시 실행 1개",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "체결 완료된 주문을 취소 시도",
            "reason": "키움이 에러를 반환하며, fallback.mode=error(기본)면 워크플로우가 중단됩니다.",
            "alternative": "취소 전 미체결 여부를 확인하거나 fallback.mode='skip'으로 설정하세요.",
        },
        {
            "pattern": "주문 정정 용도로 취소-재주문 없이 사용",
            "reason": "이 노드는 취소 전용입니다 (정정 api-id kt10002는 미지원).",
            "alternative": "취소 후 KiwoomNewOrderNode로 재주문하세요.",
        },
    ]
    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "주문 후 즉시 취소 (라이프사이클 테스트)",
            "description": "모의투자에서 지정가 매수 주문을 넣고 바로 취소합니다.",
            "workflow_snippet": {
                "id": "kiwoom-cancel-lifecycle",
                "name": "키움 주문-취소 라이프사이클",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "order", "type": "KiwoomNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "50000"}},
                    {"id": "cancel", "type": "KiwoomCancelOrderNode",
                     "original_order_no": "{{ nodes.order.result.order_no }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "order"},
                    {"from": "order", "to": "cancel"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "cancel_result에 취소 접수 결과, cancelled_order_no에 취소된 주문번호가 반환됩니다.",
        },
        {
            "title": "일부 수량만 취소",
            "description": "미체결 주문에서 5주만 취소하고 나머지는 유지합니다.",
            "workflow_snippet": {
                "id": "kiwoom-cancel-partial",
                "name": "키움 부분 취소",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "order", "type": "KiwoomNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "50000"}},
                    {"id": "cancel", "type": "KiwoomCancelOrderNode",
                     "original_order_no": "{{ nodes.order.result.order_no }}",
                     "quantity": "5"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "order"},
                    {"from": "order", "to": "cancel"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "5주가 취소되고 5주는 미체결 상태로 유지됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "original_order_no에 취소할 주문번호를 바인딩합니다. quantity 생략 시 전량 취소. 브로커 연결은 자동 주입됩니다.",
        "output_consumption": "cancel_result(취소 접수 dict)와 cancelled_order_no(문자열)를 하위 노드에서 참조합니다.",
        "common_combinations": [
            "KiwoomNewOrderNode.result.order_no → KiwoomCancelOrderNode (조건부 취소)",
            "ScheduleNode → KiwoomCancelOrderNode (장 마감 전 미체결 정리)",
        ],
        "pitfalls": [
            "이미 체결/취소된 주문의 취소는 키움 에러 반환 — fallback.mode로 처리 방침을 정할 것",
            "취소도 주문 api — rate-limit(최소 5초 간격)이 적용됨",
            "모의투자에서는 체결 시뮬레이션 속도가 빨라 취소 시점에 이미 체결됐을 수 있음",
        ],
    }

    _inputs: List[InputPort] = [
        InputPort(name="trigger", type="signal", description="i18n:ports.cancel_trigger"),
        InputPort(name="original_order_no", type="string", description="i18n:ports.original_order_id"),
    ]
    _outputs: List[OutputPort] = [
        OutputPort(
            name="cancel_result",
            type="order_result",
            description="i18n:ports.cancel_result",
            fields=KIWOOM_ORDER_RESULT_FIELDS,
        ),
        OutputPort(
            name="cancelled_order_no",
            type="string",
            description="i18n:ports.cancelled_order_id",
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-18"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        from programgarden_core.models.field_binding import (
            FieldSchema, FieldType, FieldCategory, ExpressionMode
        )
        return {
            "original_order_no": FieldSchema(
                name="original_order_no",
                type=FieldType.STRING,
                description="i18n:fields.KiwoomCancelOrderNode.original_order_no",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="{{ nodes.order.result.order_no }}",
                example="0001234567",
                example_binding="{{ nodes.order.result.order_no }}",
                expected_type="str",
            ),
            "quantity": FieldSchema(
                name="quantity",
                type=FieldType.STRING,
                description="i18n:fields.KiwoomCancelOrderNode.quantity",
                required=False,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="10",
                example="10",
                help_text="취소할 수량. 생략하면 잔량 전부를 취소합니다.",
                expected_type="str",
            ),
        }
