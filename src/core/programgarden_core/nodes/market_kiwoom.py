"""
ProgramGarden Core - Kiwoom Market Data Node

키움증권 시세 조회:
- KiwoomMarketDataNode: 주식 현재가 REST 1회 조회 (api-id ka10001)
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

KIWOOM_PRICE_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리, 005930 등)"},
    {"name": "current_price", "type": "number", "description": "현재가(원)"},
    {"name": "change", "type": "number", "description": "전일 대비(원)"},
    {"name": "change_rate", "type": "number", "description": "전일 대비율(%)"},
    {"name": "open_price", "type": "number", "description": "당일 시가"},
    {"name": "high_price", "type": "number", "description": "당일 고가"},
    {"name": "low_price", "type": "number", "description": "당일 저가"},
    {"name": "volume", "type": "number", "description": "누적 거래량"},
    {"name": "trade_amount", "type": "number", "description": "누적 거래대금(원)"},
    {"name": "per", "type": "number", "description": "PER"},
    {"name": "pbr", "type": "number", "description": "PBR"},
]


class KiwoomMarketDataNode(BaseNode):
    """
    키움증권 주식 현재가 REST 1회 조회 노드

    키움 주식현재가 시세 api-id(ka10001)로 현재가를 조회합니다.
    빗썸 공개 API와 달리 키움 시세 조회도 appkey 인증이 필요하므로
    상위 KiwoomBrokerNode 연결이 필수입니다.

    ``symbols`` 필드에 종목코드를 콤마 구분으로 입력하세요 (ex. ``005930,000660``).
    여러 종목을 입력하면 각 종목에 대한 현재가가 반환됩니다.
    """

    type: Literal["KiwoomMarketDataNode"] = "KiwoomMarketDataNode"
    category: NodeCategory = NodeCategory.MARKET
    description: str = "i18n:nodes.KiwoomMarketDataNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIWOOM

    symbols: str = ""

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "국내주식 현재가·등락률·거래량 조회 (키움 계정)",
            "조건 노드에 데이터 공급 전 현재가 확인",
        ],
        "when_not_to_use": [
            "LS증권 계정의 시세 조회 — KoreaStockMarketDataNode 사용",
            "한국투자증권 계정의 시세 조회 — KisMarketDataNode 사용",
            "과거 일봉 데이터 — KiwoomHistoricalDataNode 사용",
        ],
        "typical_scenarios": [
            "KiwoomMarketDataNode → IfNode (current_price <= 60000 → 매수)",
            "KiwoomMarketDataNode → TableDisplayNode (현재가 대시보드)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "여러 종목코드 동시 조회 (콤마 구분)",
        "현재가·등락률·거래량·PER/PBR 등 주요 시세 필드 제공",
        "is_tool_enabled=True — AI Agent가 현재가 조회 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "KiwoomBrokerNode 없이 KiwoomMarketDataNode 단독 사용",
            "reason": "키움 시세 API도 appkey 인증이 필요합니다 (빗썸 공개 API와 다름).",
            "alternative": "워크플로우에 KiwoomBrokerNode를 먼저 배치하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "현재가 대시보드",
            "description": "삼성전자·SK하이닉스 현재가를 테이블로 표시합니다.",
            "workflow_snippet": {
                "id": "kiwoom-market-dashboard",
                "name": "키움 현재가 대시보드",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "market", "type": "KiwoomMarketDataNode", "symbols": "005930,000660"},
                    {"id": "display", "type": "TableDisplayNode", "title": "현재가",
                     "columns": ["symbol", "current_price", "change_rate", "volume"],
                     "data": "{{ nodes.market.values }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "market"},
                    {"from": "market", "to": "display"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "values 포트에 종목별 {symbol, current_price, change_rate, volume, ...} 배열이 반환되고 테이블에 표시됩니다.",
        },
        {
            "title": "가격 조건 매수 트리거",
            "description": "현재가가 목표가 이하로 내려오면 매수 주문을 실행합니다.",
            "workflow_snippet": {
                "id": "kiwoom-market-price-trigger",
                "name": "가격 조건 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "market", "type": "KiwoomMarketDataNode", "symbols": "005930"},
                    {"id": "gate", "type": "IfNode", "condition": "{{ nodes.market.values[0].current_price <= 60000 }}"},
                    {"id": "order", "type": "KiwoomNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "60000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "market"},
                    {"from": "market", "to": "gate"},
                    {"from": "gate", "to": "order", "condition": "true"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "현재가가 60,000원 이하면 지정가 매수 주문이 실행됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "symbols 필드에 6자리 종목코드를 콤마 구분으로 입력합니다. 브로커 연결은 자동 주입됩니다.",
        "output_consumption": "values 포트는 종목별 시세 dict 배열 — values[0].current_price 형태로 개별 필드를 참조합니다.",
        "common_combinations": [
            "KiwoomMarketDataNode → TableDisplayNode (시세 대시보드)",
            "KiwoomMarketDataNode → IfNode → KiwoomNewOrderNode (가격 조건 주문)",
            "ScheduleNode → KiwoomMarketDataNode (주기적 시세 수집)",
        ],
        "pitfalls": [
            "키움 시세 API도 appkey 인증 필요 — 빗썸과 달리 KiwoomBrokerNode 없이 사용 불가",
            "종목코드는 6자리 문자열 — 앞자리 0이 잘리지 않도록 문자열로 입력",
            "여러 종목 조회 시 종목당 REST 1회 호출 — rate-limit을 고려해 종목 수를 제한할 것",
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
            fields=KIWOOM_PRICE_FIELDS,
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
            "symbols": FieldSchema(
                name="symbols",
                type=FieldType.STRING,
                description="i18n:fields.KiwoomMarketDataNode.symbols",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="005930,000660",
                example="005930,000660",
                help_text="종목코드 6자리. 콤마(,)로 구분하여 여러 종목을 입력할 수 있습니다.",
            ),
        }
