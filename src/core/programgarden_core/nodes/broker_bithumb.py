"""
ProgramGarden Core - Bithumb Broker Node

빗썸(Bithumb) 거래소 연결 노드:
- BithumbBrokerNode: 빗썸 API Access Key/Secret Key 인증 게이트웨이
"""

from typing import Optional, List, Literal, Dict, ClassVar, Any, TYPE_CHECKING
from pydantic import Field

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


class BithumbBrokerNode(BaseNode):
    """
    빗썸(Bithumb) 거래소 연결 노드

    빗썸 OpenAPI v2.1.5를 통해 코인 거래를 위한 연결을 생성합니다.
    인증 게이트웨이 역할 — 하위 계좌, 시세, 주문 노드가 DAG 순회를 통해
    자동으로 브로커 연결을 상속합니다.

    credential_id로 ``broker_bithumb`` 인증 정보(access_key + secret_key)를 참조합니다.
    LS증권과 달리 OAuth 토큰이 없으며 요청마다 JWT를 생성합니다.
    """

    type: Literal["BithumbBrokerNode"] = "BithumbBrokerNode"
    description: str = "i18n:nodes.BithumbBrokerNode.description"

    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB

    category: NodeCategory = NodeCategory.INFRA

    provider: str = Field(default="bithumb.com", description="거래소 제공자")
    credential_id: Optional[str] = Field(
        default=None, description="빗썸 인증정보 참조 (broker_bithumb 타입)"
    )

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "모든 빗썸 코인 거래 워크플로우의 시작점",
            "BithumbAccountNode / BithumbMarketDataNode / BithumbNewOrderNode 앞에 반드시 배치",
        ],
        "when_not_to_use": [
            "LS증권 거래 워크플로우 — OverseasStockBrokerNode / KoreaStockBrokerNode 사용",
            "인증이 불필요한 공개 API만 쓰는 경우 (단, BithumbMarketDataNode는 인증 불필요)",
        ],
        "typical_scenarios": [
            "StartNode → BithumbBrokerNode → BithumbAccountNode → TableDisplayNode",
            "StartNode → BithumbBrokerNode → BithumbNewOrderNode (RSI 기반 BTC 매수)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "빗썸 API access_key/secret_key로 인증 — 요청마다 HS256 JWT 자동 생성",
        "connection 출력은 하위 모든 빗썸 노드에 DAG 자동 주입 — 명시적 바인딩 불필요",
        "credential_types=['broker_bithumb'] 으로 올바른 인증 정보만 선택됨",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "BithumbBrokerNode 없이 BithumbAccountNode / BithumbNewOrderNode 사용",
            "reason": "인증 정보가 없어 모든 Private API 호출이 실패합니다.",
            "alternative": "항상 BithumbBrokerNode를 DAG 시작부에 배치하세요.",
        },
        {
            "pattern": "하위 노드에 connection을 수동으로 바인딩",
            "reason": "connection은 DAG 순회로 자동 주입되므로 수동 바인딩은 불필요하고 오타 위험만 늘립니다.",
            "alternative": "엣지로 연결만 하면 됩니다 — 바인딩 없이 자동 상속됩니다.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "빗썸 계좌 잔고 조회",
            "description": "브로커 연결 후 KRW 잔고와 보유 코인을 테이블로 표시합니다.",
            "workflow_snippet": {
                "id": "bithumb-broker-account",
                "name": "빗썸 계좌 조회",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "account", "type": "BithumbAccountNode"},
                    {"id": "display", "type": "TableDisplayNode", "title": "보유 코인",
                     "columns": ["market", "balance", "avg_buy_price"],
                     "data": "{{ nodes.account.positions }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "display"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "connection이 BithumbAccountNode에 자동 주입되어 보유 코인 테이블이 표시됩니다.",
        },
        {
            "title": "RSI 과매도 자동매수 진입점",
            "description": "브로커 연결 → 일봉 → RSI 조건 → 시장가 매수 파이프라인의 인증 게이트웨이.",
            "workflow_snippet": {
                "id": "bithumb-broker-rsi-buy",
                "name": "빗썸 RSI 매수",
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
                     "order": {"market": "{{ item.symbol }}", "price": "50000"}},
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
            "expected_output": "RSI(14)가 30 이하로 떨어지면 5분당 최대 1회 50,000 KRW 시장가 매수가 실행됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "입력 포트가 없는 인프라 노드 — StartNode 바로 뒤 DAG 시작부에 배치하고 credential_id에 broker_bithumb 타입 인증 정보를 지정합니다.",
        "output_consumption": "connection 포트는 하위 모든 빗썸 노드에 자동 주입됩니다. 명시적 바인딩 없이 엣지 연결만으로 상속됩니다.",
        "common_combinations": [
            "StartNode → BithumbBrokerNode → BithumbAccountNode (잔고 조회)",
            "BithumbBrokerNode → BithumbHistoricalDataNode → ConditionNode → BithumbNewOrderNode (지표 매매)",
            "BithumbBrokerNode → ScheduleNode → 하위 노드 (주기 실행)",
        ],
        "pitfalls": [
            "BithumbMarketDataNode / BithumbHistoricalDataNode는 공개 API라 브로커 없이도 동작 — Account/Order 노드만 인증 필수",
            "빗썸은 OAuth 토큰이 없고 요청마다 JWT 생성 — 별도 토큰 만료 처리 불필요",
            "같은 워크플로우에 LS/KIS 브로커와 공존 가능 (product_scope가 COIN으로 분리됨)",
        ],
    }

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-11"

    _inputs: List[InputPort] = []
    _outputs: List[OutputPort] = [
        OutputPort(
            name="connection",
            type="broker_connection",
            description="i18n:ports.connection",
            example={"_opaque": True, "provider": "bithumb.com"},
        )
    ]

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        from programgarden_core.models.field_binding import (
            FieldSchema, FieldType, FieldCategory, ExpressionMode
        )
        return {
            "credential_id": FieldSchema(
                name="credential_id",
                type=FieldType.CREDENTIAL,
                description="i18n:fields.BithumbBrokerNode.credential_id",
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.SETTINGS,
                credential_types=["broker_bithumb"],
                example="my-bithumb-api",
            ),
        }
