"""
키움증권(Kiwoom) 노드 6개 단위 테스트

테스트 대상:
1. 노드 모델 생성 및 타입/카테고리/ProductScope/BrokerProvider 검증
2. 입출력 포트 검증
3. FieldSchema 검증
4. NodeTypeRegistry 등록 확인
5. i18n 키 존재 확인
6. is_tool_enabled 검증
7. 직렬화 (JSON round-trip)

실행:
    cd src/core && poetry run pytest tests/test_kiwoom_nodes.py -v
"""

import pytest

from programgarden_core.nodes.base import NodeCategory, ProductScope, BrokerProvider
from programgarden_core.nodes.broker_kiwoom import KiwoomBrokerNode
from programgarden_core.nodes.account_kiwoom import KiwoomAccountNode
from programgarden_core.nodes.market_kiwoom import KiwoomMarketDataNode
from programgarden_core.nodes.historical_kiwoom import KiwoomHistoricalDataNode
from programgarden_core.nodes.order_kiwoom import KiwoomNewOrderNode, KiwoomCancelOrderNode

# 모든 키움 노드 클래스
ALL_KIWOOM_NODES = [
    KiwoomBrokerNode,
    KiwoomAccountNode,
    KiwoomMarketDataNode,
    KiwoomHistoricalDataNode,
    KiwoomNewOrderNode,
    KiwoomCancelOrderNode,
]


# ============================================================
# 1. 모델 기본 검증
# ============================================================


class TestKiwoomNodeModels:
    """6개 노드 인스턴스 생성 및 기본 속성 검증"""

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_instantiation(self, node_cls):
        node = node_cls(id="test1")
        assert node.id == "test1"

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_type_matches_class_name(self, node_cls):
        node = node_cls(id="test1")
        assert node.type == node_cls.__name__

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_product_scope_is_korea_stock(self, node_cls):
        assert node_cls._product_scope == ProductScope.KOREA_STOCK

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_broker_provider_is_kiwoom(self, node_cls):
        assert node_cls._broker_provider == BrokerProvider.KIWOOM

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_description_is_i18n(self, node_cls):
        node = node_cls(id="test1")
        assert node.description.startswith("i18n:")

    def test_broker_category_is_infra(self):
        node = KiwoomBrokerNode(id="b")
        assert node.category == NodeCategory.INFRA

    def test_account_category(self):
        node = KiwoomAccountNode(id="a")
        assert node.category == NodeCategory.ACCOUNT

    @pytest.mark.parametrize("node_cls", [
        KiwoomMarketDataNode, KiwoomHistoricalDataNode,
    ], ids=lambda c: c.__name__)
    def test_market_category(self, node_cls):
        node = node_cls(id="m")
        assert node.category == NodeCategory.MARKET

    @pytest.mark.parametrize("node_cls", [
        KiwoomNewOrderNode, KiwoomCancelOrderNode,
    ], ids=lambda c: c.__name__)
    def test_order_category(self, node_cls):
        node = node_cls(id="o")
        assert node.category == NodeCategory.ORDER


# ============================================================
# 2. 포트 검증
# ============================================================


class TestKiwoomNodePorts:
    """입출력 포트 검증"""

    def test_broker_output_is_connection(self):
        node = KiwoomBrokerNode(id="b")
        names = [p.name for p in node._outputs]
        assert "connection" in names

    def test_account_outputs(self):
        node = KiwoomAccountNode(id="a")
        names = [p.name for p in node._outputs]
        assert "held_symbols" in names
        assert "balance" in names
        assert "positions" in names

    def test_account_has_trigger_input(self):
        node = KiwoomAccountNode(id="a")
        names = [p.name for p in node._inputs]
        assert "trigger" in names

    def test_market_data_output_is_values(self):
        node = KiwoomMarketDataNode(id="m")
        names = [p.name for p in node._outputs]
        assert "values" in names

    def test_historical_outputs(self):
        node = KiwoomHistoricalDataNode(id="h")
        names = [p.name for p in node._outputs]
        assert "time_series" in names
        assert "values" in names

    def test_new_order_has_order_result(self):
        node = KiwoomNewOrderNode(id="n")
        names = [p.name for p in node._outputs]
        assert "result" in names

    def test_cancel_order_outputs(self):
        node = KiwoomCancelOrderNode(id="c")
        names = [p.name for p in node._outputs]
        assert "cancel_result" in names
        assert "cancelled_order_no" in names


# ============================================================
# 3. FieldSchema 검증
# ============================================================


class TestKiwoomFieldSchema:
    """FieldSchema 정합성 검증"""

    def test_broker_has_credential_and_paper_trading(self):
        schema = KiwoomBrokerNode.get_field_schema()
        assert "credential_id" in schema
        assert "paper_trading" in schema
        assert schema["credential_id"].credential_types == ["broker_kiwoom"]

    def test_account_has_no_fields(self):
        schema = KiwoomAccountNode.get_field_schema()
        assert schema == {}

    def test_market_data_has_symbols_field(self):
        schema = KiwoomMarketDataNode.get_field_schema()
        assert "symbols" in schema
        assert schema["symbols"].description.startswith("i18n:")

    def test_historical_has_symbol_and_count(self):
        schema = KiwoomHistoricalDataNode.get_field_schema()
        assert "symbol" in schema
        assert "count" in schema

    def test_new_order_has_side_order_type_order(self):
        schema = KiwoomNewOrderNode.get_field_schema()
        assert "side" in schema
        assert "order_type" in schema
        assert "order" in schema
        assert set(schema["side"].enum_values) == {"buy", "sell"}
        assert set(schema["order_type"].enum_values) == {"limit", "market"}

    def test_cancel_order_fields(self):
        schema = KiwoomCancelOrderNode.get_field_schema()
        assert "original_order_no" in schema
        # 키움 취소 api-id(kt10003)는 KIS와 달리 종목코드가 필수
        assert "symbol" in schema
        assert schema["symbol"].required is True
        assert "quantity" in schema


# ============================================================
# 4. NodeTypeRegistry 등록 확인
# ============================================================


class TestKiwoomRegistry:
    """NodeTypeRegistry 등록 확인"""

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_node_registered(self, node_cls):
        from programgarden_core.registry.node_registry import NodeTypeRegistry
        registry = NodeTypeRegistry()
        assert registry.get(node_cls.__name__) is not None

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_registry_schema_product_scope(self, node_cls):
        from programgarden_core.registry.node_registry import NodeTypeRegistry
        registry = NodeTypeRegistry()
        schema = registry.get_schema(node_cls.__name__)
        assert schema is not None
        assert schema.product_scope == "korea_stock"

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_registry_schema_broker_provider(self, node_cls):
        from programgarden_core.registry.node_registry import NodeTypeRegistry
        registry = NodeTypeRegistry()
        schema = registry.get_schema(node_cls.__name__)
        assert schema is not None
        assert schema.broker_provider == "kiwoom.com"


# ============================================================
# 5. is_tool_enabled 검증
# ============================================================


class TestKiwoomToolEnabled:
    """AI Agent 도구 활성화 검증"""

    @pytest.mark.parametrize("node_cls", [
        KiwoomAccountNode,
        KiwoomMarketDataNode,
        KiwoomHistoricalDataNode,
        KiwoomNewOrderNode,
    ], ids=lambda c: c.__name__)
    def test_tool_enabled_nodes(self, node_cls):
        assert node_cls.is_tool_enabled() is True

    @pytest.mark.parametrize("node_cls", [
        KiwoomBrokerNode,
        KiwoomCancelOrderNode,
    ], ids=lambda c: c.__name__)
    def test_tool_disabled_nodes(self, node_cls):
        assert node_cls.is_tool_enabled() is False


# ============================================================
# 6. i18n 키 존재 확인
# ============================================================


class TestKiwoomI18n:
    """i18n 번역 키 존재 확인"""

    @pytest.fixture(scope="class")
    def ko_translations(self):
        import json
        from pathlib import Path
        path = Path(__file__).parent.parent / "programgarden_core" / "i18n" / "locales" / "ko.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @pytest.fixture(scope="class")
    def en_translations(self):
        import json
        from pathlib import Path
        path = Path(__file__).parent.parent / "programgarden_core" / "i18n" / "locales" / "en.json"
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_ko_node_name_exists(self, ko_translations, node_cls):
        key = f"nodes.{node_cls.__name__}.name"
        assert key in ko_translations, f"Missing ko.json key: {key}"

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_ko_node_description_exists(self, ko_translations, node_cls):
        key = f"nodes.{node_cls.__name__}.description"
        assert key in ko_translations, f"Missing ko.json key: {key}"

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_en_node_name_exists(self, en_translations, node_cls):
        key = f"nodes.{node_cls.__name__}.name"
        assert key in en_translations, f"Missing en.json key: {key}"

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_en_node_description_exists(self, en_translations, node_cls):
        key = f"nodes.{node_cls.__name__}.description"
        assert key in en_translations, f"Missing en.json key: {key}"

    def test_ko_kiwoom_side_enums(self, ko_translations):
        assert "enums.kiwoom_side.buy" in ko_translations
        assert "enums.kiwoom_side.sell" in ko_translations

    def test_ko_kiwoom_order_type_enums(self, ko_translations):
        assert "enums.kiwoom_order_type.limit" in ko_translations
        assert "enums.kiwoom_order_type.market" in ko_translations

    def test_en_kiwoom_side_enums(self, en_translations):
        assert "enums.kiwoom_side.buy" in en_translations
        assert "enums.kiwoom_side.sell" in en_translations


# ============================================================
# 7. 직렬화 (JSON round-trip)
# ============================================================


class TestKiwoomSerialization:
    """Pydantic 직렬화/역직렬화"""

    @pytest.mark.parametrize("node_cls", ALL_KIWOOM_NODES, ids=lambda c: c.__name__)
    def test_json_round_trip(self, node_cls):
        node = node_cls(id="ser1")
        data = node.model_dump()
        restored = node_cls(**data)
        assert restored.id == "ser1"
        assert restored.type == node_cls.__name__

    def test_new_order_side_default(self):
        node = KiwoomNewOrderNode(id="o1")
        assert node.side == "buy"
        assert node.order_type == "limit"

    def test_broker_paper_trading_default(self):
        node = KiwoomBrokerNode(id="b1")
        assert node.paper_trading is False

    def test_historical_count_default(self):
        node = KiwoomHistoricalDataNode(id="h1")
        assert node.count == 30
        assert node.symbol == "005930"
