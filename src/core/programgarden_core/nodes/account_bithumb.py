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
    _updated_at: ClassVar[str] = "2026-06-19"
    _change_note: ClassVar[Optional[str]] = None

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        return {}
