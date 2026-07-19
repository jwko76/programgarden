"""
ProgramGarden Core - KIS Account Node

한국투자증권 계좌 조회:
- KisAccountNode: 주식 잔고·예수금 REST 1회 조회 (TTTC8434R/VTTC8434R)
- KisOrderableAmountNode: 매수가능조회 (TTTC8908R/VTTC8908R)
"""

from typing import Any, ClassVar, Dict, List, Literal, Optional, TYPE_CHECKING

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

KIS_BALANCE_FIELDS: List[Dict[str, str]] = [
    {"name": "deposit", "type": "number", "description": "예수금 총액(원)"},
    {"name": "orderable_amount", "type": "number", "description": "주문 가능 현금(원)"},
    {"name": "total_evaluation", "type": "number", "description": "총 평가 금액(원)"},
    {"name": "total_purchase", "type": "number", "description": "매입 금액 합계(원)"},
    {"name": "total_profit_loss", "type": "number", "description": "평가 손익 합계(원)"},
]

KIS_POSITION_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리, 005930 등)"},
    {"name": "symbol_name", "type": "string", "description": "종목명"},
    {"name": "quantity", "type": "number", "description": "보유 수량"},
    {"name": "orderable_quantity", "type": "number", "description": "주문 가능 수량"},
    {"name": "avg_buy_price", "type": "number", "description": "매입 평균 가격(원)"},
    {"name": "current_price", "type": "number", "description": "현재가(원)"},
    {"name": "evaluation_amount", "type": "number", "description": "평가 금액(원)"},
    {"name": "profit_loss", "type": "number", "description": "평가 손익(원)"},
    {"name": "profit_loss_rate", "type": "number", "description": "평가 손익률(%)"},
]

KIS_SYMBOL_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리)"},
]


class KisAccountNode(BaseNode):
    """
    한국투자증권 REST API 1회성 계좌 조회 노드

    KIS 주식잔고조회 TR(실전 TTTC8434R / 모의 VTTC8434R)로 현재 계좌 상태를 조회합니다:
    - 보유 종목 목록·수량·매입가·평가손익 (output1)
    - 예수금·주문가능현금·총평가금액 (output2)

    상위 KisBrokerNode 연결 필수. 모의투자 여부는 브로커 노드의
    paper_trading 설정을 자동으로 따릅니다.
    """

    type: Literal["KisAccountNode"] = "KisAccountNode"
    category: NodeCategory = NodeCategory.ACCOUNT
    description: str = "i18n:nodes.KisAccountNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIS

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "주문 전 주문가능현금 확인",
            "보유 종목 목록·평가손익 조회",
            "포트폴리오 현황 표시",
        ],
        "when_not_to_use": [
            "LS증권 계좌 조회 — KoreaStockAccountNode 사용",
            "빗썸 코인 계좌 — BithumbAccountNode 사용",
        ],
        "typical_scenarios": [
            "StartNode → KisBrokerNode → KisAccountNode → TableDisplayNode",
            "KisAccountNode.balance.orderable_amount → IfNode (잔고 >= 1000000 → 주문)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "세 포트 출력: held_symbols (보유 종목코드 목록), balance (예수금·평가액), positions (종목별 잔고)",
        "브로커의 paper_trading 설정에 따라 실전/모의 TR(TTTC8434R/VTTC8434R) 자동 선택",
        "is_tool_enabled=True — AI Agent가 포트폴리오 상태 조회 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "KisAccountNode를 실시간 잔고 모니터링 용도로 짧은 주기 반복 호출",
            "reason": "REST 1회성 조회 노드이며 KIS rate-limit을 소진합니다.",
            "alternative": "ScheduleNode로 적절한 주기(분 단위 이상)를 설정하세요.",
        },
        {
            "pattern": "LS KoreaStockBrokerNode 연결에 KisAccountNode 사용",
            "reason": "프로바이더가 달라 연결이 주입되지 않습니다.",
            "alternative": "KisBrokerNode를 배치하거나 LS 계좌는 KoreaStockAccountNode를 사용하세요.",
        },
    ]
    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "예수금·보유 종목 대시보드",
            "description": "모의투자 계좌의 예수금과 종목별 평가손익을 표시합니다.",
            "workflow_snippet": {
                "id": "kis-account-dashboard",
                "name": "KIS 계좌 대시보드",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
                    {"id": "account", "type": "KisAccountNode"},
                    {"id": "balance_display", "type": "SummaryDisplayNode", "title": "예수금", "data": "{{ nodes.account.balance }}"},
                    {"id": "positions_display", "type": "TableDisplayNode", "title": "보유 종목",
                     "columns": ["symbol", "symbol_name", "quantity", "avg_buy_price", "current_price", "profit_loss"],
                     "data": "{{ nodes.account.positions }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "balance_display"},
                    {"from": "account", "to": "positions_display"},
                ],
                "credentials": [
                    {"credential_id": "kis_cred", "type": "broker_kis", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호 8자리"},
                        {"key": "account_product_code", "value": "01", "type": "text", "label": "계좌상품코드"},
                    ]},
                ],
            },
            "expected_output": "balance 포트에 예수금·주문가능현금·총평가금액, positions 포트에 종목별 수량·평가손익 테이블.",
        },
        {
            "title": "잔고 조건부 주문 게이트",
            "description": "주문가능현금이 100만원 이상일 때만 매수 주문을 실행합니다.",
            "workflow_snippet": {
                "id": "kis-account-gated-order",
                "name": "잔고 게이트 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
                    {"id": "account", "type": "KisAccountNode"},
                    {"id": "gate", "type": "IfNode", "condition": "{{ nodes.account.balance.orderable_amount >= 1000000 }}"},
                    {"id": "order", "type": "KisNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "60000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "gate"},
                    {"from": "gate", "to": "order", "condition": "true"},
                ],
                "credentials": [
                    {"credential_id": "kis_cred", "type": "broker_kis", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호 8자리"},
                        {"key": "account_product_code", "value": "01", "type": "text", "label": "계좌상품코드"},
                    ]},
                ],
            },
            "expected_output": "잔고가 조건을 충족하면 지정가 매수 주문이 실행되고, 미달이면 주문 노드가 스킵됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "데이터 입력 없음 (trigger 신호만). 브로커 연결은 DAG 순회로 자동 주입됩니다.",
        "output_consumption": "balance.orderable_amount로 주문 가능 현금을, positions[]로 종목별 잔고를 참조합니다. held_symbols는 보유 종목코드 목록입니다.",
        "common_combinations": [
            "KisBrokerNode → KisAccountNode → SummaryDisplayNode/TableDisplayNode",
            "KisAccountNode.balance → IfNode → KisNewOrderNode (잔고 게이트)",
            "ScheduleNode → KisAccountNode (주기적 포트폴리오 점검)",
        ],
        "pitfalls": [
            "모의투자 계좌의 잔고는 실계좌와 별개 — paper_trading 설정을 혼동하지 말 것",
            "실전 TTTC8434R과 모의 VTTC8434R은 브로커 설정에 따라 자동 선택되므로 수동 지정 불필요",
            "체결 직후 잔고 반영에 지연이 있을 수 있음 — 주문 직후 재조회는 이전 값을 반환할 수 있음",
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
            name="held_symbols",
            type="symbol_list",
            description="i18n:ports.held_symbols",
            fields=KIS_SYMBOL_FIELDS,
        ),
        OutputPort(
            name="balance",
            type="balance_data",
            description="i18n:ports.balance",
            fields=KIS_BALANCE_FIELDS,
        ),
        OutputPort(
            name="positions",
            type="position_data",
            description="i18n:ports.positions",
            fields=KIS_POSITION_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-11"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        return {}


KIS_ORDERABLE_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리)"},
    {"name": "orderable_cash", "type": "number", "description": "주문 가능 현금(원)"},
    {"name": "max_buy_amount", "type": "number", "description": "최대 매수 가능 금액(원)"},
    {"name": "max_buy_quantity", "type": "number", "description": "최대 매수 가능 수량"},
    {"name": "nrcvb_buy_amount", "type": "number", "description": "미수 없는 매수 금액(원)"},
    {"name": "nrcvb_buy_quantity", "type": "number", "description": "미수 없는 매수 수량"},
    {"name": "calc_price", "type": "number", "description": "가능 수량 계산 단가(원)"},
]


class KisOrderableAmountNode(BaseNode):
    """
    한국투자증권 매수가능조회 노드

    KIS 매수가능조회 TR(실전 TTTC8908R / 모의 VTTC8908R)로 특정 종목을
    지정가/시장가로 살 때의 주문 가능 현금·최대 매수 수량을 조회합니다.
    주문 수량 산정(포지션 사이징)의 입력으로 사용합니다.

    상위 KisBrokerNode 연결 필수.
    """

    type: Literal["KisOrderableAmountNode"] = "KisOrderableAmountNode"
    category: NodeCategory = NodeCategory.ACCOUNT
    description: str = "i18n:nodes.KisOrderableAmountNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIS

    symbol: Any = Field(
        default=None,
        description="매수 가능 금액을 계산할 종목코드 (6자리)",
    )
    price: Any = Field(
        default=None,
        description="계산 기준 지정가 (생략 시 시장가 기준)",
    )

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "매수 주문 전 최대 매수 가능 수량 산정 (포지션 사이징)",
            "특정 종목·가격 기준의 주문 가능 현금 확인",
        ],
        "when_not_to_use": [
            "계좌 전체 잔고·보유 종목 조회 — KisAccountNode 사용",
            "매도 가능 수량 확인 — KisAccountNode.positions의 orderable_quantity 사용",
        ],
        "typical_scenarios": [
            "KisOrderableAmountNode.orderable.max_buy_quantity → KisNewOrderNode.order.quantity (전량 매수)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "종목·가격 기준 최대 매수 가능 수량/금액 계산 (미수 미포함 값 포함)",
        "price 생략 시 시장가(ORD_DVSN=01) 기준으로 계산",
        "브로커 paper_trading에 따라 실전/모의 TR(TTTC8908R/VTTC8908R) 자동 선택",
        "is_tool_enabled=True — AI Agent 포지션 사이징 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "max_buy_quantity 전량을 그대로 주문 수량으로 사용",
            "reason": "조회와 주문 사이 가격 변동으로 주문이 거부될 수 있습니다.",
            "alternative": "여유율을 두거나(예: 90%) 미수 없는 수량(nrcvb_buy_quantity)을 사용하세요.",
        },
        {
            "pattern": "실시간 노드에 직결해 틱마다 조회",
            "reason": "REST 1회성 조회 노드이며 KIS rate-limit을 소진합니다.",
            "alternative": "ThrottleNode 또는 ScheduleNode로 주기를 제한하세요.",
        },
    ]
    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "가능 수량 기반 매수 (포지션 사이징)",
            "description": "삼성전자를 60,000원에 살 때 미수 없이 가능한 수량을 조회해 그대로 매수합니다.",
            "workflow_snippet": {
                "id": "kis-orderable-sizing",
                "name": "KIS 가능수량 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
                    {"id": "orderable", "type": "KisOrderableAmountNode", "symbol": "005930", "price": "60000"},
                    {"id": "gate", "type": "IfNode", "condition": "{{ nodes.orderable.orderable.nrcvb_buy_quantity >= 1 }}"},
                    {"id": "order", "type": "KisNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "{{ nodes.orderable.orderable.nrcvb_buy_quantity }}", "price": "60000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "orderable"},
                    {"from": "orderable", "to": "gate"},
                    {"from": "gate", "to": "order", "condition": "true"},
                ],
                "credentials": [
                    {"credential_id": "kis_cred", "type": "broker_kis", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호 8자리"},
                        {"key": "account_product_code", "value": "01", "type": "text", "label": "계좌상품코드"},
                    ]},
                ],
            },
            "expected_output": "orderable 포트에 {orderable_cash, max_buy_quantity, nrcvb_buy_quantity, ...}가 반환되고 가능 수량만큼 매수 주문이 나갑니다.",
        },
        {
            "title": "시장가 기준 가능 금액 표시",
            "description": "가격을 생략해 시장가 기준 매수 가능 정보를 조회해 표시합니다.",
            "workflow_snippet": {
                "id": "kis-orderable-display",
                "name": "KIS 매수가능 확인",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
                    {"id": "orderable", "type": "KisOrderableAmountNode", "symbol": "005930"},
                    {"id": "display", "type": "SummaryDisplayNode", "title": "매수가능", "data": "{{ nodes.orderable.orderable }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "orderable"},
                    {"from": "orderable", "to": "display"},
                ],
                "credentials": [
                    {"credential_id": "kis_cred", "type": "broker_kis", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호 8자리"},
                        {"key": "account_product_code", "value": "01", "type": "text", "label": "계좌상품코드"},
                    ]},
                ],
            },
            "expected_output": "orderable 포트의 주문가능현금·최대매수수량이 요약 표시됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "symbol(6자리 종목코드)을 설정하고, 지정가 기준 계산이 필요하면 price를 입력합니다 (생략 시 시장가 기준). 브로커 연결은 자동 주입됩니다.",
        "output_consumption": "orderable.max_buy_quantity/nrcvb_buy_quantity를 KisNewOrderNode.order.quantity에 바인딩해 포지션 사이징에 사용합니다.",
        "common_combinations": [
            "KisOrderableAmountNode → IfNode → KisNewOrderNode (가능 수량 게이트 매수)",
            "ConditionNode(RSI) → KisOrderableAmountNode → KisNewOrderNode (시그널 기반 사이징)",
        ],
        "pitfalls": [
            "매수 전용 TR — 매도 가능 수량은 KisAccountNode.positions에서 확인",
            "조회 시점과 주문 시점의 가격 차이로 실제 체결 가능 수량은 달라질 수 있음",
            "모의투자 계좌 기준 값은 실계좌와 다름",
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
            name="orderable",
            type="balance_data",
            description="i18n:ports.orderable_amount",
            fields=KIS_ORDERABLE_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-19"
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
                description="i18n:fields.KisOrderableAmountNode.symbol",
                required=True,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="005930",
                example="005930",
                example_binding="{{ nodes.rsi.passed_symbols[0].symbol }}",
                expected_type="str",
            ),
            "price": FieldSchema(
                name="price",
                type=FieldType.STRING,
                description="i18n:fields.KisOrderableAmountNode.price",
                required=False,
                expression_mode=ExpressionMode.BOTH,
                category=FieldCategory.PARAMETERS,
                placeholder="60000",
                example="60000",
                help_text="지정가 기준 계산 단가(원). 생략하면 시장가 기준으로 계산합니다.",
                expected_type="str",
            ),
        }
