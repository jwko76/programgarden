"""deep_validate (virtual full-execution) tests.

Covers the Phase 1 contract from the deep-workflow-validation plan:

- Orders are never placed (no broker login, no order send) in deep mode.
- Realtime / data nodes return schema-shaped fixtures so the flow completes
  without waiting for live events (no hang).
- ScheduleNode fires once and the run terminates.
- Strict error collection: a single pass accumulates as many node errors as
  possible (does not abort on the first failure) and reports passed=False.
- Time-boxing: a hanging node still returns within the timeout.
- Zero network: data nodes (Account / MarketData) never call ensure_ls_login.

All tests run with a hard timeout to guarantee no test hangs.
"""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import programgarden.executor as executor_mod
from programgarden import ProgramGarden
from programgarden.context import ExecutionContext
from programgarden.executor import (
    AccountNodeExecutor,
    BrokerNodeExecutor,
    MarketDataNodeExecutor,
    NewOrderNodeExecutor,
    OpenOrdersNodeExecutor,
    RealAccountNodeExecutor,
    RealMarketDataNodeExecutor,
    RealOrderEventNodeExecutor,
    WorkflowExecutor,
)


pytestmark = pytest.mark.timeout(30)


# ============================================================
# Helpers
# ============================================================

def make_deep_context(job_id: str = "deep-test") -> ExecutionContext:
    ctx = ExecutionContext(
        job_id=job_id,
        workflow_id="wf-deep-test",
        context_params={"deep_validate": True},
    )
    ctx._is_running = True
    return ctx


def _broker_node(node_id: str = "broker", node_type: str = "OverseasStockBrokerNode") -> dict:
    return {"id": node_id, "type": node_type, "credential_id": "cred"}


def _credentials() -> list:
    return [
        {
            "credential_id": "cred",
            "type": "broker_ls_overseas_stock",
            "data": [
                {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
            ],
        }
    ]


def order_workflow() -> dict:
    """start → broker → account → new_order (overseas stock)."""
    return {
        "id": "wf-deep-order",
        "name": "deep order workflow",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            _broker_node(),
            {"id": "account", "type": "OverseasStockAccountNode"},
            {
                "id": "new_order",
                "type": "OverseasStockNewOrderNode",
                "config": {
                    "symbol": {"symbol": "AAPL", "exchange": "NASDAQ"},
                    "side": "buy",
                    "quantity": 1,
                    "order_type": "market",
                },
            },
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
            {"from": "account", "to": "new_order"},
        ],
        "credentials": _credentials(),
    }


# ============================================================
# 1. flag propagation
# ============================================================

def test_deep_validate_flag_is_dry_run_superset():
    ctx = make_deep_context()
    assert ctx.is_deep_validate is True
    assert ctx.is_dry_run is True  # superset


def test_plain_dry_run_is_not_deep():
    ctx = ExecutionContext(
        job_id="x", workflow_id="w", context_params={"dry_run": True}
    )
    assert ctx.is_dry_run is True
    assert ctx.is_deep_validate is False


# ============================================================
# 2. Orders are never placed; broker login never happens
# ============================================================

@pytest.mark.asyncio
async def test_order_workflow_places_no_real_order_and_no_login():
    """Deep-validating an order workflow must NOT log into the broker or send
    an order — every order node returns a simulated result."""
    pg = ProgramGarden()

    # If ensure_ls_login is ever called in deep mode, fail loudly.
    def _boom(*args, **kwargs):  # pragma: no cover - asserted via call_count
        raise AssertionError("ensure_ls_login must NOT be called in deep_validate")

    with patch.object(executor_mod, "ensure_ls_login", side_effect=_boom) as mock_login:
        result = await pg.executor.deep_validate(order_workflow(), timeout=12.0)

    assert mock_login.call_count == 0, "broker login must never happen in deep mode"
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_new_order_executor_simulates_in_deep_mode():
    """The order executor itself returns a simulated order (no LS call)."""
    ctx = make_deep_context()
    ex = NewOrderNodeExecutor()
    out = await ex.execute(
        node_id="new_order",
        node_type="OverseasStockNewOrderNode",
        config={"symbol": {"symbol": "AAPL", "exchange": "NASDAQ"}, "side": "buy", "quantity": 1},
        context=ctx,
    )
    assert out.get("status") == "simulated"
    assert str(out.get("order_id", "")).startswith("DRYRUN-")


# ============================================================
# 3. Realtime / data nodes return fixtures (no event wait, no network)
# ============================================================

@pytest.mark.asyncio
async def test_real_market_data_returns_fixture_in_deep_mode():
    ctx = make_deep_context()
    ex = RealMarketDataNodeExecutor()
    out = await ex.execute(
        node_id="rt",
        node_type="OverseasStockRealMarketDataNode",
        config={"symbols": [{"symbol": "TSLA", "exchange": "NASDAQ"}], "connection": {"product": "overseas_stock"}},
        context=ctx,
    )
    assert "ohlcv_data" in out and "data" in out
    assert "TSLA" in out["ohlcv_data"]
    bars = out["ohlcv_data"]["TSLA"]
    assert bars and all(k in bars[0] for k in ("date", "open", "high", "low", "close", "volume"))


@pytest.mark.asyncio
async def test_real_account_returns_fixture_positions_balance():
    ctx = make_deep_context()
    ex = RealAccountNodeExecutor()
    out = await ex.execute(
        node_id="acct",
        node_type="OverseasStockRealAccountNode",
        config={"symbols": [{"symbol": "AAPL", "exchange": "NASDAQ"}], "connection": {"product": "overseas_stock"}},
        context=ctx,
    )
    assert isinstance(out.get("positions"), list)
    assert isinstance(out.get("balance"), dict)
    assert "USD" in out["balance"]


@pytest.mark.asyncio
async def test_real_order_event_returns_simulated_fill():
    ctx = make_deep_context()
    ex = RealOrderEventNodeExecutor()
    out = await ex.execute(
        node_id="evt",
        node_type="OverseasStockRealOrderEventNode",
        config={"connection": {"product": "overseas_stock"}},
        context=ctx,
    )
    assert out.get("status") == "체결"
    assert "filled" in out and out["filled"].get("status") == "체결"


@pytest.mark.asyncio
async def test_account_node_fixture_no_login():
    """AccountNode (REST) had no dry_run guard — verify deep injects a fixture
    and never calls ensure_ls_login."""
    ctx = make_deep_context()
    ex = AccountNodeExecutor()
    with patch.object(executor_mod, "ensure_ls_login") as mock_login:
        out = await ex.execute(
            node_id="account",
            node_type="OverseasStockAccountNode",
            config={"connection": {"product": "overseas_stock"}},
            context=ctx,
        )
    assert mock_login.call_count == 0
    assert isinstance(out.get("positions"), list)
    assert isinstance(out.get("balance"), dict)


@pytest.mark.asyncio
async def test_market_data_node_fixture_no_login():
    ctx = make_deep_context()
    ex = MarketDataNodeExecutor()
    with patch.object(executor_mod, "ensure_ls_login") as mock_login:
        out = await ex.execute(
            node_id="md",
            node_type="OverseasStockMarketDataNode",
            config={"symbols": [{"symbol": "NVDA", "exchange": "NASDAQ"}], "connection": {"product": "overseas_stock"}},
            context=ctx,
        )
    assert mock_login.call_count == 0
    assert isinstance(out.get("values"), list) and out["values"]
    assert out["values"][0]["symbol"] == "NVDA"


@pytest.mark.asyncio
async def test_open_orders_fixture_no_network():
    ctx = make_deep_context()
    ex = OpenOrdersNodeExecutor()
    with patch.object(executor_mod, "ensure_ls_login") as mock_login:
        out = await ex.execute(
            node_id="oo",
            node_type="OverseasStockOpenOrdersNode",
            config={"connection": {"product": "overseas_stock"}},
            context=ctx,
        )
    assert mock_login.call_count == 0
    assert out.get("open_orders") == [] and out.get("count") == 0


@pytest.mark.asyncio
async def test_broker_node_fixture_connection_no_login():
    """BrokerNode deep returns a fixture connection without login/credential
    injection or fill-price sync (no network)."""
    ctx = make_deep_context()
    ex = BrokerNodeExecutor()
    with patch.object(executor_mod, "ensure_ls_login") as mock_login:
        out = await ex.execute(
            node_id="broker",
            node_type="OverseasStockBrokerNode",
            config={"credential_id": "cred", "product": "overseas_stock"},
            context=ctx,
        )
    assert mock_login.call_count == 0
    assert out.get("connected") is True
    assert out["connection"]["product"] == "overseas_stock"


# ============================================================
# 4. Fixture override
# ============================================================

@pytest.mark.asyncio
async def test_fixture_override_is_applied():
    ctx = ExecutionContext(
        job_id="ovr",
        workflow_id="w",
        context_params={
            "deep_validate": True,
            "deep_fixtures": {"md": {"values": [{"symbol": "ZZZ", "price": 999.0}]}},
        },
    )
    ctx._is_running = True
    ex = MarketDataNodeExecutor()
    out = await ex.execute(
        node_id="md",
        node_type="OverseasStockMarketDataNode",
        config={"symbols": [{"symbol": "AAPL", "exchange": "NASDAQ"}], "connection": {"product": "overseas_stock"}},
        context=ctx,
    )
    assert out["values"] == [{"symbol": "ZZZ", "price": 999.0}]


# ============================================================
# 5. End-to-end entry: realtime / schedule workflows complete
# ============================================================

@pytest.mark.asyncio
async def test_realtime_workflow_completes_without_event_wait():
    pg = ProgramGarden()
    wf = {
        "id": "wf-deep-realtime",
        "name": "deep realtime",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            _broker_node(),
            {"id": "watchlist", "type": "WatchlistNode", "config": {"symbols": [{"symbol": "AAPL", "exchange": "NASDAQ"}]}},
            {"id": "realtime", "type": "OverseasStockRealMarketDataNode", "config": {}},
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "watchlist"},
            {"from": "watchlist", "to": "realtime"},
        ],
        "credentials": _credentials(),
    }
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_schedule_workflow_fires_once_and_terminates():
    pg = ProgramGarden()
    wf = {
        "id": "wf-deep-sched",
        "name": "deep schedule",
        "nodes": [
            {"id": "sched", "type": "ScheduleNode", "config": {"cron": "0 9 * * *", "enabled": True}},
            {"id": "start", "type": "StartNode"},
        ],
        "edges": [{"from": "sched", "to": "start"}],
    }
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=10.0), timeout=18.0)
    assert result.is_valid, [e.short() for e in result.errors]


# ============================================================
# 6. Strict error collection (accumulate, do not abort on first failure)
# ============================================================

@pytest.mark.asyncio
async def test_deep_collects_multiple_node_errors_without_aborting():
    """Two independent nodes both raise → both surface in errors, and passed is
    False. This proves the deep pass keeps going after the first failure."""
    pg = ProgramGarden()
    wf = {
        "id": "wf-deep-multierr",
        "name": "deep multi error",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "a", "type": "WatchlistNode", "config": {"symbols": [{"symbol": "AAPL", "exchange": "NASDAQ"}]}},
            {"id": "b", "type": "WatchlistNode", "config": {"symbols": [{"symbol": "TSLA", "exchange": "NASDAQ"}]}},
        ],
        "edges": [
            {"from": "start", "to": "a"},
            {"from": "start", "to": "b"},
        ],
        "credentials": [],
    }

    real_execute_node = WorkflowExecutor.execute_node

    async def failing_execute_node(self, *, node_id, node_type, **kwargs):
        if node_id in ("a", "b"):
            raise RuntimeError(f"boom-{node_id}")
        return await real_execute_node(self, node_id=node_id, node_type=node_type, **kwargs)

    with patch.object(WorkflowExecutor, "execute_node", failing_execute_node):
        result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=10.0), timeout=18.0)

    assert not result.is_valid
    failed_nodes = {e.location.node_id for e in result.errors if e.location.node_id}
    assert {"a", "b"} <= failed_nodes, f"expected both a and b in {failed_nodes}"
    # deep errors use the dedicated code with a stage detail
    deep_errs = [e for e in result.errors if e.code == "DEEP_VALIDATION_NODE_ERROR"]
    assert len(deep_errs) >= 2
    assert all(e.details.get("stage") == "node_execution" for e in deep_errs)


@pytest.mark.asyncio
async def test_deep_reports_static_structure_errors_without_raising():
    """A definition that fails static schema validation returns a result (never
    raises) carrying the structure errors."""
    pg = ProgramGarden()
    bad = {"workflow_id": "no_id_or_name", "nodes": [], "edges": []}
    result = await asyncio.wait_for(pg.executor.deep_validate(bad, timeout=5.0), timeout=10.0)
    assert not result.is_valid
    assert result.errors  # structure errors surfaced, no exception


# ============================================================
# 7. Time-boxing: a hanging node still returns within timeout
# ============================================================

@pytest.mark.asyncio
async def test_deep_returns_within_timeout_on_hang():
    pg = ProgramGarden()
    wf = {
        "id": "wf-deep-hang",
        "name": "deep hang",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "slow", "type": "WatchlistNode", "config": {"symbols": [{"symbol": "AAPL", "exchange": "NASDAQ"}]}},
        ],
        "edges": [{"from": "start", "to": "slow"}],
        "credentials": [],
    }

    real_execute_node = WorkflowExecutor.execute_node

    async def hanging_execute_node(self, *, node_id, node_type, **kwargs):
        if node_id == "slow":
            await asyncio.sleep(60)  # would hang far past the timeout
        return await real_execute_node(self, node_id=node_id, node_type=node_type, **kwargs)

    loop = asyncio.get_event_loop()
    t0 = loop.time()
    with patch.object(WorkflowExecutor, "execute_node", hanging_execute_node):
        result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=2.0), timeout=12.0)
    elapsed = loop.time() - t0

    assert elapsed < 10.0, f"deep_validate should return near the 2s timeout, took {elapsed:.1f}s"
    assert not result.is_valid
    assert any(e.code == "DEEP_VALIDATION_FLOW_BROKEN" for e in result.errors)


# ============================================================
# 8. client.validate_deep (sync wrapper)
# ============================================================

def test_client_validate_deep_sync_wrapper():
    pg = ProgramGarden()
    result = pg.validate_deep(order_workflow(), timeout=12.0)
    assert result.is_valid, [e.short() for e in result.errors]


def test_sync_wrapper_does_not_pollute_main_thread_event_loop():
    """Regression guard (test isolation): the synchronous ``validate_deep`` /
    ``run`` wrappers must NOT leave the main thread without a current event loop.

    ``asyncio.run`` clears the thread's loop on exit; if the wrappers used it
    directly, a later ``asyncio.get_event_loop()`` (in legacy tests / sync user
    code running in the same process) would raise "There is no current event
    loop". The wrappers run their coroutine in a dedicated worker thread, so the
    main thread's loop state is untouched. Verified inline (before the autouse
    loop-restore fixture in conftest runs).
    """
    import asyncio

    loop_before = asyncio.new_event_loop()
    asyncio.set_event_loop(loop_before)
    try:
        pg = ProgramGarden()
        pg.validate_deep(order_workflow(), timeout=12.0)
        # The current loop must be unchanged (same object, still open) — the sync
        # wrapper neither closed it nor cleared it to None.
        loop_after = asyncio.get_event_loop()
        assert loop_after is loop_before, "sync wrapper replaced the main-thread loop"
        assert not loop_after.is_closed(), "sync wrapper closed the main-thread loop"
    finally:
        asyncio.set_event_loop(loop_before)
        loop_before.close()


# ============================================================
# 9. Phase 1.5 — faithful fixtures (schema-mirrored, sufficient OHLCV)
# ============================================================

def test_historical_fixture_mirrors_real_output_schema():
    """HistoricalDataNode real output is {value, values, symbols} where each
    entry is {symbol, exchange, time_series:[bars]} — NOT an ohlcv_data map.
    A faithful fixture must mirror that so the downstream ConditionNode (which
    auto-iterates `values` and reads `item.time_series`) sees the runtime shape.
    """
    from programgarden import deep_fixtures as df

    fx = df.historical_data_fixture(
        {"period": "1d"}, [{"symbol": "AAPL", "exchange": "NASDAQ"}]
    )
    assert set(fx) >= {"value", "values", "symbols"}
    assert fx["value"] is not None  # single symbol → populated value port
    assert isinstance(fx["values"], list) and fx["values"]
    entry = fx["values"][0]
    assert set(entry) >= {"symbol", "exchange", "time_series"}
    assert entry["symbol"] == "AAPL"
    bars = entry["time_series"]
    assert all(k in bars[0] for k in ("date", "open", "high", "low", "close", "volume"))


def test_historical_fixture_has_enough_bars_for_rsi():
    """The series must be long enough that RSI(14)/Bollinger(20) compute a real
    value rather than a 'data too short' sentinel (Phase 1 false-positive root)."""
    from programgarden import deep_fixtures as df

    fx = df.historical_data_fixture({}, [{"symbol": "AAPL", "exchange": "NASDAQ"}])
    bars = fx["values"][0]["time_series"]
    assert len(bars) >= 30, f"need >=30 bars for indicator computation, got {len(bars)}"


def test_account_fixture_has_a_losing_position():
    """At least one held position must be underwater so per-position stop-loss
    conditions actually trigger during a deep run (else the risk branch is never
    exercised — a false negative)."""
    from programgarden import deep_fixtures as df

    positions = df._fixture_positions(
        {}, [{"symbol": "AAPL", "exchange": "NASDAQ"}, {"symbol": "TSLA", "exchange": "NASDAQ"}]
    )
    assert any(p["pnl_rate"] < 0 for p in positions), "expected a losing position"


# ============================================================
# 10. Phase 1.5 — ConditionNode / SymbolFilter deep flow guarantee
# ============================================================

@pytest.mark.asyncio
async def test_condition_node_passes_input_symbols_in_deep_mode():
    """A signal gate in deep mode must let at least its input symbols through so
    the downstream sizing/order/notify branch (and its {{ item.* }} bindings) is
    exercised regardless of whether the fixture series fires the indicator."""
    from programgarden.executor import ConditionNodeExecutor

    ctx = make_deep_context()
    # Seed a historical-shaped input the ConditionNode RSI plugin can read.
    from programgarden import deep_fixtures as df
    hist = df.historical_data_fixture({}, [{"symbol": "AAPL", "exchange": "NASDAQ"}])
    ctx.set_output("hist", "values", hist["values"])
    ctx.set_iteration_context(hist["values"][0], 0, 1)

    ex = ConditionNodeExecutor()
    out = await ex.execute(
        node_id="rsi",
        node_type="ConditionNode",
        config={
            "plugin": "RSI",
            "items": {
                "from": "{{ item.time_series }}",
                "extract": {
                    "symbol": "{{ item.symbol }}",
                    "exchange": "{{ item.exchange }}",
                    "date": "{{ row.date }}",
                    "close": "{{ row.close }}",
                },
            },
            "fields": {"period": 14, "threshold": 30, "direction": "above"},
        },
        context=ctx,
        fields={"period": 14, "threshold": 30, "direction": "above"},
    )
    # direction=above on a declining-tail series would normally fail; deep mode
    # guarantees the input symbols flow through anyway.
    assert out.get("passed_symbols"), "deep mode should pass input symbols through"
    assert out.get("result") is True


@pytest.mark.asyncio
async def test_symbol_filter_falls_back_to_input_a_in_deep_mode():
    """A difference that empties out (all candidates already held) must not gate
    the downstream branch in deep mode — fall back to input_a."""
    from programgarden.executor import SymbolFilterNodeExecutor

    ctx = make_deep_context()
    ex = SymbolFilterNodeExecutor()
    held = [{"symbol": "AAPL", "exchange": "NASDAQ"}]
    out = await ex.execute(
        node_id="filter",
        node_type="SymbolFilterNode",
        config={"operation": "difference", "input_a": held, "input_b": held},
        context=ctx,
    )
    assert out["symbols"], "deep mode should not leave the filter empty"
    assert out["symbols"][0]["symbol"] == "AAPL"


@pytest.mark.asyncio
async def test_symbol_filter_keeps_real_result_in_dry_run():
    """The fallback is deep-only — plain dry_run keeps the exact set-op result."""
    from programgarden.executor import SymbolFilterNodeExecutor

    ctx = ExecutionContext(job_id="x", workflow_id="w", context_params={"dry_run": True})
    ctx._is_running = True
    ex = SymbolFilterNodeExecutor()
    held = [{"symbol": "AAPL", "exchange": "NASDAQ"}]
    out = await ex.execute(
        node_id="filter",
        node_type="SymbolFilterNode",
        config={"operation": "difference", "input_a": held, "input_b": held},
        context=ctx,
    )
    assert out["symbols"] == [], "dry_run must keep the empty difference result"


# ============================================================
# 11. Phase 1.5 — unresolved binding promotion
# ============================================================

def test_unresolved_binding_recorded_only_in_deep_mode():
    deep = make_deep_context()
    deep.record_deep_unresolved_binding("n", "{{ item.x }}", "undefined")
    assert deep.get_deep_unresolved_bindings() == [
        {"node_id": "n", "expression": "{{ item.x }}", "reason": "undefined"}
    ]
    # dedup on (node, expression)
    deep.record_deep_unresolved_binding("n", "{{ item.x }}", "undefined again")
    assert len(deep.get_deep_unresolved_bindings()) == 1

    dry = ExecutionContext(job_id="x", workflow_id="w", context_params={"dry_run": True})
    dry.record_deep_unresolved_binding("n", "{{ item.x }}", "undefined")
    assert dry.get_deep_unresolved_bindings() == [], "no-op outside deep mode"


@pytest.mark.asyncio
async def test_unresolved_item_binding_blocks_deep_validate():
    """An IfNode using `{{ item.pnl_rate }}` (which never resolves at runtime —
    IfNode has no iteration context) must be flagged as a blocking
    DEEP_VALIDATION_BINDING_UNRESOLVED error, not silently pass."""
    pg = ProgramGarden()
    wf = {
        "id": "wf-deep-item-bug",
        "name": "if-node item anti-pattern",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            _broker_node(),
            {"id": "account", "type": "OverseasStockAccountNode"},
            {"id": "gate", "type": "IfNode", "left": "{{ item.pnl_rate }}", "operator": "<=", "right": -5},
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
            {"from": "account", "to": "gate"},
        ],
        "credentials": _credentials(),
    }
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    assert not result.is_valid
    binding_errs = [e for e in result.errors if e.code == "DEEP_VALIDATION_BINDING_UNRESOLVED"]
    assert binding_errs, [e.short() for e in result.errors]
    assert "item" in binding_errs[0].message


@pytest.mark.asyncio
async def test_faithful_workflow_passes_deep_validate():
    """A correctly-wired multi-symbol workflow (watchlist → market → sizing with
    sizing auto-iterating) passes deep_validate with the faithful fixtures."""
    pg = ProgramGarden()
    wf = {
        "id": "wf-deep-faithful",
        "name": "faithful sizing",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            _broker_node(),
            {"id": "account", "type": "OverseasStockAccountNode"},
            {"id": "watchlist", "type": "WatchlistNode", "config": {"symbols": [{"symbol": "AAPL", "exchange": "NASDAQ"}]}},
            {"id": "market", "type": "OverseasStockMarketDataNode"},
            {
                "id": "sizing",
                "type": "PositionSizingNode",
                "symbol": "{{ item }}",
                "balance": "{{ nodes.account.balance.orderable_amount }}",
                "market_data": "{{ nodes.market.value }}",
                "method": "fixed_percent",
                "max_percent": 10.0,
            },
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
            {"from": "watchlist", "to": "market"},
            {"from": "account", "to": "sizing"},
            {"from": "market", "to": "sizing"},
        ],
        "credentials": _credentials(),
    }
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    assert result.is_valid, [e.short() for e in result.errors]


# ============================================================
# 12. Phase 1.5 — auto-iterate pacing skipped in deep mode (timebox)
# ============================================================

@pytest.mark.asyncio
async def test_auto_iterate_pacing_skipped_in_deep_mode():
    """The per-item rate-limit pacing models a real broker API limit; in deep
    mode (no real calls) it must be skipped so a wide watchlist does not blow the
    timebox."""
    ctx = make_deep_context()
    ex = WorkflowExecutor()
    job = WorkflowExecutor.__new__(WorkflowExecutor)  # not needed; use a job-bound sleep check

    # Build a minimal job that carries the deep context and call the pacing helper.
    from programgarden.executor import WorkflowJob
    job = WorkflowJob.__new__(WorkflowJob)
    job.context = ctx
    slept = []

    import programgarden.executor as exmod
    orig_sleep = asyncio.sleep

    async def spy_sleep(d, *a, **k):
        slept.append(d)
        return await orig_sleep(0)

    with patch.object(exmod.asyncio, "sleep", spy_sleep):
        # Even a node type that has a rate limit must not sleep in deep mode.
        await WorkflowJob._auto_iterate_pacing_sleep(job, "new_order", "OverseasStockNewOrderNode")
    assert slept == [], "deep mode must not pace-sleep"


# ============================================================
# 13. Phase 1.5 — Pydantic field/type error promotion (deep only)
# ============================================================

@pytest.mark.asyncio
async def test_generic_node_invalid_config_raises_in_deep_mode():
    """GenericNodeExecutor: a Pydantic construction failure (bad/extra field)
    must RAISE in deep mode so the main loop captures a blocking node error,
    rather than returning a silent {"error": ...} output that marks the node
    completed and hides the defect from deep_validate."""
    from programgarden.executor import GenericNodeExecutor

    ctx = make_deep_context()
    ex = GenericNodeExecutor()
    # SQLiteNode.query expects a string; an int fails Pydantic construction.
    with pytest.raises(Exception):
        await ex.execute(
            node_id="sql",
            node_type="SQLiteNode",
            config={"query": 123},
            context=ctx,
        )


@pytest.mark.asyncio
async def test_generic_node_invalid_config_lenient_in_dry_run():
    """The raise is deep-only — plain dry_run keeps the lenient {"error": ...}
    output so existing mocked validation flows are unaffected."""
    from programgarden.executor import GenericNodeExecutor

    ctx = ExecutionContext(job_id="x", workflow_id="w", context_params={"dry_run": True})
    ctx._is_running = True
    ex = GenericNodeExecutor()
    out = await ex.execute(
        node_id="sql",
        node_type="SQLiteNode",
        config={"query": 123},
        context=ctx,
    )
    assert isinstance(out, dict)
    assert "error" in out, "dry_run must keep lenient error output"


# ============================================================
# 14. Static binding scan — display/non-evaluate_all_bindings executors
#
# Some executors (DisplayNode / TableDisplayNode / Fundamental / Backtest /
# Portfolio / LLM / AIAgent / SQLite ...) never call evaluate_all_bindings, so a
# `{{ }}` expression in their config fields (data / title / limit ...) used to
# slip past deep_validate entirely. The static binding scan in
# `_resolve_config_expressions` (deep mode) now evaluates those leaves per-field
# and records unresolved ones as DEEP_VALIDATION_BINDING_UNRESOLVED, while a C1
# guard keeps mid-iteration `{{ item.* }}` / `{{ row.* }}` from false-rejecting
# correct examples.
# ============================================================

_EXAMPLES_DIR = (
    Path(__file__).resolve().parent / ".." / "examples" / "workflows"
).resolve()


def _load_example(name: str) -> dict:
    """Load an examples/workflows/<name>.json workflow definition."""
    return json.loads((_EXAMPLES_DIR / f"{name}.json").read_text())


@pytest.mark.asyncio
async def test_display_node_unsupported_filter_binding_is_caught():
    """A TableDisplayNode `data` field using an unsupported pipe filter
    (`{{ ... | length }}`) — which never resolves at runtime — must now be
    flagged as a blocking DEEP_VALIDATION_BINDING_UNRESOLVED, not silently pass.

    TableDisplayNode does not call evaluate_all_bindings, so before the static
    binding scan this slipped through deep_validate (is_valid=True)."""
    pg = ProgramGarden()
    wf = _load_example("22-display-table")
    for node in wf["nodes"]:
        if node["id"] == "table":
            node["data"] = "{{ nodes.account.positions | length }}"
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    assert not result.is_valid, [e.short() for e in result.errors]
    binding_errs = [e for e in result.errors if e.code == "DEEP_VALIDATION_BINDING_UNRESOLVED"]
    assert binding_errs, [e.short() for e in result.errors]
    assert "length" in binding_errs[0].message or "| length" in binding_errs[0].message


@pytest.mark.asyncio
async def test_display_node_undefined_variable_binding_is_caught():
    """A DisplayNode `title` referencing an undefined variable must be flagged as
    DEEP_VALIDATION_BINDING_UNRESOLVED (would keep its literal text at runtime)."""
    pg = ProgramGarden()
    wf = _load_example("22-display-table")
    for node in wf["nodes"]:
        if node["id"] == "table":
            node["title"] = "{{ bogus_undefined_var }}"
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    assert not result.is_valid, [e.short() for e in result.errors]
    binding_errs = [e for e in result.errors if e.code == "DEEP_VALIDATION_BINDING_UNRESOLVED"]
    assert binding_errs, [e.short() for e in result.errors]
    assert "bogus_undefined_var" in binding_errs[0].message


@pytest.mark.asyncio
async def test_unmodified_display_table_example_still_passes():
    """The pristine 22-display-table example (data = `{{ nodes.account.positions }}`,
    a fully-resolvable binding) must remain valid with zero errors — the scan must
    not introduce a false positive on a correct DisplayNode."""
    pg = ProgramGarden()
    wf = _load_example("22-display-table")
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    assert result.is_valid, [e.short() for e in result.errors]
    binding_errs = [e for e in result.errors if e.code == "DEEP_VALIDATION_BINDING_UNRESOLVED"]
    assert not binding_errs, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_c1_guard_nested_item_binding_not_false_rejected():
    """C1 guard: the 30-liquidate-futures example wires nested `{{ item.symbol }}`
    / `{{ item.quantity }}` etc. inside the order node's `order` dict. These are
    auto-iterate bindings that only resolve mid-iteration; the static scan must
    NOT record them as unresolved (would false-reject a correct example).

    Proves the C1 reserved-iteration-root guard is load-bearing: the example must
    have zero DEEP_VALIDATION_BINDING_UNRESOLVED errors and stay valid."""
    pg = ProgramGarden()
    wf = _load_example("30-liquidate-futures-positions")
    result = await asyncio.wait_for(pg.executor.deep_validate(wf, timeout=12.0), timeout=20.0)
    binding_errs = [e for e in result.errors if e.code == "DEEP_VALIDATION_BINDING_UNRESOLVED"]
    assert not binding_errs, (
        "nested {{ item.* }} must not be false-rejected: "
        + str([e.short() for e in binding_errs])
    )
    assert result.is_valid, [e.short() for e in result.errors]


def test_free_root_names_does_not_raise_on_unparseable_source():
    """_free_root_names must not raise on a value `ast.parse` can't even
    encode (e.g. a lone surrogate char) — that would drop the whole node's
    binding scan (false-negative). It must return the `__syntax_error__`
    sentinel so the expression is still recorded as a real defect.

    `ast.parse` raises ValueError (incl. UnicodeEncodeError) on surrogate
    chars, not SyntaxError, so the guard must catch (SyntaxError, ValueError).
    """
    from programgarden.executor import _free_root_names

    roots = _free_root_names("{{ \udcff }}")
    assert "__syntax_error__" in roots


# ============================================================
# Bithumb (코인) deep_validate tests
# ============================================================

def _bithumb_credentials() -> list:
    return [
        {
            "credential_id": "bithumb_cred",
            "type": "broker_bithumb",
            "data": [
                {"key": "access_key", "value": "", "type": "password", "label": "Access Key"},
                {"key": "secret_key", "value": "", "type": "password", "label": "Secret Key"},
            ],
        }
    ]


def bithumb_account_workflow() -> dict:
    """start → BithumbBroker → BithumbAccount."""
    return {
        "id": "wf-bithumb-account",
        "name": "bithumb account deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
            {"id": "account", "type": "BithumbAccountNode"},
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
        ],
        "credentials": _bithumb_credentials(),
    }


def bithumb_order_workflow() -> dict:
    """start → BithumbBroker → BithumbAccount → BithumbNewOrder."""
    return {
        "id": "wf-bithumb-order",
        "name": "bithumb order deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "broker", "type": "BithumbBrokerNode", "credential_id": "bithumb_cred"},
            {"id": "account", "type": "BithumbAccountNode"},
            {
                "id": "buy",
                "type": "BithumbNewOrderNode",
                "side": "bid",
                "order_type": "price",
                "order": {"market": "KRW-BTC", "price": "50000"},
            },
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
            {"from": "account", "to": "buy"},
        ],
        "credentials": _bithumb_credentials(),
    }


@pytest.mark.asyncio
async def test_bithumb_account_deep_validate_passes():
    """BithumbBrokerNode → BithumbAccountNode must deep-validate cleanly.
    No real API call should be made — fixture is returned instead."""
    pg = ProgramGarden()
    result = await asyncio.wait_for(
        pg.executor.deep_validate(bithumb_account_workflow(), timeout=12.0),
        timeout=20.0,
    )
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_bithumb_market_data_standalone_deep_validate():
    """BithumbMarketDataNode requires no broker — must pass standalone."""
    pg = ProgramGarden()
    wf = {
        "id": "wf-bithumb-market",
        "name": "bithumb market data deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "market", "type": "BithumbMarketDataNode", "markets": "KRW-BTC,KRW-ETH"},
        ],
        "edges": [{"from": "start", "to": "market"}],
        "credentials": [],
    }
    result = await asyncio.wait_for(
        pg.executor.deep_validate(wf, timeout=12.0),
        timeout=20.0,
    )
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_bithumb_order_deep_validate_no_real_api_call():
    """Deep-validating a Bithumb order workflow must NOT call the real Bithumb API.
    BithumbNewOrderNode must return a simulated result."""
    pg = ProgramGarden()

    # Patch _make_bithumb_client so any real call fails loudly
    import programgarden.bithumb_executors as bx_mod

    def _boom(*args, **kwargs):  # pragma: no cover
        raise AssertionError("_make_bithumb_client must NOT be called in deep_validate")

    with patch.object(bx_mod, "_make_bithumb_client", side_effect=_boom) as mock_client:
        result = await asyncio.wait_for(
            pg.executor.deep_validate(bithumb_order_workflow(), timeout=12.0),
            timeout=20.0,
        )

    assert mock_client.call_count == 0, "Bithumb API must never be called in deep mode"
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_bithumb_account_fixture_shape():
    """BithumbAccountNodeExecutor in deep mode returns correct fixture shape."""
    from programgarden.bithumb_executors import BithumbAccountNodeExecutor

    ctx = make_deep_context()
    ex = BithumbAccountNodeExecutor()
    out = await ex.execute(
        node_id="account",
        node_type="BithumbAccountNode",
        config={"connection": {"provider": "bithumb.com", "access_key": "x", "secret_key": "y"}},
        context=ctx,
    )
    assert "balance" in out
    assert "positions" in out
    assert "held_symbols" in out
    assert out["balance"]["krw_balance"] > 0


@pytest.mark.asyncio
async def test_bithumb_market_data_fixture_shape():
    """BithumbMarketDataNodeExecutor in deep mode returns correct fixture shape."""
    from programgarden.bithumb_executors import BithumbMarketDataNodeExecutor

    ctx = make_deep_context()
    ex = BithumbMarketDataNodeExecutor()
    out = await ex.execute(
        node_id="market",
        node_type="BithumbMarketDataNode",
        config={"markets": "KRW-BTC,KRW-ETH"},
        context=ctx,
    )
    assert "values" in out
    values = out["values"]
    assert len(values) == 2
    assert values[0]["market"] == "KRW-BTC"
    assert values[1]["market"] == "KRW-ETH"
    assert all("trade_price" in v for v in values)


# ============================================================
# KIS (한국투자증권 국내주식) deep_validate tests
# ============================================================

def _kis_credentials() -> list:
    return [
        {
            "credential_id": "kis_cred",
            "type": "broker_kis",
            "data": [
                {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
                {"key": "account_product_code", "value": "01", "type": "text", "label": "상품코드"},
            ],
        }
    ]


def kis_account_workflow() -> dict:
    """start → KisBroker(모의) → KisAccount."""
    return {
        "id": "wf-kis-account",
        "name": "kis account deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
            {"id": "account", "type": "KisAccountNode"},
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
        ],
        "credentials": _kis_credentials(),
    }


def kis_order_workflow() -> dict:
    """start → KisBroker(모의) → KisAccount → KisNewOrder."""
    return {
        "id": "wf-kis-order",
        "name": "kis order deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
            {"id": "account", "type": "KisAccountNode"},
            {
                "id": "buy",
                "type": "KisNewOrderNode",
                "side": "buy",
                "order_type": "limit",
                "order": {"symbol": "005930", "quantity": "10", "price": "60000"},
            },
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
            {"from": "account", "to": "buy"},
        ],
        "credentials": _kis_credentials(),
    }


@pytest.mark.asyncio
async def test_kis_account_deep_validate_passes():
    """KisBrokerNode → KisAccountNode must deep-validate cleanly.
    No real API call should be made — fixture is returned instead."""
    pg = ProgramGarden()
    result = await asyncio.wait_for(
        pg.executor.deep_validate(kis_account_workflow(), timeout=12.0),
        timeout=20.0,
    )
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_kis_order_deep_validate_no_real_api_call():
    """Deep-validating a KIS order workflow must NOT call the real KIS API.
    토큰 발급 자체가 라이브 호출이므로 _make_kis_client는 절대 호출되면 안 됩니다."""
    pg = ProgramGarden()

    import programgarden.kis_executors as kx_mod

    def _boom(*args, **kwargs):  # pragma: no cover
        raise AssertionError("_make_kis_client must NOT be called in deep_validate")

    with patch.object(kx_mod, "_make_kis_client", side_effect=_boom) as mock_client:
        result = await asyncio.wait_for(
            pg.executor.deep_validate(kis_order_workflow(), timeout=12.0),
            timeout=20.0,
        )

    assert mock_client.call_count == 0, "KIS API must never be called in deep mode"
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_kis_ls_multi_broker_deep_validate_passes():
    """LS KoreaStockBrokerNode + KisBrokerNode 공존 워크플로우가 deep-validate를 통과해야 합니다.
    각 계좌 노드는 자기 프로바이더의 connection에 바인딩됩니다."""
    pg = ProgramGarden()
    wf = {
        "id": "wf-kis-ls-multi",
        "name": "kis ls multi broker deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "ls_broker", "type": "KoreaStockBrokerNode", "credential_id": "ls_cred"},
            {"id": "kis_broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
            {"id": "ls_account", "type": "KoreaStockAccountNode"},
            {"id": "kis_account", "type": "KisAccountNode"},
        ],
        "edges": [
            {"from": "start", "to": "ls_broker"},
            {"from": "start", "to": "kis_broker"},
            {"from": "ls_broker", "to": "ls_account"},
            {"from": "kis_broker", "to": "kis_account"},
        ],
        "credentials": _kis_credentials() + [
            {
                "credential_id": "ls_cred",
                "type": "broker_ls_korea_stock",
                "data": [
                    {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                    {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                ],
            }
        ],
    }
    result = await asyncio.wait_for(
        pg.executor.deep_validate(wf, timeout=12.0),
        timeout=20.0,
    )
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_kis_account_fixture_shape():
    """KisAccountNodeExecutor in deep mode returns correct fixture shape."""
    from programgarden.kis_executors import KisAccountNodeExecutor

    ctx = make_deep_context()
    ex = KisAccountNodeExecutor()
    out = await ex.execute(
        node_id="account",
        node_type="KisAccountNode",
        config={"connection": {"provider": "koreainvestment.com", "appkey": "x", "appsecret": "y"}},
        context=ctx,
    )
    assert "balance" in out
    assert "positions" in out
    assert "held_symbols" in out
    assert out["balance"]["orderable_amount"] > 0


@pytest.mark.asyncio
async def test_kis_market_data_fixture_shape():
    """KisMarketDataNodeExecutor in deep mode returns correct fixture shape."""
    from programgarden.kis_executors import KisMarketDataNodeExecutor

    ctx = make_deep_context()
    ex = KisMarketDataNodeExecutor()
    out = await ex.execute(
        node_id="market",
        node_type="KisMarketDataNode",
        config={"symbols": "005930,000660"},
        context=ctx,
    )
    assert "values" in out
    values = out["values"]
    assert len(values) == 2
    assert values[0]["symbol"] == "005930"
    assert values[1]["symbol"] == "000660"
    assert all("current_price" in v for v in values)


@pytest.mark.asyncio
async def test_kis_historical_fixture_shape():
    """KisHistoricalDataNodeExecutor in deep mode returns ConditionNode-ready shape."""
    from programgarden.kis_executors import KisHistoricalDataNodeExecutor

    ctx = make_deep_context()
    ex = KisHistoricalDataNodeExecutor()
    out = await ex.execute(
        node_id="candles",
        node_type="KisHistoricalDataNode",
        config={"symbol": "005930", "count": 30},
        context=ctx,
    )
    assert "values" in out and "time_series" in out
    series = out["time_series"]
    assert len(series) == 1
    assert series[0]["symbol"] == "005930"
    assert series[0]["exchange"] == "KRX"
    candles = series[0]["time_series"]
    assert len(candles) == 30
    # time_series는 oldest-first — 날짜 오름차순
    assert candles[0]["date"] < candles[-1]["date"]
    assert all("close" in c for c in candles)


# ============================================================
# Kiwoom (키움증권 국내주식) deep_validate tests
# ============================================================

def _kiwoom_credentials() -> list:
    return [
        {
            "credential_id": "kiwoom_cred",
            "type": "broker_kiwoom",
            "data": [
                {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                {"key": "account_no", "value": "", "type": "text", "label": "계좌번호"},
            ],
        }
    ]


def kiwoom_account_workflow() -> dict:
    """start → KiwoomBroker(모의) → KiwoomAccount."""
    return {
        "id": "wf-kiwoom-account",
        "name": "kiwoom account deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
            {"id": "account", "type": "KiwoomAccountNode"},
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
        ],
        "credentials": _kiwoom_credentials(),
    }


def kiwoom_order_workflow() -> dict:
    """start → KiwoomBroker(모의) → KiwoomAccount → KiwoomNewOrder → KiwoomCancelOrder."""
    return {
        "id": "wf-kiwoom-order",
        "name": "kiwoom order deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
            {"id": "account", "type": "KiwoomAccountNode"},
            {
                "id": "buy",
                "type": "KiwoomNewOrderNode",
                "side": "buy",
                "order_type": "limit",
                "order": {"symbol": "005930", "quantity": "10", "price": "60000"},
            },
            {
                "id": "cancel",
                "type": "KiwoomCancelOrderNode",
                "original_order_no": "{{ nodes.buy.result.order_no }}",
                "symbol": "{{ nodes.buy.result.symbol }}",
            },
        ],
        "edges": [
            {"from": "start", "to": "broker"},
            {"from": "broker", "to": "account"},
            {"from": "account", "to": "buy"},
            {"from": "buy", "to": "cancel"},
        ],
        "credentials": _kiwoom_credentials(),
    }


@pytest.mark.asyncio
async def test_kiwoom_account_deep_validate_passes():
    """KiwoomBrokerNode → KiwoomAccountNode must deep-validate cleanly.
    No real API call should be made — fixture is returned instead."""
    pg = ProgramGarden()
    result = await asyncio.wait_for(
        pg.executor.deep_validate(kiwoom_account_workflow(), timeout=12.0),
        timeout=20.0,
    )
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_kiwoom_order_deep_validate_no_real_api_call():
    """Deep-validating a Kiwoom order workflow must NOT call the real Kiwoom API.
    토큰 발급 자체가 라이브 호출이므로 _make_kiwoom_client는 절대 호출되면 안 됩니다."""
    pg = ProgramGarden()

    import programgarden.kiwoom_executors as kw_mod

    def _boom(*args, **kwargs):  # pragma: no cover
        raise AssertionError("_make_kiwoom_client must NOT be called in deep_validate")

    with patch.object(kw_mod, "_make_kiwoom_client", side_effect=_boom) as mock_client:
        result = await asyncio.wait_for(
            pg.executor.deep_validate(kiwoom_order_workflow(), timeout=12.0),
            timeout=20.0,
        )

    assert mock_client.call_count == 0, "Kiwoom API must never be called in deep mode"
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_kiwoom_ls_kis_three_broker_deep_validate_passes():
    """LS + KIS + 키움 3사 브로커 공존 워크플로우가 deep-validate를 통과해야 합니다.
    각 계좌 노드는 자기 프로바이더의 connection에 바인딩됩니다."""
    pg = ProgramGarden()
    wf = {
        "id": "wf-kiwoom-ls-kis-multi",
        "name": "kiwoom ls kis multi broker deep",
        "nodes": [
            {"id": "start", "type": "StartNode"},
            {"id": "ls_broker", "type": "KoreaStockBrokerNode", "credential_id": "ls_cred"},
            {"id": "kis_broker", "type": "KisBrokerNode", "credential_id": "kis_cred", "paper_trading": True},
            {"id": "kiwoom_broker", "type": "KiwoomBrokerNode", "credential_id": "kiwoom_cred", "paper_trading": True},
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
        "credentials": _kiwoom_credentials() + _kis_credentials() + [
            {
                "credential_id": "ls_cred",
                "type": "broker_ls_korea_stock",
                "data": [
                    {"key": "appkey", "value": "", "type": "password", "label": "App Key"},
                    {"key": "appsecret", "value": "", "type": "password", "label": "App Secret"},
                ],
            }
        ],
    }
    result = await asyncio.wait_for(
        pg.executor.deep_validate(wf, timeout=12.0),
        timeout=20.0,
    )
    assert result.is_valid, [e.short() for e in result.errors]


@pytest.mark.asyncio
async def test_kiwoom_account_fixture_shape():
    """KiwoomAccountNodeExecutor in deep mode returns correct fixture shape."""
    from programgarden.kiwoom_executors import KiwoomAccountNodeExecutor

    ctx = make_deep_context()
    ex = KiwoomAccountNodeExecutor()
    out = await ex.execute(
        node_id="account",
        node_type="KiwoomAccountNode",
        config={"connection": {"provider": "kiwoom.com", "appkey": "x", "appsecret": "y"}},
        context=ctx,
    )
    assert "balance" in out
    assert "positions" in out
    assert "held_symbols" in out
    assert out["balance"]["orderable_amount"] > 0


@pytest.mark.asyncio
async def test_kiwoom_market_data_fixture_shape():
    """KiwoomMarketDataNodeExecutor in deep mode returns correct fixture shape."""
    from programgarden.kiwoom_executors import KiwoomMarketDataNodeExecutor

    ctx = make_deep_context()
    ex = KiwoomMarketDataNodeExecutor()
    out = await ex.execute(
        node_id="market",
        node_type="KiwoomMarketDataNode",
        config={"symbols": "005930,000660"},
        context=ctx,
    )
    assert "values" in out
    values = out["values"]
    assert len(values) == 2
    assert values[0]["symbol"] == "005930"
    assert values[1]["symbol"] == "000660"
    assert all("current_price" in v for v in values)


@pytest.mark.asyncio
async def test_kiwoom_historical_fixture_shape():
    """KiwoomHistoricalDataNodeExecutor in deep mode returns ConditionNode-ready shape."""
    from programgarden.kiwoom_executors import KiwoomHistoricalDataNodeExecutor

    ctx = make_deep_context()
    ex = KiwoomHistoricalDataNodeExecutor()
    out = await ex.execute(
        node_id="candles",
        node_type="KiwoomHistoricalDataNode",
        config={"symbol": "005930", "count": 30},
        context=ctx,
    )
    assert "values" in out and "time_series" in out
    series = out["time_series"]
    assert len(series) == 1
    assert series[0]["symbol"] == "005930"
    assert series[0]["exchange"] == "KRX"
    candles = series[0]["time_series"]
    assert len(candles) == 30
    # time_series는 oldest-first — 날짜 오름차순
    assert candles[0]["date"] < candles[-1]["date"]
    assert all("close" in c for c in candles)
