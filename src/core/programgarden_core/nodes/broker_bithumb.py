"""
ProgramGarden Core - Bithumb Broker Node

빗썸(Bithumb) 거래소 연결 노드:
- BithumbBrokerNode: 빗썸 API Access Key/Secret Key 인증 게이트웨이
"""

from typing import Optional, List, Literal, Dict, ClassVar, Any, TYPE_CHECKING
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


class BithumbBrokerNode(BaseNode):
    """
    빗썸(Bithumb) 거래소 연결 노드

    빗썸 OpenAPI v2.1.5를 통해 코인 거래를 위한 연결을 생성합니다.
    인증 게이트웨이 역할 — 하위 계좌, 시세, 주문 노드가 DAG 순회를 통해
    자동으로 브로커 연결을 상속합니다.

    credential_id로 ``broker_bithumb`` 인증 정보(access_key + secret_key)를 참조합니다.
    LS증권과 달리 OAuth 토큰이 없으며 요청마다 JWT를 생성합니다.
    """

    type: Literal["BithumbBrokerNode"] = "BithumbBrokerNode"
    description: str = "i18n:nodes.BithumbBrokerNode.description"

    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.COIN
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.BITHUMB

    category: NodeCategory = NodeCategory.INFRA

    provider: str = Field(default="bithumb.com", description="거래소 제공자")
    credential_id: Optional[str] = Field(
        default=None, description="빗썸 인증정보 참조 (broker_bithumb 타입)"
    )

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "모든 빗썸 코인 거래 워크플로우의 시작점",
            "BithumbAccountNode / BithumbMarketDataNode / BithumbNewOrderNode 앞에 반드시 배치",
        ],
        "when_not_to_use": [
            "LS증권 거래 워크플로우 — OverseasStockBrokerNode / KoreaStockBrokerNode 사용",
            "인증이 불필요한 공개 API만 쓰는 경우 (단, BithumbMarketDataNode는 인증 불필요)",
        ],
        "typical_scenarios": [
            "StartNode → BithumbBrokerNode → BithumbAccountNode → TableDisplayNode",
            "StartNode → BithumbBrokerNode → BithumbNewOrderNode (RSI 기반 BTC 매수)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "빗썸 API access_key/secret_key로 인증 — 요청마다 HS256 JWT 자동 생성",
        "connection 출력은 하위 모든 빗썸 노드에 DAG 자동 주입 — 명시적 바인딩 불필요",
        "credential_types=['broker_bithumb'] 으로 올바른 인증 정보만 선택됨",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "BithumbBrokerNode 없이 BithumbAccountNode / BithumbNewOrderNode 사용",
            "reason": "인증 정보가 없어 모든 Private API 호출이 실패합니다.",
            "alternative": "항상 BithumbBrokerNode를 DAG 시작부에 배치하세요.",
        },
    ]

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-06-19"

    _inputs: List[InputPort] = []
    _outputs: List[OutputPort] = [
        OutputPort(
            name="connection",
            type="broker_connection",
            description="i18n:ports.connection",
            example={"_opaque": True, "provider": "bithumb.com"},
        )
    ]

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        from programgarden_core.models.field_binding import (
            FieldSchema, FieldType, FieldCategory, ExpressionMode
        )
        return {
            "credential_id": FieldSchema(
                name="credential_id",
                type=FieldType.CREDENTIAL,
                description="i18n:fields.BithumbBrokerNode.credential_id",
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.SETTINGS,
                credential_types=["broker_bithumb"],
                example="my-bithumb-api",
            ),
        }
