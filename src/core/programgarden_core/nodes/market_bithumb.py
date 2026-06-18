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
    _updated_at: ClassVar[str] = "2026-06-19"
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
