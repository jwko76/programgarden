"""
ProgramGarden Core - KIS Broker Node

한국투자증권(KIS) 연결 노드:
- KisBrokerNode: KIS Developers OpenAPI appkey/appsecret 인증 게이트웨이
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


class KisBrokerNode(BaseNode):
    """
    한국투자증권(KIS) 브로커 연결 노드

    KIS Developers OpenAPI(REST + WebSocket)를 통해 국내주식 거래를 위한
    연결을 생성합니다. 인증 게이트웨이 역할 — 하위 계좌, 시세, 주문 노드가
    DAG 순회를 통해 자동으로 브로커 연결을 상속합니다.

    credential_id로 ``broker_kis`` 인증 정보를 참조합니다:
    appkey + appsecret + account_no(계좌번호 8자리) + account_product_code(상품코드, 기본 01)

    LS증권과 같은 국내주식 스코프이지만 프로바이더가 다르므로
    KoreaStockBrokerNode(LS)와 같은 워크플로우에 공존할 수 있습니다.
    KIS 계열 노드(Kis*)는 이 노드의 연결에만 바인딩됩니다.

    ``paper_trading=True`` 로 설정하면 KIS 모의투자 서버로 접속합니다.
    """

    type: Literal["KisBrokerNode"] = "KisBrokerNode"
    description: str = "i18n:nodes.KisBrokerNode.description"

    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIS

    category: NodeCategory = NodeCategory.INFRA

    provider: str = Field(default="koreainvestment.com", description="증권사 제공자")
    credential_id: Optional[str] = Field(
        default=None, description="한국투자증권 인증정보 참조 (broker_kis 타입)"
    )
    paper_trading: bool = Field(default=False, description="모의투자 모드")

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "한국투자증권 API로 국내주식을 거래하는 모든 워크플로우의 시작점",
            "KisAccountNode / KisMarketDataNode / KisNewOrderNode 앞에 반드시 배치",
            "모의투자 검증 워크플로우 (paper_trading=True)",
        ],
        "when_not_to_use": [
            "LS증권 국내주식 워크플로우 — KoreaStockBrokerNode 사용 (같은 국내주식이라도 프로바이더가 다름)",
            "코인 거래 — BithumbBrokerNode 사용",
        ],
        "typical_scenarios": [
            "StartNode → KisBrokerNode → KisAccountNode → TableDisplayNode",
            "StartNode → KisBrokerNode(paper_trading=True) → KisNewOrderNode (RSI 기반 매수)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "KIS Developers appkey/appsecret 인증 — OAuth 토큰(24h) 자동 발급·캐시·갱신",
        "connection 출력은 하위 모든 KIS 노드에 DAG 자동 주입 — 명시적 바인딩 불필요",
        "paper_trading=True 시 모의투자 서버(openapivts) 접속 — 주문 tr_id도 자동 전환",
        "LS KoreaStockBrokerNode와 같은 워크플로우 공존 가능 (프로바이더별 연결 분리)",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "KisBrokerNode 없이 KisAccountNode / KisNewOrderNode 사용",
            "reason": "인증 정보가 없어 모든 KIS API 호출이 실패합니다.",
            "alternative": "항상 KisBrokerNode를 DAG 시작부에 배치하세요.",
        },
        {
            "pattern": "KIS 노드를 LS KoreaStockBrokerNode 연결에 바인딩",
            "reason": "프로바이더가 달라 자동 주입되지 않으며 검증 단계에서 INCOMPATIBLE_BROKER_PROVIDER 에러가 발생합니다.",
            "alternative": "Kis* 노드에는 KisBrokerNode를, KoreaStock* 노드에는 KoreaStockBrokerNode를 배치하세요.",
        },
        {
            "pattern": "데모/검증 워크플로우에 paper_trading=False 사용",
            "reason": "실계좌로 실제 주문이 전송됩니다.",
            "alternative": "실주문 의도가 없는 워크플로우는 paper_trading=True로 설정하세요.",
        },
    ]

    _examples: ClassVar[List[Dict[str, Any]]] = [
        {
            "title": "모의투자 계좌 잔고 조회",
            "description": "KIS 모의투자 서버에 연결해 예수금·보유 종목을 표시합니다.",
            "workflow_snippet": {
                "id": "kis-broker-paper-account",
                "name": "KIS 모의투자 잔고",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
                    {"id": "account", "type": "KisAccountNode"},
                    {"id": "display", "type": "SummaryDisplayNode", "title": "예수금", "data": "{{ nodes.account.balance }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "display"},
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
            "expected_output": "브로커가 모의투자 세션 연결을 생성하고, 계좌 노드가 모의 계좌의 예수금·잔고를 반환합니다.",
        },
        {
            "title": "LS + KIS 국내주식 브로커 공존",
            "description": "같은 워크플로우에서 LS와 KIS 계좌를 동시에 조회합니다 (프로바이더별 연결 분리).",
            "workflow_snippet": {
                "id": "kis-ls-multi-broker",
                "name": "LS + KIS 멀티브로커",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "ls_broker", "type": "KoreaStockBrokerNode", "credential_id": "ls_cred"},
                    {"id": "kis_broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": False},
                    {"id": "ls_account", "type": "KoreaStockAccountNode"},
                    {"id": "kis_account", "type": "KisAccountNode"},
                ],
                "edges": [
                    {"from": "start", "to": "ls_broker"},
                    {"from": "start", "to": "kis_broker"},
                    {"from": "ls_broker", "to": "ls_account"},
                    {"from": "kis_broker", "to": "kis_account"},
                ],
                "credentials": [
                    {"credential_id": "ls_cred", "type": "broker_ls_korea_stock", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                    ]},
                    {"credential_id": "kis_cred", "type": "broker_kis", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호 8자리"},
                        {"key": "account_product_code", "value": "01", "type": "text", "label": "계좌상품코드"},
                    ]},
                ],
            },
            "expected_output": "KoreaStock* 노드는 LS 연결에, Kis* 노드는 KIS 연결에 각각 자동 바인딩되어 두 계좌가 독립적으로 조회됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "credential_id(broker_kis: appkey/appsecret/account_no/account_product_code)와 paper_trading 불리언만 설정합니다. 런타임 데이터 입력은 없습니다.",
        "output_consumption": "connection 출력은 같은 워크플로우의 모든 korea_stock+KIS 스코프 노드에 자동 주입됩니다. `{{ nodes.broker.connection }}`을 수동 바인딩하지 마세요.",
        "common_combinations": [
            "KisBrokerNode → KisAccountNode → TableDisplayNode",
            "KisBrokerNode → KisHistoricalDataNode → ConditionNode(RSI) → ThrottleNode → KisNewOrderNode",
            "KoreaStockBrokerNode(LS) + KisBrokerNode 병렬 배치 (멀티브로커 분산)",
        ],
        "pitfalls": [
            "credential 타입은 broker_kis — LS의 broker_ls_korea_stock과 혼용 불가",
            "KIS 접근토큰은 재발급이 분당 1회로 제한되므로 짧은 주기로 워크플로우를 재시작하면 토큰 발급이 거부될 수 있음 (SDK가 파일 캐시로 완화)",
            "paper_trading=True여도 시세 데이터는 실전 서버와 동일 — 주문만 모의 체결",
        ],
    }

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-11"

    _inputs: List[InputPort] = []
    _outputs: List[OutputPort] = [
        OutputPort(
            name="connection",
            type="broker_connection",
            description="i18n:ports.connection",
            example={"_opaque": True, "provider": "koreainvestment.com"},
        )
    ]

    @classmethod
    def get_field_schema(cls) -> Dict[str, "FieldSchema"]:
        from programgarden_core.models.field_binding import (
            FieldSchema, FieldType, FieldCategory, UIComponent, ExpressionMode
        )
        return {
            "credential_id": FieldSchema(
                name="credential_id",
                type=FieldType.CREDENTIAL,
                description="i18n:fields.KisBrokerNode.credential_id",
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.SETTINGS,
                ui_component=UIComponent.CUSTOM_CREDENTIAL_SELECT,
                credential_types=["broker_kis"],
                example="my-kis-api",
                help_text="Use the credential id provided in user message <credentials_context> block (verbatim). Do NOT invent.",
            ),
            "paper_trading": FieldSchema(
                name="paper_trading",
                type=FieldType.BOOLEAN,
                description="i18n:fields.KisBrokerNode.paper_trading",
                default=False,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.PARAMETERS,
                example=True,
                help_text="true면 KIS 모의투자 서버로 접속합니다. 실주문 의도가 없으면 반드시 true로 설정하세요.",
            ),
        }
