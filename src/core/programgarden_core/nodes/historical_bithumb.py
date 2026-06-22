"""
ProgramGarden Core - Bithumb Historical Data Node

빗썸 일봉 캔들 조회:
- BithumbHistoricalDataNode: GET /v1/candles/days — RSI/Bollinger 등 지표 계산용
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

COIN_CANDLE_FIELDS: List[Dict[str, str]] = [
    {"name": "market", "type": "string", "description": "마켓 코드 (KRW-BTC 등)"},
    {"name": "candle_date_time_utc", "type": "string", "description": "캔들 기준 시각 (UTC, YYYY-MM-DDTHH:MM:SS)"},
    {"name": "opening_price", "type": "number", "description": "시가"},
    {"name": "high_price", "type": "number", "description": "고가"},
    {"name": "low_price", "type": "number", "description": "저가"},
    {"name": "trade_price", "type": "number", "description": "종가 (최종 체결가)"},
    {"name": "candle_acc_trade_volume", "type": "number", "description": "캔들 누적 거래량"},
    {"name": "candle_acc_trade_price", "type": "number", "description": "캔들 누적 거래금액(KRW)"},
]

# ConditionNode RSI/Bollinger 플러그인이 기대하는 time_series 형식
COIN_TIME_SERIES_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "마켓 코드 (ConditionNode items.extract 용)"},
    {"name": "exchange", "type": "string", "description": "거래소 식별자 (BITHUMB)"},
    {"name": "time_series", "type": "array", "description": "OHLCV 캔들 배열 (ConditionNode 전달용)"},
]


class BithumbHistoricalDataNode(BaseNode):
    """
    빗썸 일봉 캔들 REST 조회 노드

    빗썸 공개 API ``GET /v1/candles/days`` 로 일봉 데이터를 조회합니다.
    인증이 필요 없는 공개 API 이므로 BithumbBrokerNode 없이 사용 가능합니다.

    ``time_series`` 출력 포트는 ConditionNode(RSI/BollingerBands 등)에 바로 연결할 수 있는
    ``[{symbol, exchange, time_series: [...candles]}]`` 형식을 반환합니다.

    최신 캔들이 배열 앞쪽(인덱스 0)에 옵니다. ConditionNode 플러그인은 oldest-first를
    기대하므로 executor에서 자동으로 역순 정렬합니다.
    """

    type: Literal["BithumbHistoricalDataNode"] = "BithumbHistoricalDataNode"
    category: NodeCategory = NodeCategory.MARKET
    description: str = "i18n:nodes.BithumbHistoricalDataNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB
    _requires_broker: ClassVar[bool] = False  # 공개 API

    market: str = "KRW-BTC"
    count: int = 30

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "RSI · Bollinger 등 지표 계산을 위한 일봉 OHLCV 데이터 수집",
            "89번 예제: RSI 과매도 BTC 자동매수 봇의 캔들 소스",
        ],
        "when_not_to_use": [
            "실시간 현재가 → BithumbMarketDataNode 사용",
            "분봉/시봉 → HTTPRequestNode로 /v1/candles/minutes/{unit} 직접 호출",
        ],
        "typical_scenarios": [
            "BithumbHistoricalDataNode → ConditionNode(RSI, period=14, threshold=30)",
            "BithumbHistoricalDataNode → ConditionNode(BollingerBands) → ThrottleNode → BithumbNewOrderNode",
        ],
    }
    _features: ClassVar[List[str]] = [
        "공개 API — BithumbBrokerNode 없이 단독 사용 가능",
        "time_series 출력 포트: ConditionNode와 직결 (역순 자동 정렬)",
        "values 출력 포트: 원본 캔들 배열 (필드 직접 접근용)",
    ]

    @classmethod
    def is_tool_enabled(cls) -> bool:
        return True

    _inputs: List[InputPort] = [
        InputPort(name="trigger", type="signal", description="i18n:ports.trigger", required=False),
    ]
    _outputs: List[OutputPort] = [
        OutputPort(
            name="time_series",
            type="symbol_series",
            description="i18n:ports.time_series",
            fields=COIN_TIME_SERIES_FIELDS,
        ),
        OutputPort(
            name="values",
            type="candle_data",
            description="i18n:ports.values",
            fields=COIN_CANDLE_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-06-22"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        from programgarden_core.models.field_binding import (
            FieldSchema, FieldType, FieldCategory, ExpressionMode
        )
        return {
            "market": FieldSchema(
                name="market",
                type=FieldType.STRING,
                description="i18n:fields.BithumbHistoricalDataNode.market",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="KRW-BTC",
                example="KRW-BTC",
                help_text="빗썸 마켓 코드. 예: KRW-BTC, KRW-ETH",
            ),
            "count": FieldSchema(
                name="count",
                type=FieldType.NUMBER,
                description="i18n:fields.BithumbHistoricalDataNode.count",
                required=False,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                default=30,
                example=30,
                help_text="조회할 일봉 수 (1~200). RSI(14) 계산 시 최소 30 권장.",
            ),
        }
