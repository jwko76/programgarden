"""
ProgramGarden Core - Kiwoom Account Node

키움증권 계좌 조회:
- KiwoomAccountNode: 주식 잔고·예수금 REST 1회 조회 (api-id kt00018/kt00010)
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

KIWOOM_BALANCE_FIELDS: List[Dict[str, str]] = [
    {"name": "deposit", "type": "number", "description": "예수금 총액(원)"},
    {"name": "orderable_amount", "type": "number", "description": "주문 가능 현금(원)"},
    {"name": "total_evaluation", "type": "number", "description": "총 평가 금액(원)"},
    {"name": "total_purchase", "type": "number", "description": "매입 금액 합계(원)"},
    {"name": "total_profit_loss", "type": "number", "description": "평가 손익 합계(원)"},
]

KIWOOM_POSITION_FIELDS: List[Dict[str, str]] = [
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

KIWOOM_SYMBOL_FIELDS: List[Dict[str, str]] = [
    {"name": "symbol", "type": "string", "description": "종목코드 (6자리)"},
]


class KiwoomAccountNode(BaseNode):
    """
    키움증권 REST API 1회성 계좌 조회 노드

    키움 계좌평가잔고내역 api-id(kt00018)와 매수가능금액 api-id(kt00010)로
    현재 계좌 상태를 조회합니다:
    - 보유 종목 목록·수량·매입가·평가손익
    - 예수금·주문가능현금·총평가금액

    상위 KiwoomBrokerNode 연결 필수. 모의투자 여부는 브로커 노드의
    paper_trading 설정을 자동으로 따릅니다 (키움은 KIS와 달리 api-id
    분기가 아닌 접속 도메인 전환으로 실전/모의를 구분합니다).
    """

    type: Literal["KiwoomAccountNode"] = "KiwoomAccountNode"
    category: NodeCategory = NodeCategory.ACCOUNT
    description: str = "i18n:nodes.KiwoomAccountNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIWOOM

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "주문 전 주문가능현금 확인",
            "보유 종목 목록·평가손익 조회",
            "포트폴리오 현황 표시",
        ],
        "when_not_to_use": [
            "LS증권 계좌 조회 — KoreaStockAccountNode 사용",
            "한국투자증권 계좌 조회 — KisAccountNode 사용",
            "빗썸 코인 계좌 — BithumbAccountNode 사용",
        ],
        "typical_scenarios": [
            "StartNode → KiwoomBrokerNode → KiwoomAccountNode → TableDisplayNode",
            "KiwoomAccountNode.balance.orderable_amount → IfNode (잔고 >= 1000000 → 주문)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "세 포트 출력: held_symbols (보유 종목코드 목록), balance (예수금·평가액), positions (종목별 잔고)",
        "브로커의 paper_trading 설정에 따라 실전/모의 접속 도메인이 자동 전환됨 (api-id는 동일, KIS의 TTTC/VTTC 분기와 다름)",
        "is_tool_enabled=True — AI Agent가 포트폴리오 상태 조회 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "KiwoomAccountNode를 실시간 잔고 모니터링 용도로 짧은 주기 반복 호출",
            "reason": "REST 1회성 조회 노드이며 키움 rate-limit을 소진합니다.",
            "alternative": "ScheduleNode로 적절한 주기(분 단위 이상)를 설정하세요.",
        },
        {
            "pattern": "LS KoreaStockBrokerNode 또는 KIS KisBrokerNode 연결에 KiwoomAccountNode 사용",
            "reason": "프로바이더가 달라 연결이 주입되지 않습니다.",
            "alternative": "KiwoomBrokerNode를 배치하거나 해당 증권사 전용 계좌 노드를 사용하세요.",
        },
    ]
    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "예수금·보유 종목 대시보드",
            "description": "모의투자 계좌의 예수금과 종목별 평가손익을 표시합니다.",
            "workflow_snippet": {
                "id": "kiwoom-account-dashboard",
                "name": "키움 계좌 대시보드",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "account", "type": "KiwoomAccountNode"},
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
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "balance 포트에 예수금·주문가능현금·총평가금액, positions 포트에 종목별 수량·평가손익 테이블.",
        },
        {
            "title": "잔고 조건부 주문 게이트",
            "description": "주문가능현금이 100만원 이상일 때만 매수 주문을 실행합니다.",
            "workflow_snippet": {
                "id": "kiwoom-account-gated-order",
                "name": "잔고 게이트 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "account", "type": "KiwoomAccountNode"},
                    {"id": "gate", "type": "IfNode", "condition": "{{ nodes.account.balance.orderable_amount >= 1000000 }}"},
                    {"id": "order", "type": "KiwoomNewOrderNode", "side": "buy", "order_type": "limit",
                     "order": {"symbol": "005930", "quantity": "10", "price": "60000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "gate"},
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
            "expected_output": "잔고가 조건을 충족하면 지정가 매수 주문이 실행되고, 미달이면 주문 노드가 스킵됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "데이터 입력 없음 (trigger 신호만). 브로커 연결은 DAG 순회로 자동 주입됩니다.",
        "output_consumption": "balance.orderable_amount로 주문 가능 현금을, positions[]로 종목별 잔고를 참조합니다. held_symbols는 보유 종목코드 목록입니다.",
        "common_combinations": [
            "KiwoomBrokerNode → KiwoomAccountNode → SummaryDisplayNode/TableDisplayNode",
            "KiwoomAccountNode.balance → IfNode → KiwoomNewOrderNode (잔고 게이트)",
            "ScheduleNode → KiwoomAccountNode (주기적 포트폴리오 점검)",
        ],
        "pitfalls": [
            "모의투자 계좌의 잔고는 실계좌와 별개 — paper_trading 설정을 혼동하지 말 것",
            "키움은 실전/모의 구분이 접속 도메인 전환이므로 api-id(kt00018/kt00010)는 그대로 사용됨",
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
            fields=KIWOOM_SYMBOL_FIELDS,
        ),
        OutputPort(
            name="balance",
            type="balance_data",
            description="i18n:ports.balance",
            fields=KIWOOM_BALANCE_FIELDS,
        ),
        OutputPort(
            name="positions",
            type="position_data",
            description="i18n:ports.positions",
            fields=KIWOOM_POSITION_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-18"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        return {}
