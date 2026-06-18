"""빗썸(Bithumb) 노드 executor 구현.

BithumbBrokerNodeExecutor, BithumbAccountNodeExecutor,
BithumbMarketDataNodeExecutor, BithumbNewOrderNodeExecutor,
BithumbCancelOrderNodeExecutor — 각각 빗썸 OpenAPI를 직접 호출합니다.

LS증권 executor와의 주요 차이:
- OAuth 토큰 없음 — 요청마다 HS256 JWT 자동 생성 (``auth.build_authorization_header``)
- 인증 정보: access_key + secret_key (appkey/appsecret 아님)
- credential 타입: ``broker_bithumb``
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

logger = logging.getLogger("programgarden.bithumb")


# executor.py와의 순환 참조를 피하기 위해 standalone 베이스 클래스를 정의합니다.
# NodeExecutorBase의 _inject_credentials를 인라인으로 재현합니다.

class _BithumbExecutorBase:
    """빗썸 executor 공통 베이스. executor.py 순환 참조 없이 동작합니다."""

    def _inject_credentials(self, credential_id, config, context, node_id):
        cred_data = context.get_workflow_credential(credential_id)
        if cred_data:
            config = config.copy()
            injected = []
            for key, value in cred_data.items():
                if config.get(key) is None and value:
                    config[key] = value
                    injected.append(key)
            if injected:
                context.log("debug", f"Bithumb credentials injected: {', '.join(injected)}", node_id)
        else:
            context.log("warning", f"Credential '{credential_id}' not found", node_id)
        return config


def _evaluate_all_bindings(config, context, node_id):
    """executor.py의 evaluate_all_bindings를 lazy import해서 호출합니다."""
    from programgarden.executor import evaluate_all_bindings
    return evaluate_all_bindings(config, context, node_id)


# ──────────────────────────────────────────────────────────────────── helpers ──


def _get_bithumb_credentials(connection: Dict[str, Any]) -> tuple[str, str]:
    """connection dict에서 access_key, secret_key 추출."""
    return connection.get("access_key", ""), connection.get("secret_key", "")


def _make_bithumb_client(access_key: str, secret_key: str):
    """인증된 Bithumb 클라이언트를 반환합니다."""
    from programgarden_finance.bithumb.client import Bithumb
    b = Bithumb()
    if access_key and secret_key:
        b.login(accesskey=access_key, secretkey=secret_key)
    return b


def _error(msg: str) -> Dict[str, Any]:
    return {"error": msg, "success": False}


# ─────────────────────────────────────────── BithumbBrokerNodeExecutor ──


class BithumbBrokerNodeExecutor(_BithumbExecutorBase):
    """BithumbBrokerNode executor.

    credential_id로 access_key/secret_key를 주입하고
    connection dict를 하위 노드에 전파합니다.
    """

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        # deep_validate: fixture 반환
        if context.is_deep_validate:
            from programgarden import deep_fixtures as _df
            config = _evaluate_all_bindings(config, context, node_id)
            fixture = _df.broker_connection_fixture(node_type, config)
            override = context.get_deep_fixture(node_id, node_type)
            return _df.apply_override(fixture, override)

        credential_id = config.get("credential_id")
        if credential_id:
            config = self._inject_credentials(credential_id, config, context, node_id)

        access_key = config.get("access_key", "")
        secret_key = config.get("secret_key", "")

        if not access_key or not secret_key:
            context.log(
                "warning",
                "BithumbBrokerNode: access_key/secret_key가 없습니다. "
                "Public API(시세 조회)는 사용 가능하지만 Private API는 실패합니다.",
                node_id,
            )

        return {
            "connected": True,
            "connection": {
                "provider": "bithumb.com",
                "product": "coin",
                "access_key": access_key,
                "secret_key": secret_key,
            },
        }


# ──────────────────────────────────────── BithumbAccountNodeExecutor ──


class BithumbAccountNodeExecutor(_BithumbExecutorBase):
    """BithumbAccountNode executor — GET /v1/accounts 호출."""

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        if context.is_deep_validate or context.is_dry_run:
            from programgarden import deep_fixtures as _df
            config = _evaluate_all_bindings(config, context, node_id)
            fixture = _df.bithumb_account_fixture()
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "BithumbAccountNode: BithumbBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        access_key, secret_key = _get_bithumb_credentials(connection)
        if not access_key or not secret_key:
            context.log("error", "BithumbAccountNode: access_key/secret_key 없음", node_id)
            return _error("Missing Bithumb credentials")

        config = _evaluate_all_bindings(config, context, node_id)

        try:
            bithumb = _make_bithumb_client(access_key, secret_key)
            resp = bithumb.account().accounts().req()

            if resp.error_msg:
                context.log("error", f"BithumbAccountNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            blocks = resp.blocks or []

            # KRW 잔고 분리
            krw_block = next((b for b in blocks if b.currency == "KRW"), None)
            krw_balance = float(krw_block.balance) if krw_block else 0.0
            krw_locked = float(krw_block.locked) if krw_block else 0.0

            balance = {
                "krw_balance": krw_balance,
                "krw_locked": krw_locked,
                "orderable_amount": krw_balance,
            }

            # KRW 제외 코인 포지션
            positions = []
            held_symbols = []
            for blk in blocks:
                if blk.currency == "KRW":
                    continue
                bal = float(blk.balance)
                if bal <= 0:
                    continue
                market = f"KRW-{blk.currency}"
                positions.append({
                    "market": market,
                    "currency": blk.currency,
                    "balance": bal,
                    "locked": float(blk.locked),
                    "avg_buy_price": float(blk.avg_buy_price),
                })
                held_symbols.append({"market": market})

            context.log(
                "info",
                f"BithumbAccountNode: KRW={krw_balance:,.0f}, 보유코인={len(positions)}종",
                node_id,
            )
            return {
                "balance": balance,
                "positions": positions,
                "held_symbols": held_symbols,
            }

        except Exception as exc:
            context.log("error", f"BithumbAccountNode 실패: {exc}", node_id)
            return _error(str(exc))


# ─────────────────────────────────── BithumbMarketDataNodeExecutor ──


class BithumbMarketDataNodeExecutor(_BithumbExecutorBase):
    """BithumbMarketDataNode executor — GET /v1/ticker 호출."""

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        if context.is_deep_validate or context.is_dry_run:
            from programgarden import deep_fixtures as _df
            config = _evaluate_all_bindings(config, context, node_id)
            markets_raw = config.get("markets", "KRW-BTC")
            fixture = _df.bithumb_market_data_fixture(markets_raw)
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        config = _evaluate_all_bindings(config, context, node_id)
        markets = str(config.get("markets", "KRW-BTC")).strip()
        if not markets:
            markets = "KRW-BTC"

        try:
            from programgarden_finance.bithumb.market.ticker.blocks import TickerInBlock

            bithumb = _make_bithumb_client("", "")  # Public API — 인증 불필요
            resp = bithumb.market().ticker(TickerInBlock(markets=markets)).req()

            if resp.error_msg:
                context.log("error", f"BithumbMarketDataNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            values = []
            for blk in resp.blocks or []:
                values.append({
                    "market": blk.market,
                    "trade_price": blk.trade_price,
                    "change": blk.change,
                    "change_price": blk.change_price,
                    "signed_change_rate": blk.signed_change_rate,
                    "acc_trade_volume_24h": blk.acc_trade_volume_24h,
                    "acc_trade_price_24h": blk.acc_trade_price_24h,
                    "high_price": blk.high_price,
                    "low_price": blk.low_price,
                    "opening_price": blk.opening_price,
                    "prev_closing_price": blk.prev_closing_price,
                    "timestamp": blk.timestamp,
                })

            context.log("info", f"BithumbMarketDataNode: {len(values)}개 마켓 조회", node_id)
            return {"values": values}

        except Exception as exc:
            context.log("error", f"BithumbMarketDataNode 실패: {exc}", node_id)
            return _error(str(exc))


# ─────────────────────────────────── BithumbNewOrderNodeExecutor ──


class BithumbNewOrderNodeExecutor(_BithumbExecutorBase):
    """BithumbNewOrderNode executor — POST /v2/orders 호출."""

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        # dry_run
        if context.is_dry_run:
            order_id = f"DRYRUN-{uuid.uuid4()}"
            context.log("info", f"[dry_run] BithumbNewOrderNode → {order_id}", node_id)
            return {
                "result": {"order_id": order_id, "status": "simulated", "dry_run": True},
                "order_id": order_id,
            }

        if context.is_risk_halted:
            context.log("warning", "BithumbNewOrderNode: risk_halt 상태 — 주문 중단", node_id)
            return _error("Order halted by risk event")

        connection = config.get("connection")
        if not connection:
            context.log("error", "BithumbNewOrderNode: BithumbBrokerNode 연결 없음", node_id)
            return _error("Missing connection")

        access_key, secret_key = _get_bithumb_credentials(connection)
        if not access_key or not secret_key:
            return _error("Missing Bithumb credentials")

        config = _evaluate_all_bindings(config, context, node_id)

        order = config.get("order") or {}
        side = config.get("side", "bid")
        order_type = config.get("order_type", "limit")

        if isinstance(order, dict):
            market = order.get("market", "")
            volume = str(order.get("volume", "")) or None
            price = str(order.get("price", "")) or None
        else:
            context.log("error", "BithumbNewOrderNode: order 필드가 dict여야 합니다", node_id)
            return _error("Invalid order format")

        if not market:
            context.log("error", "BithumbNewOrderNode: market이 없습니다", node_id)
            return _error("Missing market in order")

        context.log(
            "info",
            f"BithumbNewOrderNode: {market} {side} {order_type} vol={volume} price={price}",
            node_id,
        )

        try:
            from programgarden_finance.bithumb.order.order_new.blocks import OrderNewInBlock

            bithumb = _make_bithumb_client(access_key, secret_key)
            resp = bithumb.order().order_new(
                body=OrderNewInBlock(
                    market=market,
                    side=side,
                    order_type=order_type,
                    volume=volume,
                    price=price,
                )
            ).req()

            if resp.error_msg:
                context.log("error", f"BithumbNewOrderNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            blk = resp.block
            if not blk:
                return _error("Empty order response")

            result = {
                "order_id": blk.order_id,
                "market": blk.market,
                "side": blk.side,
                "order_type": blk.order_type,
                "status": "accepted",
                "created_at": blk.created_at,
            }
            context.log("info", f"BithumbNewOrderNode 주문 완료: {blk.order_id}", node_id)
            return {"result": result, "order_id": blk.order_id}

        except Exception as exc:
            context.log("error", f"BithumbNewOrderNode 실패: {exc}", node_id)
            return _error(str(exc))


# ────────────────────────────────── BithumbCancelOrderNodeExecutor ──


class BithumbCancelOrderNodeExecutor(_BithumbExecutorBase):
    """BithumbCancelOrderNode executor — DELETE /v2/order 호출."""

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        if context.is_dry_run:
            original = config.get("original_order_id", "UNKNOWN")
            context.log("info", f"[dry_run] BithumbCancelOrderNode → {original}", node_id)
            return {
                "cancel_result": {"order_id": original, "status": "simulated_cancel"},
                "cancelled_order_id": original,
            }

        connection = config.get("connection")
        if not connection:
            context.log("error", "BithumbCancelOrderNode: BithumbBrokerNode 연결 없음", node_id)
            return _error("Missing connection")

        access_key, secret_key = _get_bithumb_credentials(connection)
        if not access_key or not secret_key:
            return _error("Missing Bithumb credentials")

        config = _evaluate_all_bindings(config, context, node_id)
        original_order_id = str(config.get("original_order_id") or "").strip()

        if not original_order_id:
            context.log("error", "BithumbCancelOrderNode: original_order_id 없음", node_id)
            return _error("Missing original_order_id")

        context.log("info", f"BithumbCancelOrderNode: 주문 취소 {original_order_id}", node_id)

        try:
            from programgarden_finance.bithumb.order.order_cancel.blocks import OrderCancelInBlock

            bithumb = _make_bithumb_client(access_key, secret_key)
            resp = bithumb.order().order_cancel(
                params=OrderCancelInBlock(order_id=original_order_id)
            ).req()

            if resp.error_msg:
                context.log("error", f"BithumbCancelOrderNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            result = {
                "order_id": original_order_id,
                "status": "cancelled",
            }
            context.log("info", f"BithumbCancelOrderNode: 취소 완료 {original_order_id}", node_id)
            return {"cancel_result": result, "cancelled_order_id": original_order_id}

        except Exception as exc:
            context.log("error", f"BithumbCancelOrderNode 실패: {exc}", node_id)
            return _error(str(exc))
