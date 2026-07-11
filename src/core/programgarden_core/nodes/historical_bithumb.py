"""
ProgramGarden Core - Bithumb Historical Data Node

빗썸 캔들 조회 (분/일/주/월):
- BithumbHistoricalDataNode: GET /v1/candles/{minutes/{unit}|days|weeks|months} — RSI/Bollinger 등 지표 계산용
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
    빗썸 캔들 REST 조회 노드 (분/일/주/월)

    빗썸 공개 API ``GET /v1/candles/...`` 로 캔들 데이터를 조회합니다.
    ``interval`` 필드로 봉 종류를 선택합니다: ``day``(기본)/``week``/``month`` 또는
    분봉 ``1m``/``3m``/``5m``/``10m``/``15m``/``30m``/``60m``/``240m``.
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
    interval: Literal[
        "day", "week", "month",
        "1m", "3m", "5m", "10m", "15m", "30m", "60m", "240m",
    ] = "day"

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "RSI · Bollinger 등 지표 계산을 위한 일봉 OHLCV 데이터 수집",
            "89번 예제: RSI 과매도 BTC 자동매수 봇의 캔들 소스",
        ],
        "when_not_to_use": [
            "실시간 현재가 → BithumbMarketDataNode 사용",
        ],
        "typical_scenarios": [
            "BithumbHistoricalDataNode → ConditionNode(RSI, period=14, threshold=30)",
            "BithumbHistoricalDataNode → ConditionNode(BollingerBands) → ThrottleNode → BithumbNewOrderNode",
        ],
    }
    _features: ClassVar[List[str]] = [
        "공개 API — BithumbBrokerNode 없이 단독 사용 가능",
        "interval 필드로 분(1~240m)/일/주/월봉 선택 (기본 일봉)",
        "time_series 출력 포트: ConditionNode와 직결 (역순 자동 정렬)",
        "values 출력 포트: 원본 캔들 배열 (필드 직접 접근용)",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "values 포트를 ConditionNode items.from에 연결",
            "reason": "ConditionNode 플러그인은 [{symbol, exchange, time_series}] 형식을 기대합니다. values는 원본 캔들 배열이라 shape이 맞지 않습니다.",
            "alternative": "ConditionNode에는 time_series 포트를 연결하세요.",
        },
        {
            "pattern": "count를 지표 period보다 작게 설정 (예: RSI 14에 count 10)",
            "reason": "표본이 부족하면 지표가 계산되지 않거나 부정확합니다.",
            "alternative": "count는 period의 2배 이상 (RSI 14 → 30 권장)으로 설정하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "RSI 과매도 자동매수",
            "description": "일봉 30개로 RSI(14)를 계산해 과매도 시 소액 시장가 매수합니다.",
            "workflow_snippet": {
                "id": "bithumb-hist-rsi-buy",
                "name": "RSI 과매도 매수",
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
            "expected_output": "RSI(14)가 30 이하이면 50,000 KRW 시장가 매수가 실행됩니다 (5분당 최대 1회).",
        },
        {
            "title": "5분봉 캔들 테이블",
            "description": "최근 BTC 5분봉 캔들을 테이블로 표시합니다. 인증 없이 동작합니다.",
            "workflow_snippet": {
                "id": "bithumb-hist-candle-table",
                "name": "BTC 5분봉 조회",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "candles", "type": "BithumbHistoricalDataNode",
                     "market": "KRW-BTC", "count": 10, "interval": "5m"},
                    {"id": "display", "type": "TableDisplayNode", "title": "BTC 5분봉",
                     "columns": ["candle_date_time_utc", "opening_price", "high_price", "low_price", "trade_price"],
                     "data": "{{ nodes.candles.values }}"},
                ],
                "edges": [
                    {"from": "start", "to": "candles"},
                    {"from": "candles", "to": "display"},
                ],
            },
            "expected_output": "values 포트의 5분봉 캔들 10개가 OHLC 컬럼 테이블로 표시됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "market에 단일 마켓 코드(KRW-BTC), count에 캔들 수(1~200), interval에 봉 종류(day/week/month/1m~240m)를 지정합니다. 공개 API라 브로커 연결이 필수는 아닙니다.",
        "output_consumption": "지표 계산에는 time_series 포트([{symbol, exchange, time_series}])를 ConditionNode items.from에 연결합니다. 원본 캔들 필드 접근에는 values 포트를 사용합니다.",
        "common_combinations": [
            "BithumbHistoricalDataNode → ConditionNode(RSI/BollingerBands) → ThrottleNode → BithumbNewOrderNode",
            "BithumbHistoricalDataNode → TableDisplayNode (캔들 차트 데이터)",
            "ScheduleNode → BithumbHistoricalDataNode (주기적 재계산)",
        ],
        "pitfalls": [
            "API 원본은 최신-우선(newest-first) — executor가 ConditionNode용으로 자동 역순 정렬하므로 별도 처리 불필요",
            "market은 단일 코드만 — 여러 마켓은 노드를 복수 배치",
            "count 최대 200 — 그 이상 필요하면 to 파라미터 페이지네이션 (미지원, HTTPRequestNode 활용)",
            "분봉은 짧은 주기 폴링과 결합 시 rate-limit 주의 — ScheduleNode 주기를 봉 주기 이상으로 설정",
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

    _version: ClassVar[str] = "1.1.0"
    _updated_at: ClassVar[str] = "2026-07-12"
    _change_note: ClassVar[Optional[str]] = "interval 필드 추가 — 분(1m~240m)/일/주/월봉 지원"

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
                help_text="조회할 캔들 수 (1~200). RSI(14) 계산 시 최소 30 권장.",
            ),
            "interval": FieldSchema(
                name="interval",
                type=FieldType.ENUM,
                description="i18n:fields.BithumbHistoricalDataNode.interval",
                default="day",
                enum_values=[
                    "day", "week", "month",
                    "1m", "3m", "5m", "10m", "15m", "30m", "60m", "240m",
                ],
                enum_labels={
                    "day": "i18n:enums.bithumb_interval.day",
                    "week": "i18n:enums.bithumb_interval.week",
                    "month": "i18n:enums.bithumb_interval.month",
                    "1m": "i18n:enums.bithumb_interval.1m",
                    "3m": "i18n:enums.bithumb_interval.3m",
                    "5m": "i18n:enums.bithumb_interval.5m",
                    "10m": "i18n:enums.bithumb_interval.10m",
                    "15m": "i18n:enums.bithumb_interval.15m",
                    "30m": "i18n:enums.bithumb_interval.30m",
                    "60m": "i18n:enums.bithumb_interval.60m",
                    "240m": "i18n:enums.bithumb_interval.240m",
                },
                required=False,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.PARAMETERS,
                expected_type="str",
                example="day",
                help_text="봉 종류. day(일봉)/week(주봉)/month(월봉) 또는 분봉(1m~240m).",
            ),
        }
