"""한국투자증권(KIS) 노드 executor 구현.

KisBrokerNodeExecutor, KisAccountNodeExecutor, KisMarketDataNodeExecutor,
KisHistoricalDataNodeExecutor, KisNewOrderNodeExecutor,
KisCancelOrderNodeExecutor — 각각 KIS Developers OpenAPI를 직접 호출합니다.

빗썸 executor와의 주요 차이:
- OAuth 접근토큰 방식 (24h 유효, 파일 캐시) — 클라이언트 생성 시 토큰 지연 발급
- 인증 정보: appkey + appsecret + account_no + account_product_code
- credential 타입: ``broker_kis``
- paper_trading 플래그가 connection에 전파되어 TR ID(TTTC↔VTTC)가 자동 분기

주의: deep_validate에서는 절대 Kis 클라이언트를 생성하지 않습니다 —
토큰 발급 자체가 라이브 API 호출이며 재발급이 분당 1회로 제한됩니다.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("programgarden.kis")

_SYMBOL_RE = re.compile(r"^[0-9A-Z]{6}$")


# executor.py와의 순환 참조를 피하기 위해 standalone 베이스 클래스를 정의합니다.

class _KisExecutorBase:
    """KIS executor 공통 베이스. executor.py 순환 참조 없이 동작합니다."""

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
                context.log("debug", f"KIS credentials injected: {', '.join(injected)}", node_id)
        else:
            context.log("warning", f"Credential '{credential_id}' not found", node_id)
        return config


def _evaluate_all_bindings(config, context, node_id):
    """executor.py의 evaluate_all_bindings를 lazy import해서 호출합니다."""
    from programgarden.executor import evaluate_all_bindings
    return evaluate_all_bindings(config, context, node_id)


# ──────────────────────────────────────────────────────────────────── helpers ──


def _get_kis_connection(connection: Dict[str, Any]) -> Tuple[str, str, str, str, bool]:
    """connection dict에서 (appkey, appsecret, account_no, account_product_code, paper_trading) 추출."""
    return (
        connection.get("appkey", ""),
        connection.get("appsecret", ""),
        connection.get("account_no", ""),
        connection.get("account_product_code", "01") or "01",
        bool(connection.get("paper_trading", False)),
    )


def _make_kis_client(
    appkey: str,
    appsecret: str,
    account_no: str = "",
    account_product_code: str = "01",
    paper_trading: bool = False,
):
    """인증된 Kis 클라이언트를 반환합니다 (토큰은 첫 TR 요청 시 지연 발급)."""
    from programgarden_finance.kis.client import Kis
    kis = Kis(paper_trading=paper_trading)
    kis.login(
        appkey=appkey,
        appsecretkey=appsecret,
        account_no=account_no,
        account_product_code=account_product_code,
    )
    return kis


def _error(msg: str) -> Dict[str, Any]:
    return {"error": msg, "success": False}


def _to_float(value: Optional[str], default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ─────────────────────────────────────────────── KisBrokerNodeExecutor ──


class KisBrokerNodeExecutor(_KisExecutorBase):
    """KisBrokerNode executor.

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
        # deep_validate: fixture 반환 (Kis 클라이언트 생성 금지 — 토큰 발급은 라이브 호출)
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
                "KisBrokerNode: appkey/appsecret이 없습니다. 모든 KIS API 호출이 실패합니다.",
                node_id,
            )

        mode = "모의투자" if paper_trading else "실전투자"
        context.log("info", f"KisBrokerNode: {mode} 모드로 연결 구성", node_id)

        return {
            "connected": True,
            "connection": {
                "provider": "koreainvestment.com",
                "product": "korea_stock",
                "appkey": appkey,
                "appsecret": appsecret,
                "account_no": account_no,
                "account_product_code": account_product_code,
                "paper_trading": paper_trading,
            },
        }


# ──────────────────────────────────────────── KisAccountNodeExecutor ──


class KisAccountNodeExecutor(_KisExecutorBase):
    """KisAccountNode executor — 주식잔고조회 (TTTC8434R/VTTC8434R)."""

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
            fixture = _df.kis_account_fixture()
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "KisAccountNode: KisBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kis_connection(connection)
        if not appkey or not appsecret:
            context.log("error", "KisAccountNode: appkey/appsecret 없음", node_id)
            return _error("Missing KIS credentials")
        if not account_no:
            context.log("error", "KisAccountNode: account_no(계좌번호) 없음", node_id)
            return _error("Missing KIS account_no")

        config = _evaluate_all_bindings(config, context, node_id)

        try:
            kis = _make_kis_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            resp = kis.accno().inquire_balance().req()

            if resp.error_msg:
                context.log("error", f"KisAccountNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            summary = resp.block2
            deposit = _to_float(getattr(summary, "dnca_tot_amt", None))
            orderable = _to_float(getattr(summary, "prvs_rcdl_excc_amt", None), deposit)
            balance = {
                "deposit": deposit,
                "orderable_amount": orderable,
                "total_evaluation": _to_float(getattr(summary, "tot_evlu_amt", None)),
                "total_purchase": _to_float(getattr(summary, "pchs_amt_smtl_amt", None)),
                "total_profit_loss": _to_float(getattr(summary, "evlu_pfls_smtl_amt", None)),
            }

            positions = []
            held_symbols = []
            for blk in resp.blocks or []:
                quantity = _to_float(blk.hldg_qty)
                if quantity <= 0:
                    continue
                positions.append({
                    "symbol": blk.pdno,
                    "symbol_name": blk.prdt_name,
                    "quantity": quantity,
                    "orderable_quantity": _to_float(blk.ord_psbl_qty),
                    "avg_buy_price": _to_float(blk.pchs_avg_pric),
                    "current_price": _to_float(blk.prpr),
                    "evaluation_amount": _to_float(blk.evlu_amt),
                    "profit_loss": _to_float(blk.evlu_pfls_amt),
                    "profit_loss_rate": _to_float(blk.evlu_pfls_rt),
                })
                held_symbols.append({"symbol": blk.pdno})

            context.log(
                "info",
                f"KisAccountNode: 예수금={deposit:,.0f}, 보유종목={len(positions)}종",
                node_id,
            )
            return {
                "balance": balance,
                "positions": positions,
                "held_symbols": held_symbols,
            }

        except Exception as exc:
            context.log("error", f"KisAccountNode 실패: {exc}", node_id)
            return _error(str(exc))


# ─────────────────────────────────────── KisMarketDataNodeExecutor ──


class KisMarketDataNodeExecutor(_KisExecutorBase):
    """KisMarketDataNode executor — 주식현재가 시세 (FHKST01010100).

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
            fixture = _df.kis_market_data_fixture(config.get("symbols", "005930"))
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "KisMarketDataNode: KisBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kis_connection(connection)
        if not appkey or not appsecret:
            context.log("error", "KisMarketDataNode: appkey/appsecret 없음", node_id)
            return _error("Missing KIS credentials")

        config = _evaluate_all_bindings(config, context, node_id)
        symbols_raw = str(config.get("symbols", "")).strip()
        symbols = [s.strip().upper() for s in symbols_raw.split(",") if s.strip()]
        if not symbols:
            context.log("error", "KisMarketDataNode: symbols가 비어 있습니다.", node_id)
            return _error("Missing symbols")

        # 입력 검증 (시큐어 코딩 §1.3)
        for symbol in symbols:
            if not _SYMBOL_RE.match(symbol):
                context.log("error", f"KisMarketDataNode: 잘못된 종목코드 '{symbol}'", node_id)
                return _error(f"Invalid symbol format: {symbol}")

        try:
            from programgarden_finance.kis.quotations.inquire_price.blocks import InquirePriceInBlock

            kis = _make_kis_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            quotations = kis.quotations()

            values = []
            for symbol in symbols:
                resp = quotations.inquire_price(InquirePriceInBlock(fid_input_iscd=symbol)).req()
                if resp.error_msg:
                    context.log("error", f"KisMarketDataNode ({symbol}): {resp.error_msg}", node_id)
                    return _error(resp.error_msg)
                blk = resp.block
                values.append({
                    "symbol": symbol,
                    "current_price": _to_float(blk.stck_prpr),
                    "change": _to_float(blk.prdy_vrss),
                    "change_rate": _to_float(blk.prdy_ctrt),
                    "open_price": _to_float(blk.stck_oprc),
                    "high_price": _to_float(blk.stck_hgpr),
                    "low_price": _to_float(blk.stck_lwpr),
                    "volume": _to_float(blk.acml_vol),
                    "trade_amount": _to_float(blk.acml_tr_pbmn),
                    "per": _to_float(blk.per),
                    "pbr": _to_float(blk.pbr),
                })

            context.log("info", f"KisMarketDataNode: {len(values)}개 종목 조회", node_id)
            return {"values": values}

        except Exception as exc:
            context.log("error", f"KisMarketDataNode 실패: {exc}", node_id)
            return _error(str(exc))


# ──────────────────────────────── KisHistoricalDataNodeExecutor ──


class KisHistoricalDataNodeExecutor(_KisExecutorBase):
    """KisHistoricalDataNode executor — 기간별 시세 일봉 (FHKST03010100).

    보안:
    - symbol 파라미터: ^[0-9A-Z]{6}$ 패턴 검증
    - count: 1~100 범위 강제 (KIS 1회 최대 100건)
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
            fixture = _df.kis_historical_fixture(config.get("symbol", "005930"))
            if context.is_deep_validate:
                return _df.apply_override(fixture, context.get_deep_fixture(node_id, node_type))
            return fixture

        connection = config.get("connection")
        if not connection:
            context.log("error", "KisHistoricalDataNode: KisBrokerNode 연결이 없습니다.", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kis_connection(connection)
        if not appkey or not appsecret:
            context.log("error", "KisHistoricalDataNode: appkey/appsecret 없음", node_id)
            return _error("Missing KIS credentials")

        config = _evaluate_all_bindings(config, context, node_id)
        symbol = str(config.get("symbol", "005930")).strip().upper()
        count = int(config.get("count", 30))

        # 입력 검증 (시큐어 코딩 §1.3)
        if not _SYMBOL_RE.match(symbol):
            context.log("error", f"KisHistoricalDataNode: 잘못된 종목코드 '{symbol}'", node_id)
            return _error(f"Invalid symbol format: {symbol}")
        count = max(1, min(100, count))

        try:
            from programgarden_finance.kis.quotations.inquire_daily_itemchartprice.blocks import (
                InquireDailyItemChartPriceInBlock,
            )

            # 휴장일 보정을 위해 여유 있게 조회 기간 산정 (count 영업일 ≈ count*2 달력일)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=count * 2 + 10)

            kis = _make_kis_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            resp = kis.quotations().inquire_daily_itemchartprice(
                InquireDailyItemChartPriceInBlock(
                    fid_input_iscd=symbol,
                    fid_input_date_1=start_date.strftime("%Y%m%d"),
                    fid_input_date_2=end_date.strftime("%Y%m%d"),
                )
            ).req()

            if resp.error_msg:
                context.log("error", f"KisHistoricalDataNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            # 원본 캔들 (최신→과거 순, API 반환 그대로) — count 개로 절단
            values = []
            for blk in (resp.blocks or [])[:count]:
                values.append({
                    "symbol": symbol,
                    "date": blk.stck_bsop_date,
                    "open": _to_float(blk.stck_oprc),
                    "high": _to_float(blk.stck_hgpr),
                    "low": _to_float(blk.stck_lwpr),
                    "close": _to_float(blk.stck_clpr),
                    "volume": _to_float(blk.acml_vol),
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

            context.log("info", f"KisHistoricalDataNode: {symbol} {len(values)}개 캔들 조회", node_id)
            return {"values": values, "time_series": time_series}

        except Exception as exc:
            context.log("error", f"KisHistoricalDataNode 실패: {exc}", node_id)
            return _error(str(exc))


# ─────────────────────────────────────── KisNewOrderNodeExecutor ──


class KisNewOrderNodeExecutor(_KisExecutorBase):
    """KisNewOrderNode executor — 주식주문(현금).

    실전 TTTC0802U(매수)/TTTC0801U(매도), 모의 VTTC0802U/VTTC0801U —
    connection의 paper_trading 플래그로 SDK가 자동 분기합니다.
    """

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
            context.log("info", f"[dry_run] KisNewOrderNode → {order_no}", node_id)
            return {
                "result": {"order_no": order_no, "status": "simulated", "dry_run": True},
                "order_no": order_no,
            }

        if context.is_risk_halted:
            context.log("warning", "KisNewOrderNode: risk_halt 상태 — 주문 중단", node_id)
            return _error("Order halted by risk event")

        connection = config.get("connection")
        if not connection:
            context.log("error", "KisNewOrderNode: KisBrokerNode 연결 없음", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kis_connection(connection)
        if not appkey or not appsecret:
            return _error("Missing KIS credentials")
        if not account_no:
            return _error("Missing KIS account_no")

        config = _evaluate_all_bindings(config, context, node_id)

        order = config.get("order") or {}
        side = config.get("side", "buy")
        order_type = config.get("order_type", "limit")

        if not isinstance(order, dict):
            context.log("error", "KisNewOrderNode: order 필드가 dict여야 합니다", node_id)
            return _error("Invalid order format")

        symbol = str(order.get("symbol", "")).strip().upper()
        quantity = str(order.get("quantity", "")).strip()
        price = str(order.get("price", "")).strip()

        if not symbol or not _SYMBOL_RE.match(symbol):
            context.log("error", f"KisNewOrderNode: 잘못된 종목코드 '{symbol}'", node_id)
            return _error(f"Invalid symbol: {symbol}")
        if not quantity or not quantity.isdigit() or int(quantity) <= 0:
            context.log("error", f"KisNewOrderNode: 잘못된 수량 '{quantity}'", node_id)
            return _error(f"Invalid quantity: {quantity}")

        # 주문구분: 00 지정가(가격 필수), 01 시장가(가격 0)
        if order_type == "market":
            ord_dvsn, ord_unpr = "01", "0"
        else:
            if not price or _to_float(price) <= 0:
                context.log("error", "KisNewOrderNode: 지정가 주문에 price가 필요합니다", node_id)
                return _error("Missing price for limit order")
            ord_dvsn, ord_unpr = "00", price

        mode = "모의" if paper_trading else "실전"
        context.log(
            "info",
            f"KisNewOrderNode({mode}): {symbol} {side} {order_type} qty={quantity} price={ord_unpr}",
            node_id,
        )

        try:
            from programgarden_finance.kis.order.order_cash.blocks import OrderCashBodyBlock

            kis = _make_kis_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            body = OrderCashBodyBlock(
                cano="",  # 클라이언트 등록 계좌 자동 사용
                pdno=symbol,
                ord_dvsn=ord_dvsn,
                ord_qty=quantity,
                ord_unpr=ord_unpr,
            )
            order_api = kis.order()
            tr = order_api.order_cash_buy(body) if side == "buy" else order_api.order_cash_sell(body)
            resp = tr.req()

            if resp.error_msg:
                context.log("error", f"KisNewOrderNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            blk = resp.block
            if not blk or not blk.odno:
                return _error("Empty order response")

            result = {
                "order_no": blk.odno,
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "quantity": _to_float(quantity),
                "price": _to_float(ord_unpr),
                "order_time": blk.ord_tmd,
                "paper_trading": paper_trading,
                "krx_fwdg_ord_orgno": blk.krx_fwdg_ord_orgno,
                "status": "accepted",
            }
            context.log("info", f"KisNewOrderNode 주문 접수: {blk.odno}", node_id)
            return {"result": result, "order_no": blk.odno}

        except Exception as exc:
            context.log("error", f"KisNewOrderNode 실패: {exc}", node_id)
            return _error(str(exc))


# ────────────────────────────────── KisCancelOrderNodeExecutor ──


class KisCancelOrderNodeExecutor(_KisExecutorBase):
    """KisCancelOrderNode executor — 주식주문(정정취소)로 취소 실행."""

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
            context.log("info", f"[dry_run] KisCancelOrderNode → {original}", node_id)
            return {
                "cancel_result": {"order_no": original, "status": "simulated_cancel"},
                "cancelled_order_no": original,
            }

        connection = config.get("connection")
        if not connection:
            context.log("error", "KisCancelOrderNode: KisBrokerNode 연결 없음", node_id)
            return _error("Missing connection")

        appkey, appsecret, account_no, account_product_code, paper_trading = _get_kis_connection(connection)
        if not appkey or not appsecret:
            return _error("Missing KIS credentials")
        if not account_no:
            return _error("Missing KIS account_no")

        config = _evaluate_all_bindings(config, context, node_id)
        original_order_no = str(config.get("original_order_no") or "").strip()
        quantity = str(config.get("quantity") or "").strip()

        if not original_order_no:
            context.log("error", "KisCancelOrderNode: original_order_no 없음", node_id)
            return _error("Missing original_order_no")

        # 수량 지정 시 일부 취소, 미지정 시 잔량 전부 취소
        if quantity and quantity.isdigit() and int(quantity) > 0:
            ord_qty, qty_all = quantity, "N"
        else:
            ord_qty, qty_all = "0", "Y"

        context.log("info", f"KisCancelOrderNode: 주문 취소 {original_order_no} (수량={ord_qty or '전량'})", node_id)

        try:
            from programgarden_finance.kis.order.order_rvsecncl.blocks import OrderRvsecnclBodyBlock

            kis = _make_kis_client(appkey, appsecret, account_no, account_product_code, paper_trading)
            resp = kis.order().order_rvsecncl(
                OrderRvsecnclBodyBlock(
                    cano="",
                    orgn_odno=original_order_no,
                    rvse_cncl_dvsn_cd="02",  # 취소
                    ord_qty=ord_qty,
                    ord_unpr="0",
                    qty_all_ord_yn=qty_all,
                )
            ).req()

            if resp.error_msg:
                context.log("error", f"KisCancelOrderNode: {resp.error_msg}", node_id)
                return _error(resp.error_msg)

            result = {
                "order_no": original_order_no,
                "cancel_receipt_no": getattr(resp.block, "odno", None),
                "status": "cancelled",
                "paper_trading": paper_trading,
            }
            context.log("info", f"KisCancelOrderNode: 취소 접수 완료 {original_order_no}", node_id)
            return {"cancel_result": result, "cancelled_order_no": original_order_no}

        except Exception as exc:
            context.log("error", f"KisCancelOrderNode 실패: {exc}", node_id)
            return _error(str(exc))
