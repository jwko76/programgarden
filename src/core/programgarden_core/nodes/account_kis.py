"""
ProgramGarden Core - KIS Account Node

한국투자증권 계좌 조회:
- KisAccountNode: 주식 잔고·예수금 REST 1회 조회 (TTTC8434R/VTTC8434R)
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
