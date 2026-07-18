"""
ProgramGarden Core - Kiwoom Broker Node

키움증권(Kiwoom Securities) 연결 노드:
- KiwoomBrokerNode: 키움 OpenAPI appkey/appsecret 인증 게이트웨이
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


class KiwoomBrokerNode(BaseNode):
    """
    키움증권(Kiwoom) 브로커 연결 노드

    키움 OpenAPI(REST + WebSocket)를 통해 국내주식 거래를 위한 연결을
    생성합니다. 인증 게이트웨이 역할 — 하위 계좌, 시세, 주문 노드가
    DAG 순회를 통해 자동으로 브로커 연결을 상속합니다.

    credential_id로 ``broker_kiwoom`` 인증 정보를 참조합니다:
    appkey + appsecret + account_no(계좌번호)

    LS증권·KIS와 같은 국내주식 스코프이지만 프로바이더가 다르므로
    KoreaStockBrokerNode(LS)·KisBrokerNode(KIS)와 같은 워크플로우에
    공존할 수 있습니다. 키움 계열 노드(Kiwoom*)는 이 노드의 연결에만
    바인딩됩니다.

    ``paper_trading=True`` 로 설정하면 키움 모의투자 서버로 접속합니다.
    KIS와 달리 키움은 실전/모의 구분이 tr_id(TTTC/VTTC) 분기가 아니라
    **접속 도메인 자체**가 다릅니다 (``api.kiwoom.com`` ↔
    ``mockapi.kiwoom.com``) — paper_trading은 단순히 접속 서버를
    전환할 뿐, api-id는 실전/모의 공용입니다.
    """

    type: Literal["KiwoomBrokerNode"] = "KiwoomBrokerNode"
    description: str = "i18n:nodes.KiwoomBrokerNode.description"

    _img_url: ClassVar[str] = ""
    _product_scope: ClassVar[ProductScope] = ProductScope.KOREA_STOCK
    _broker_provider: ClassVar[BrokerProvider] = BrokerProvider.KIWOOM

    category: NodeCategory = NodeCategory.INFRA

    provider: str = Field(default="kiwoom.com", description="증권사 제공자")
    credential_id: Optional[str] = Field(
        default=None, description="키움증권 인증정보 참조 (broker_kiwoom 타입)"
    )
    paper_trading: bool = Field(default=False, description="모의투자 모드")

    _usage: ClassVar[Dict[str, Any]] = {
        "when_to_use": [
            "키움증권 API로 국내주식을 거래하는 모든 워크플로우의 시작점",
            "KiwoomAccountNode / KiwoomMarketDataNode / KiwoomNewOrderNode 앞에 반드시 배치",
            "모의투자 검증 워크플로우 (paper_trading=True)",
        ],
        "when_not_to_use": [
            "LS증권 국내주식 워크플로우 — KoreaStockBrokerNode 사용 (같은 국내주식이라도 프로바이더가 다름)",
            "한국투자증권 국내주식 워크플로우 — KisBrokerNode 사용",
            "코인 거래 — BithumbBrokerNode 사용",
        ],
        "typical_scenarios": [
            "StartNode → KiwoomBrokerNode → KiwoomAccountNode → TableDisplayNode",
            "StartNode → KiwoomBrokerNode(paper_trading=True) → KiwoomNewOrderNode (RSI 기반 매수)",
        ],
    }
    _features: ClassVar[List[str]] = [
        "키움 OpenAPI appkey/appsecret 인증 — OAuth 접근토큰 자동 발급·캐시·갱신",
        "connection 출력은 하위 모든 키움 노드에 DAG 자동 주입 — 명시적 바인딩 불필요",
        "paper_trading=True 시 모의투자 도메인(mockapi.kiwoom.com) 접속 — KIS와 달리 tr_id 분기가 아닌 도메인 자체가 전환됨",
        "LS KoreaStockBrokerNode·KIS KisBrokerNode와 같은 워크플로우 공존 가능 (프로바이더별 연결 분리)",
    ]
    _anti_patterns: ClassVar[List[Dict[str, str]]] = [
        {
            "pattern": "KiwoomBrokerNode 없이 KiwoomAccountNode / KiwoomNewOrderNode 사용",
            "reason": "인증 정보가 없어 모든 키움 API 호출이 실패합니다.",
            "alternative": "항상 KiwoomBrokerNode를 DAG 시작부에 배치하세요.",
        },
        {
            "pattern": "키움 노드를 LS KoreaStockBrokerNode 또는 KIS KisBrokerNode 연결에 바인딩",
            "reason": "프로바이더가 달라 자동 주입되지 않으며 검증 단계에서 INCOMPATIBLE_BROKER_PROVIDER 에러가 발생합니다.",
            "alternative": "Kiwoom* 노드에는 KiwoomBrokerNode를, KoreaStock* 노드에는 KoreaStockBrokerNode를, Kis* 노드에는 KisBrokerNode를 배치하세요.",
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
            "description": "키움 모의투자 서버에 연결해 예수금·보유 종목을 표시합니다.",
            "workflow_snippet": {
                "id": "kiwoom-broker-paper-account",
                "name": "키움 모의투자 잔고",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
                    {"id": "account", "type": "KiwoomAccountNode"},
                    {"id": "display", "type": "SummaryDisplayNode", "title": "예수금", "data": "{{ nodes.account.balance }}"},
                ],
                "edges": [
                    {"from": "start", "to": "broker"},
                    {"from": "broker", "to": "account"},
                    {"from": "account", "to": "display"},
                ],
                "credentials": [
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "브로커가 모의투자 세션 연결을 생성하고, 계좌 노드가 모의 계좌의 예수금·잔고를 반환합니다.",
        },
        {
            "title": "LS + KIS + 키움 국내주식 3사 브로커 공존",
            "description": "같은 워크플로우에서 LS·KIS·키움 세 증권사 계좌를 동시에 조회합니다 (프로바이더별 연결 분리).",
            "workflow_snippet": {
                "id": "kiwoom-ls-kis-multi-broker",
                "name": "LS + KIS + 키움 멀티브로커",
                "nodes": [
                    {"id": "start", "type": "StartNode"},
                    {"id": "ls_broker", "type": "KoreaStockBrokerNode", "credential_id": "ls_cred"},
                    {"id": "kis_broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": False},
                    {"id": "kiwoom_broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": False},
                    {"id": "ls_account", "type": "KoreaStockAccountNode"},
                    {"id": "kis_account", "type": "KisAccountNode"},
                    {"id": "kiwoom_account", "type": "KiwoomAccountNode"},
                ],
                "edges": [
                    {"from": "start", "to": "ls_broker"},
                    {"from": "start", "to": "kis_broker"},
                    {"from": "start", "to": "kiwoom_broker"},
                    {"from": "ls_broker", "to": "ls_account"},
                    {"from": "kis_broker", "to": "kis_account"},
                    {"from": "kiwoom_broker", "to": "kiwoom_account"},
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
                    {"credential_id": "kiwoom_cred", "type": "broker_kiwoom", "data": [
                        {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                        {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                        {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                    ]},
                ],
            },
            "expected_output": "KoreaStock* 노드는 LS 연결에, Kis* 노드는 KIS 연결에, Kiwoom* 노드는 키움 연결에 각각 자동 바인딩되어 세 계좌가 독립적으로 조회됩니다.",
        },
    ]
    _node_guide: ClassVar[Dict[str, Any]] = {
        "input_handling": "credential_id(broker_kiwoom: appkey/appsecret/account_no)와 paper_trading 불리언만 설정합니다. 런타임 데이터 입력은 없습니다.",
        "output_consumption": "connection 출력은 같은 워크플로우의 모든 korea_stock+Kiwoom 스코프 노드에 자동 주입됩니다. `{{ nodes.broker.connection }}`을 수동 바인딩하지 마세요.",
        "common_combinations": [
            "KiwoomBrokerNode → KiwoomAccountNode → TableDisplayNode",
            "KiwoomBrokerNode → KiwoomHistoricalDataNode → ConditionNode(RSI) → ThrottleNode → KiwoomNewOrderNode",
            "KoreaStockBrokerNode(LS) + KisBrokerNode(KIS) + KiwoomBrokerNode 병렬 배치 (3사 멀티브로커 분산)",
        ],
        "pitfalls": [
            "credential 타입은 broker_kiwoom — LS의 broker_ls_korea_stock, KIS의 broker_kis와 혼용 불가",
            "키움은 실전/모의가 tr_id 분기가 아닌 접속 도메인 자체 전환이므로, paper_trading 값이 곧 접속 서버를 결정함 (KIS의 TTTC/VTTC 패턴과 다름)",
            "키움 계좌가 KIS처럼 cano+acnt_prdt_cd 2단 구조를 요구하는지는 실계좌로 확인되지 않음 — 현재 노드는 단일 account_no 필드만 사용하며, 향후 검증 결과에 따라 account_product_code 필드가 추가될 수 있음",
        ],
    }

    _version: ClassVar[str] = "1.0.0"
    _updated_at: ClassVar[str] = "2026-07-18"
    _change_note: ClassVar[Optional[str]] = None

    _inputs: List[InputPort] = []
    _outputs: List[OutputPort] = [
        OutputPort(
            name="connection",
            type="broker_connection",
            description="i18n:ports.connection",
            example={"_opaque": True, "provider": "kiwoom.com"},
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
                description="i18n:fields.KiwoomBrokerNode.credential_id",
                required=True,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.SETTINGS,
                ui_component=UIComponent.CUSTOM_CREDENTIAL_SELECT,
                credential_types=["broker_kiwoom"],
                example="my-kiwoom-api",
                help_text="Use the credential id provided in user message <credentials_context> block (verbatim). Do NOT invent.",
            ),
            "paper_trading": FieldSchema(
                name="paper_trading",
                type=FieldType.BOOLEAN,
                description="i18n:fields.KiwoomBrokerNode.paper_trading",
                default=False,
                expression_mode=ExpressionMode.FIXED_ONLY,
                category=FieldCategory.PARAMETERS,
                example=True,
                help_text="true면 키움 모의투자 서버(mockapi.kiwoom.com)로 접속합니다. 실주문 의도가 없으면 반드시 true로 설정하세요.",
            ),
        }
