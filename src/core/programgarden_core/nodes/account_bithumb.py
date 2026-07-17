"""
ProgramGarden Core - Bithumb Account Node

빗썸 계좌 조회:
- BithumbAccountNode: 빗썸 보유 자산·KRW 잔고 REST 1회 조회
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

COIN_BALANCE_FIELDS: List[Dict[str, str]] = [
    {"name": "krw_balance", "type": "number", "description": "주문 가능 원화 잔고(KRW)"},
    {"name": "krw_locked", "type": "number", "description": "주문 중 묶인 원화(KRW)"},
    {"name": "orderable_amount", "type": "number", "description": "주문 가능 금액 (krw_balance 동일)"},
]

COIN_POSITION_FIELDS: List[Dict[str, str]] = [
    {"name": "market", "type": "string", "description": "마켓 코드 (KRW-BTC 등)"},
    {"name": "currency", "type": "string", "description": "화폐 코드 (BTC 등)"},
    {"name": "balance", "type": "number", "description": "주문 가능 수량"},
    {"name": "locked", "type": "number", "description": "주문 중 묶인 수량"},
    {"name": "avg_buy_price", "type": "number", "description": "평균 매수 가격(KRW)"},
]

COIN_SYMBOL_FIELDS: List[Dict[str, str]] = [
    {"name": "market", "type": "string", "description": "마켓 코드 (KRW-BTC 등)"},
]


class BithumbAccountNode(BaseNode):
    """
    빗썸 REST API 1회성 계좌 조회 노드

    빗썸 OpenAPI ``GET /v1/accounts`` 로 현재 보유 자산을 조회합니다:
    - 보유 코인 목록 (KRW 제외)
    - 각 코인별 잔고 · 묶인 수량 · 평균 매수가
    - KRW 잔고 (주문 가능 원화)

    상위 BithumbBrokerNode 연결 필수.
    """

    type: Literal["BithumbAccountNode"] = "BithumbAccountNode"
    category: NodeCategory = NodeCategory.ACCOUNT
    description: str = "i18n:nodes.BithumbAccountNode.description"
    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "주문 전 KRW 잔고 확인",
            "보유 코인 목록·잔고 조회",
            "포트폴리오 현황 표시",
        ],
        "when_not_to_use": [
            "LS증권 계좌 조회 — KoreaStockAccountNode / OverseasStockAccountNode 사용",
        ],
        "typical_scenarios": [
            "StartNode → BithumbBrokerNode → BithumbAccountNode → TableDisplayNode",
            "BithumbAccountNode.balance.orderable_amount → IfNode (잔고 >= 100000 → 주문)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "세 포트 출력: held_symbols (보유 마켓 목록), balance (KRW 잔고), positions (코인별 잔고)",
        "is_tool_enabled=True — AI Agent가 포트폴리오 상태 조회 도구로 사용 가능",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "BithumbBrokerNode 없이 BithumbAccountNode 단독 사용",
            "reason": "GET /v1/accounts 는 Private API — 인증 없이는 호출이 실패합니다.",
            "alternative": "워크플로우 시작부에 BithumbBrokerNode를 배치하세요.",
        },
        {
            "pattern": "positions 포트에서 KRW 잔고를 찾음",
            "reason": "positions는 KRW를 제외한 보유 코인 목록입니다. KRW는 별도 포트입니다.",
            "alternative": "KRW 잔고는 balance 포트(balance.orderable_amount)를 사용하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "잔고·보유코인 대시보드",
            "description": "KRW 잔고 요약과 보유 코인 테이블을 함께 표시합니다.",
            "workflow_snippet": {
                "id": "bithumb-account-dashboard",
                "name": "빗썸 잔고 대시보드",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "account", "type": "BithumbAccountNode"},
                    {"id": "krw", "type": "SummaryDisplayNode", "title": "KRW 잔고",
                     "data": "{{ nodes.account.balance }}"},
                    {"id": "coins", "type": "TableDisplayNode", "title": "보유 코인",
                     "columns": ["market", "currency", "balance", "avg_buy_price"],
                     "data": "{{ nodes.account.positions }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "krw"},
                    {"from": "account", "to": "coins"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "balance 포트가 KRW 요약에, positions 포트가 보유 코인 테이블에 표시됩니다.",
        },
        {
            "title": "잔고 조건 매수",
            "description": "주문 가능 KRW가 10만원 이상일 때만 BTC를 시장가 매수합니다.",
            "workflow_snippet": {
                "id": "bithumb-account-gated-buy",
                "name": "잔고 조건 매수",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
                    {"id": "account", "type": "BithumbAccountNode"},
                    {"id": "gate", "type": "IfNode",
                     "condition": "{{ nodes.account.balance.orderable_amount >= 100000 }}"},
                    {"id": "buy", "type": "BithumbNewOrderNode", "side": "bid", "order_type": "price",
                     "order": {"market": "KRW-BTC", "price": "100000"}},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "gate"},
                    {"from": "gate", "to": "buy", "condition": "true"},
                ],
                "credentials": [
                    {"credential_id": "bithumb_cred", "type": "broker_bithumb", "data": [
                        {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                        {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
                    ]},
                ],
            },
            "expected_output": "orderable_amount가 100,000 이상이면 100,000 KRW 시장가 매수가 실행됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "설정 필드가 없습니다 — trigger 입력(선택)만 받으며 브로커 연결은 자동 주입됩니다.",
        "output_consumption": "balance.orderable_amount로 주문 가능 KRW를, positions[n].balance로 코인 수량을 참조합니다. held_symbols는 보유 마켓 코드 목록입니다.",
        "common_combinations": [
            "BithumbAccountNode → SummaryDisplayNode / TableDisplayNode (잔고 대시보드)",
            "BithumbAccountNode.balance → IfNode → BithumbNewOrderNode (잔고 조건 주문)",
            "ScheduleNode → BithumbAccountNode (주기적 포트폴리오 스냅샷)",
        ],
        "pitfalls": [
            "KRW는 positions에 포함되지 않음 — balance 포트에서 조회",
            "avg_buy_price는 KRW 기준 — 수익률 계산 시 현재가(BithumbMarketDataNode)와 조합 필요",
            "REST 1회 조회 노드 — 연속 모니터링은 ScheduleNode로 주기 실행",
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
            fields=COIN_SYMBOL_FIELDS,
        ),
        OutputPort(
            name="balance",
            type="balance_data",
            description="i18n:ports.balance",
            fields=COIN_BALANCE_FIELDS,
        ),
        OutputPort(
            name="positions",
            type="position_data",
            description="i18n:ports.positions",
            fields=COIN_POSITION_FIELDS,
        ),
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-11"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        return {}
