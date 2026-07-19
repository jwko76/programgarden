"""
ProgramGarden Core - Kiwoom Historical Data Node

키움증권 일봉 조회:
- KiwoomHistoricalDataNode: 국내주식 기간별 시세 (api-id ka10081) — RSI/Bollinger 등 지표 계산용
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

KIWOOM_CANDLE_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리)"},
    {"name": "date", "type": "string", "description": "영업일자 (YYYYMMDD)"},
    {"name": "open", "type": "number", "description": "시가"},
    {"name": "high", "type": "number", "description": "고가"},
    {"name": "low", "type": "number", "description": "저가"},
    {"name": "close", "type": "number", "description": "종가"},
    {"name": "volume", "type": "number", "description": "누적 거래량"},
]

# ConditionNode RSI/Bollinger 플러그인이 기대하는 time_series 형식
KIWOOM_TIME_SERIES_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (ConditionNode items.extract 용)"},
    {"name": "exchange", "type": "string", "description": "거래소 식별자 (KRX)"},
    {"name": "time_series", "type": "array", "description": "OHLCV 캔들 배열 (ConditionNode 전달용)"},
]


class KiwoomHistoricalDataNode(BaseNode):
    """
    키움증권 일봉 REST 조회 노드

    키움 주식일봉차트조회 api-id(ka10081)로 일봉 데이터를 조회합니다.
    상위 KiwoomBrokerNode 연결 필수.

    ``time_series`` 출력 포트는 ConditionNode(RSI/BollingerBands 등)에 바로 연결할 수 있는
    ``[{symbol, exchange, time_series: [...candles]}]`` 형식을 반환합니다.

    키움 응답은 최신 캔들이 배열 앞쪽에 옵니다. ConditionNode 플러그인은 oldest-first를
    기대하므로 executor에서 자동으로 역순 정렬합니다.
    """

    type: Literal["KiwoomHistoricalDataNode"] = "KiwoomHistoricalDataNode"
    category: NodeCategory = NodeCategory.MARKET
    description: str = "i18n:nodes.KiwoomHistoricalDataNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIWOOM

    symbol: str = "005930"
    count: int = 30

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "RSI · Bollinger 등 지표 계산을 위한 일봉 OHLCV 데이터 수집 (키움 계정)",
            "지표 기반 자동매매 봇의 캔들 소스",
        ],
        "when_not_to_use": [
            "실시간 현재가 → KiwoomMarketDataNode 사용",
            "LS증권 계정의 일봉 조회 — KoreaStockHistoricalDataNode 계열 사용",
            "한국투자증권 계정의 일봉 조회 — KisHistoricalDataNode 사용",
        ],
        "typical_scenarios": [
            "KiwoomHistoricalDataNode → ConditionNode(RSI, period=14, threshold=30)",
            "KiwoomHistoricalDataNode → ConditionNode(BollingerBands) → ThrottleNode → KiwoomNewOrderNode",
        ],
    }
    _features: ClassVar[List[str]] = [
        "time_series 출력 포트: ConditionNode와 직결 (역순 자동 정렬)",
        "values 출력 포트: 원본 캔들 배열 (필드 직접 접근용)",
        "브로커의 paper_trading 설정과 무관하게 실전 시세 데이터 제공",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "count를 지표 기간보다 작게 설정 (예: RSI(14)에 count=10)",
            "reason": "지표 계산에 필요한 캔들이 부족해 ConditionNode가 빈 결과를 반환합니다.",
            "alternative": "RSI(14)면 count>=30, Bollinger(20)면 count>=40을 권장합니다.",
        },
        {
            "pattern": "실시간 현재가 용도로 사용",
            "reason": "일봉 데이터는 당일 종가 확정 전까지 미완성 캔들입니다.",
            "alternative": "현재가는 KiwoomMarketDataNode를 사용하세요.",
        },
    ]
    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "RSI 과매도 매수 봇",
            "description": "삼성전자 일봉으로 RSI를 계산해 과매도(RSI<30) 시 매수합니다.",
            "workflow_snippet": {
                "id": "kiwoom-historical-rsi-bot",
                "name": "키움 RSI 매수 봇",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "candles", "type": "KiwoomHistoricalDataNode", "symbol": "005930", "count": 30},
                    {"id": "rsi", "type": "ConditionNode", "plugin": "RSI",
                     "items": {"from": "{{ nodes.candles.time_series }}",
                               "extract": {"symbol": "{{ item.symbol }}", "exchange": "{{ item.exchange }}",
                                           "date": "{{ row.date }}", "close": "{{ row.close }}"}},
                     "fields": {"period": 14, "threshold": 30, "direction": "below"}},
                    {"id": "throttle", "type": "ThrottleNode", "min_interval_sec": 300},
                    {"id": "order", "type": "KiwoomNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "60000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "candles"},
                    {"from": "candles", "to": "rsi"},
                    {"from": "rsi", "to": "throttle"},
                    {"from": "throttle", "to": "order"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "RSI가 30 미만이면 매수 신호가 발생하고 ThrottleNode를 거쳐 지정가 매수 주문이 실행됩니다.",
        },
        {
            "title": "일봉 캔들 차트",
            "description": "최근 60일 일봉을 캔들 차트로 표시합니다.",
            "workflow_snippet": {
                "id": "kiwoom-historical-chart",
                "name": "키움 일봉 차트",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "candles", "type": "KiwoomHistoricalDataNode", "symbol": "005930", "count": 60},
                    {"id": "chart", "type": "CandlestickChartNode", "title": "삼성전자 일봉",
                     "data": "{{ nodes.candles.values }}",
                     "time_field": "date", "open_field": "open", "high_field": "high",
                     "low_field": "low", "close_field": "close"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "candles"},
                    {"from": "candles", "to": "chart"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "values 포트의 OHLCV 배열이 캔들 차트로 렌더링됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "symbol(6자리 종목코드)과 count(일봉 수)를 설정합니다. 브로커 연결은 자동 주입됩니다.",
        "output_consumption": "time_series 포트는 ConditionNode의 items에 바로 바인딩하고, values 포트는 차트·테이블에 사용합니다.",
        "common_combinations": [
            "KiwoomHistoricalDataNode → ConditionNode(RSI/BollingerBands) → ThrottleNode → KiwoomNewOrderNode",
            "KiwoomHistoricalDataNode → CandlestickChartNode (일봉 차트)",
            "ScheduleNode → KiwoomHistoricalDataNode (장 마감 후 일봉 갱신)",
        ],
        "pitfalls": [
            "키움 일봉차트 api-id는 1회 조회건수 제한이 있음 — count가 클수록 응답이 잘릴 수 있음",
            "time_series는 oldest-first로 자동 정렬됨 — values는 키움 원본 순서(최신 먼저)",
            "휴장일은 캔들이 없으므로 count와 실제 반환 캔들 수가 다를 수 있음",
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
            fields=KIWOOM_TIME_SERIES_FIELDS,
        ),
        OutputPort(
            name="values",
            type="candle_data",
            description="i18n:ports.values",
            fields=KIWOOM_CANDLE_FIELDS,
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
            "symbol": FieldSchema(
                name="symbol",
                type=FieldType.STRING,
                description="i18n:fields.KiwoomHistoricalDataNode.symbol",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="005930",
                example="005930",
                help_text="종목코드 6자리. 예: 005930(삼성전자), 000660(SK하이닉스)",
            ),
            "count": FieldSchema(
                name="count",
                type=FieldType.NUMBER,
                description="i18n:fields.KiwoomHistoricalDataNode.count",
                required=False,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                default=30,
                example=30,
                help_text="조회할 일봉 수 (1~100). RSI(14) 계산 시 최소 30 권장.",
            ),
        }
