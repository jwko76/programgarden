"""키움증권(Kiwoom) 노드 executor 구현.

KiwoomBrokerNodeExecutor, KiwoomAccountNodeExecutor, KiwoomMarketDataNodeExecutor,
KiwoomHistoricalDataNodeExecutor, KiwoomNewOrderNodeExecutor,
KiwoomCancelOrderNodeExecutor — 각각 키움 OpenAPI(REST)를 직접 호출합니다.

KIS executor와의 주요 차이:
- 실전/모의 분기가 tr_id(TTTC↔VTTC)가 아니라 접속 도메인 자체
  (api.kiwoom.com ↔ mockapi.kiwoom.com) — paper_trading이 서버를 전환
- 취소는 api-id kt10003 전용이며 종목코드(stk_cd)가 필수 → 노드에 symbol 필드 존재
- 응답 봉투가 return_code/return_msg 단일 구조 (KIS output/output1/output2 없음)

주의: deep_validate에서는 절대 Kiwoom 클라이언트를 생성하지 않습니다 —
토큰 발급 자체가 라이브 API 호출입니다.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("programgarden.kiwoom")

_SYMBOL_RE = re.compile(r"^[0-9A-Z]{6}$")


# executor.py와의 순환 참조를 피하기 위해 standalone 베이스 클래스를 정의합니다.

class _KiwoomExecutorBase:
    """Kiwoom executor 공통 베이스. executor.py 순환 참조 없이 동작합니다."""

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
                context.log("debug", f"Kiwoom credentials injected: {', '.join(injected)}", node_id)
        else:
            context.log("warning", f"Credential '{credential_id}' not found", node_id)
        return config


def _evaluate_all_bindings(config, context, node_id):
    """executor.py의 evaluate_all_bindings를 lazy import해서 호출합니다."""
    from programgarden.executor import evaluate_all_bindings
    return evaluate_all_bindings(config, context, node_id)


# ──────────────────────────────────────────────────────────────────── helpers ──


def _get_kiwoom_connection(connection: Dict[str, Any]) -> Tuple[str, str, str, str, bool]:
    """connection dict에서 (appkey, appsecret, account_no, account_product_code, paper_trading) 추출."""
    return (
        connection.get("appkey", ""),
        connection.get("appsecret", ""),
        connection.get("account_no", ""),
        connection.get("account_product_code", "01") or "01",
        bool(connection.get("paper_trading", False)),
    )


def _make_kiwoom_client(
    appkey: str,
    appsecret: str,
    account_no: str = "",
    account_product_code: str = "01",
    paper_trading: bool = False,
):
    """인증된 Kiwoom 클라이언트를 반환합니다 (토큰은 첫 TR 요청 시 지연 발급)."""
    from programgarden_finance.kiwoom.client import Kiwoom
    kiwoom = Kiwoom(paper_trading=paper_trading)
    kiwoom.login(
        appkey=appkey,
        appsecretkey=appsecret,
        account_no=account_no,
        account_product_code=account_product_code,
    )
    return kiwoom


def _error(msg: str) -> Dict[str, Any]:
    return {"error": msg, "success": False}


def _to_float(value: Optional[str], default: float = 0.0) -> float:
    # 키움 시세 필드는 "+500"/"-500" 형태의 부호 접두 문자열일 수 있음 — float()가 그대로 처리
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ─────────────────────────────────────────────── KiwoomBrokerNodeExecutor ──


class KiwoomBrokerNodeExecutor(_KiwoomExecutorBase):
    """KiwoomBrokerNode executor.

    credential_id로 appkey/appsecret/account_no를 주입하고
    paper_trading 플래그를 포함한 connection dict를 하위 노드에 전파합니다.
    """

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        # deep_validate: fixture 반환 (Kiwoom 클라이언트 생성 금지 — 토큰 발급은 라이브 호출)
        if context.is_deep_validate:
            from programgarden import deep_fixtures as _df
            config = _evaluate_all_bindings(config, context, node_id)
            fixture = _df.broker_connection_fixture(node_type, config)
            override = context.get_deep_fixture(node_id, node_type)
            return _df.apply_override(fixture, override)

        credential_id = config.get("credential_id")
        if credential_id:
            config = self._inject_credentials(credential_id, config, context, node_id)

        appkey = config.get("appkey", "")
        appsecret = config.get("appsecret", "")
        account_no = config.get("account_no", "")
        account_product_code = config.get("account_product_code", "01") or "01"
        paper_trading = bool(config.get("paper_trading", False))

        if not appkey or not appsecret:
            context.log(
                "warning",
                "KiwoomBrokerNode: appkey/appsecret이 없습니다. 모든 키움 API 호출이 실패합니다.",
                node_id,
            )

        mode = "모의투자(mockapi)" if paper_trading else "실전투자(api)"
        context.log("info", f"KiwoomBrokerNode: {mode} 도메인으로 연결 구성", node_id)

        return {
            "connected": True,
            "connection": {
                "provider": "kiwoom.com",
                "product": "korea_stock",
                "appkey": appkey,
                "appsecret": appsecret,
                "account_no": account_no,
                "account_product_code": account_product_code,
                "paper_trading": paper_trading,
            },
        }


# ──────────────────────────────────────────── KiwoomAccountNodeExecutor ──


class KiwoomAccountNodeExecutor(_KiwoomExecutorBase):
    """KiwoomAccountNode executor — 계좌평가잔고내역요청 (kt00018)."""

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
            fixture = _df.kiwoom_account_fixture()
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "KiwoomAccountNode: KiwoomBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kiwoom_connection(connection)
        if not appkey or not appsecret:
            context.log("error", "KiwoomAccountNode: appkey/appsecret 없음", node_id)
            return _error("Missing Kiwoom credentials")
        if not account_no:
            context.log("error", "KiwoomAccountNode: account_no(계좌번호) 없음", node_id)
            return _error("Missing Kiwoom account_no")

        config = _evaluate_all_bindings(config, context, node_id)

        try:
            kiwoom = _make_kiwoom_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            resp = kiwoom.accno().inquire_balance().req()

            if resp.error_msg:
                context.log("error", f"KiwoomAccountNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            summary = resp.block
            # kt00018 요약에는 예수금(entr)이 없어 추정예탁자산으로 대체합니다
            # (라이브 확인: 2026-07-18). 예수금 상세는 kt00001 TR 필요 (미구현).
            deposit = _to_float(getattr(summary, "prsm_dpst_aset_amt", None))
            balance = {
                "deposit": deposit,
                "orderable_amount": deposit,
                "total_evaluation": _to_float(getattr(summary, "tot_evlt_amt", None)),
                "total_purchase": _to_float(getattr(summary, "tot_pur_amt", None)),
                "total_profit_loss": _to_float(getattr(summary, "tot_evlt_pl", None)),
            }

            positions = []
            held_symbols = []
            for blk in resp.blocks or []:
                quantity = _to_float(blk.rmnd_qty)
                if quantity <= 0:
                    continue
                positions.append({
                    "symbol": blk.stk_cd,
                    "symbol_name": blk.stk_nm,
                    "quantity": quantity,
                    "orderable_quantity": _to_float(blk.trde_able_qty, quantity),
                    "avg_buy_price": _to_float(blk.pur_pric),
                    "current_price": abs(_to_float(blk.cur_prc)),
                    "evaluation_amount": _to_float(blk.evlt_amt),
                    "profit_loss": _to_float(blk.evltv_prft),
                    "profit_loss_rate": _to_float(blk.prft_rt),
                })
                held_symbols.append({"symbol": blk.stk_cd})

            context.log(
                "info",
                f"KiwoomAccountNode: 예수금={deposit:,.0f}, 보유종목={len(positions)}종",
                node_id,
            )
            return {
                "balance": balance,
                "positions": positions,
                "held_symbols": held_symbols,
            }

        except Exception as exc:
            context.log("error", f"KiwoomAccountNode 실패: {exc}", node_id)
            return _error(str(exc))


# ─────────────────────────────────────── KiwoomMarketDataNodeExecutor ──


class KiwoomMarketDataNodeExecutor(_KiwoomExecutorBase):
    """KiwoomMarketDataNode executor — 종목기본정보요청 (ka10001).

    보안:
    - symbol 파라미터: ^[0-9A-Z]{6}$ 패턴 검증 (injection 방지)
    """

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
            fixture = _df.kiwoom_market_data_fixture(config.get("symbols", "005930"))
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "KiwoomMarketDataNode: KiwoomBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kiwoom_connection(connection)
        if not appkey or not appsecret:
            context.log("error", "KiwoomMarketDataNode: appkey/appsecret 없음", node_id)
            return _error("Missing Kiwoom credentials")

        config = _evaluate_all_bindings(config, context, node_id)
        symbols_raw = str(config.get("symbols", "")).strip()
        symbols = [s.strip().upper() for s in symbols_raw.split(",") if s.strip()]
        if not symbols:
            context.log("error", "KiwoomMarketDataNode: symbols가 비어 있습니다.", node_id)
            return _error("Missing symbols")

        # 입력 검증 (시큐어 코딩 §1.3)
        for symbol in symbols:
            if not _SYMBOL_RE.match(symbol):
                context.log("error", f"KiwoomMarketDataNode: 잘못된 종목코드 '{symbol}'", node_id)
                return _error(f"Invalid symbol format: {symbol}")

        try:
            from programgarden_finance.kiwoom.quotations.inquire_price.blocks import InquirePriceInBlock

            kiwoom = _make_kiwoom_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            quotations = kiwoom.quotations()

            values = []
            for symbol in symbols:
                resp = quotations.inquire_price(InquirePriceInBlock(stk_cd=symbol)).req()
                if resp.error_msg:
                    context.log("error", f"KiwoomMarketDataNode ({symbol}): {resp.error_msg}", node_id)
                    return _error(resp.error_msg)
                blk = resp.block
                values.append({
                    "symbol": symbol,
                    "current_price": abs(_to_float(blk.cur_prc)),
                    "change": _to_float(blk.pred_pre),
                    "change_rate": _to_float(blk.flu_rt),
                    "open_price": abs(_to_float(blk.open_pric)),
                    "high_price": abs(_to_float(blk.high_pric)),
                    "low_price": abs(_to_float(blk.low_pric)),
                    "volume": _to_float(blk.trde_qty),
                    # 키움 종목기본정보에는 누적 거래대금 필드가 확인되지 않아 0으로
                    # 반환합니다. TODO(실계좌 검증): 필드 확인 시 교체.
                    "trade_amount": 0.0,
                    "per": _to_float(blk.per),
                    "pbr": _to_float(blk.pbr),
                })

            context.log("info", f"KiwoomMarketDataNode: {len(values)}개 종목 조회", node_id)
            return {"values": values}

        except Exception as exc:
            context.log("error", f"KiwoomMarketDataNode 실패: {exc}", node_id)
            return _error(str(exc))


# ──────────────────────────────── KiwoomHistoricalDataNodeExecutor ──


class KiwoomHistoricalDataNodeExecutor(_KiwoomExecutorBase):
    """KiwoomHistoricalDataNode executor — 주식일봉차트조회 (ka10081).

    보안:
    - symbol 파라미터: ^[0-9A-Z]{6}$ 패턴 검증
    - count: 1~600 범위 강제
    """

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
            fixture = _df.kiwoom_historical_fixture(config.get("symbol", "005930"))
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "KiwoomHistoricalDataNode: KiwoomBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kiwoom_connection(connection)
        if not appkey or not appsecret:
            context.log("error", "KiwoomHistoricalDataNode: appkey/appsecret 없음", node_id)
            return _error("Missing Kiwoom credentials")

        config = _evaluate_all_bindings(config, context, node_id)
        symbol = str(config.get("symbol", "005930")).strip().upper()
        count = int(config.get("count", 30))

        # 입력 검증 (시큐어 코딩 §1.3)
        if not _SYMBOL_RE.match(symbol):
            context.log("error", f"KiwoomHistoricalDataNode: 잘못된 종목코드 '{symbol}'", node_id)
            return _error(f"Invalid symbol format: {symbol}")
        count = max(1, min(600, count))

        try:
            from programgarden_finance.kiwoom.quotations.inquire_daily_itemchartprice.blocks import (
                InquireDailyItemChartPriceInBlock,
            )

            kiwoom = _make_kiwoom_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            resp = kiwoom.quotations().inquire_daily_itemchartprice(
                InquireDailyItemChartPriceInBlock(
                    stk_cd=symbol,
                    base_dt=datetime.now().strftime("%Y%m%d"),
                )
            ).req()

            if resp.error_msg:
                context.log("error", f"KiwoomHistoricalDataNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            # 원본 캔들 (최신→과거 순, API 반환 그대로) — count 개로 절단
            values = []
            for blk in (resp.blocks or [])[:count]:
                values.append({
                    "symbol": symbol,
                    "date": blk.dt,
                    "open": abs(_to_float(blk.open_pric)),
                    "high": abs(_to_float(blk.high_pric)),
                    "low": abs(_to_float(blk.low_pric)),
                    "close": abs(_to_float(blk.cur_prc)),
                    "volume": _to_float(blk.trde_qty),
                })

            # ConditionNode RSI/Bollinger용 time_series (oldest-first 역순 정렬)
            series_oldest_first = list(reversed(values))
            time_series = [
                {
                    "symbol": symbol,
                    "exchange": "KRX",
                    "time_series": series_oldest_first,
                }
            ]

            context.log("info", f"KiwoomHistoricalDataNode: {symbol} {len(values)}개 캔들 조회", node_id)
            return {"values": values, "time_series": time_series}

        except Exception as exc:
            context.log("error", f"KiwoomHistoricalDataNode 실패: {exc}", node_id)
            return _error(str(exc))


# ─────────────────────────────────────── KiwoomNewOrderNodeExecutor ──


class KiwoomNewOrderNodeExecutor(_KiwoomExecutorBase):
    """KiwoomNewOrderNode executor — 주식 현금매수(kt10000)/현금매도(kt10001).

    실전/모의는 connection의 paper_trading 플래그에 따라 접속 도메인이
    전환되며 api-id는 공용입니다.
    """

    # 매매구분 코드. TODO(실계좌 검증): 공식 문서로 코드값 확정 필요.
    _TRDE_TP_LIMIT = "0"   # 보통(지정가)로 추정
    _TRDE_TP_MARKET = "3"  # 시장가로 추정

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
            order_no = f"DRYRUN-{uuid.uuid4()}"
            context.log("info", f"[dry_run] KiwoomNewOrderNode → {order_no}", node_id)
            return {
                "result": {"order_no": order_no, "status": "simulated", "dry_run": True},
                "order_no": order_no,
            }

        if context.is_risk_halted:
            context.log("warning", "KiwoomNewOrderNode: risk_halt 상태 — 주문 중단", node_id)
            return _error("Order halted by risk event")

        connection = config.get("connection")
        if not connection:
            context.log("error", "KiwoomNewOrderNode: KiwoomBrokerNode 연결 없음", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kiwoom_connection(connection)
        if not appkey or not appsecret:
            return _error("Missing Kiwoom credentials")
        if not account_no:
            return _error("Missing Kiwoom account_no")

        config = _evaluate_all_bindings(config, context, node_id)

        order = config.get("order") or {}
        side = config.get("side", "buy")
        order_type = config.get("order_type", "limit")

        if not isinstance(order, dict):
            context.log("error", "KiwoomNewOrderNode: order 필드가 dict여야 합니다", node_id)
            return _error("Invalid order format")

        symbol = str(order.get("symbol", "")).strip().upper()
        quantity = str(order.get("quantity", "")).strip()
        price = str(order.get("price", "")).strip()

        if not symbol or not _SYMBOL_RE.match(symbol):
            context.log("error", f"KiwoomNewOrderNode: 잘못된 종목코드 '{symbol}'", node_id)
            return _error(f"Invalid symbol: {symbol}")
        if not quantity or not quantity.isdigit() or int(quantity) <= 0:
            context.log("error", f"KiwoomNewOrderNode: 잘못된 수량 '{quantity}'", node_id)
            return _error(f"Invalid quantity: {quantity}")

        # 매매구분: 지정가(가격 필수) / 시장가(가격 0)
        if order_type == "market":
            trde_tp, ord_uv = self._TRDE_TP_MARKET, "0"
        else:
            if not price or _to_float(price) <= 0:
                context.log("error", "KiwoomNewOrderNode: 지정가 주문에 price가 필요합니다", node_id)
                return _error("Missing price for limit order")
            trde_tp, ord_uv = self._TRDE_TP_LIMIT, price

        mode = "모의" if paper_trading else "실전"
        context.log(
            "info",
            f"KiwoomNewOrderNode({mode}): {symbol} {side} {order_type} qty={quantity} price={ord_uv}",
            node_id,
        )

        try:
            from programgarden_finance.kiwoom.order.order_cash.blocks import OrderCashBodyBlock

            kiwoom = _make_kiwoom_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            body = OrderCashBodyBlock(
                acnt_no="",  # 클라이언트 등록 계좌 자동 사용
                stk_cd=symbol,
                ord_qty=quantity,
                ord_uv=ord_uv,
                trde_tp=trde_tp,
            )
            order_api = kiwoom.order()
            tr = order_api.order_cash_buy(body) if side == "buy" else order_api.order_cash_sell(body)
            resp = tr.req()

            if resp.error_msg:
                context.log("error", f"KiwoomNewOrderNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            blk = resp.block
            if not blk or not blk.ord_no:
                return _error("Empty order response")

            result = {
                "order_no": blk.ord_no,
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "quantity": _to_float(quantity),
                "price": _to_float(ord_uv),
                "order_time": datetime.now().strftime("%H%M%S"),
                "paper_trading": paper_trading,
                "status": "accepted",
            }
            context.log("info", f"KiwoomNewOrderNode 주문 접수: {blk.ord_no}", node_id)
            return {"result": result, "order_no": blk.ord_no}

        except Exception as exc:
            context.log("error", f"KiwoomNewOrderNode 실패: {exc}", node_id)
            return _error(str(exc))


# ────────────────────────────────── KiwoomCancelOrderNodeExecutor ──


class KiwoomCancelOrderNodeExecutor(_KiwoomExecutorBase):
    """KiwoomCancelOrderNode executor — 주식 취소주문 (kt10003).

    키움 취소 TR은 종목코드(stk_cd)가 필수라 노드의 symbol 필드를 사용합니다.
    """

    async def execute(
        self,
        node_id: str,
        node_type: str,
        config: Dict[str, Any],
        context,
        **kwargs,
    ) -> Dict[str, Any]:
        if context.is_dry_run:
            original = config.get("original_order_no", "UNKNOWN")
            context.log("info", f"[dry_run] KiwoomCancelOrderNode → {original}", node_id)
            return {
                "cancel_result": {"order_no": original, "status": "simulated_cancel"},
                "cancelled_order_no": original,
            }

        connection = config.get("connection")
        if not connection:
            context.log("error", "KiwoomCancelOrderNode: KiwoomBrokerNode 연결 없음", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kiwoom_connection(connection)
        if not appkey or not appsecret:
            return _error("Missing Kiwoom credentials")
        if not account_no:
            return _error("Missing Kiwoom account_no")

        config = _evaluate_all_bindings(config, context, node_id)
        original_order_no = str(config.get("original_order_no") or "").strip()
        symbol = str(config.get("symbol") or "").strip().upper()
        quantity = str(config.get("quantity") or "").strip()

        if not original_order_no:
            context.log("error", "KiwoomCancelOrderNode: original_order_no 없음", node_id)
            return _error("Missing original_order_no")
        if not symbol or not _SYMBOL_RE.match(symbol):
            context.log("error", f"KiwoomCancelOrderNode: 잘못된 종목코드 '{symbol}' — 키움 취소는 symbol 필수", node_id)
            return _error(f"Invalid symbol: {symbol}")

        # 수량 지정 시 일부 취소, 미지정 시 잔량 전부 취소(0)로 가정
        # TODO(실계좌 검증): 키움 kt10003의 전량 취소 규칙 확인
        ord_qty = quantity if (quantity and quantity.isdigit() and int(quantity) > 0) else "0"

        context.log("info", f"KiwoomCancelOrderNode: 주문 취소 {original_order_no} (수량={ord_qty if ord_qty != '0' else '전량'})", node_id)

        try:
            from programgarden_finance.kiwoom.order.order_rvsecncl.blocks import OrderRvsecnclBodyBlock

            kiwoom = _make_kiwoom_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            resp = kiwoom.order().order_cancel(
                OrderRvsecnclBodyBlock(
                    acnt_no="",
                    orig_ord_no=original_order_no,
                    stk_cd=symbol,
                    ord_qty=ord_qty,
                    ord_uv="0",
                )
            ).req()

            if resp.error_msg:
                context.log("error", f"KiwoomCancelOrderNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            result = {
                "order_no": original_order_no,
                "cancel_receipt_no": getattr(resp.block, "ord_no", None),
                "status": "cancelled",
                "paper_trading": paper_trading,
            }
            context.log("info", f"KiwoomCancelOrderNode: 취소 접수 완료 {original_order_no}", node_id)
            return {"cancel_result": result, "cancelled_order_no": original_order_no}

        except Exception as exc:
            context.log("error", f"KiwoomCancelOrderNode 실패: {exc}", node_id)
            return _error(str(exc))
