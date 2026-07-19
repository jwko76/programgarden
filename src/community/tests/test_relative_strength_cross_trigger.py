"""
RelativeStrength 크로스 트리거 검증 (v1.1.0)

cross_above/cross_below가 RS 점수(rank_method=raw)가 기준값을 돌파하는 순간에만
통과하고 유지 구간에서는 침묵하는지 확인한다. RS 랭킹은 전체 종목·벤치마크 population
기반이라, 직전 봉 시점 랭킹을 재계산하는 _rank_relative_strength 헬퍼가 필요했다.
"""

import asyncio

import pytest
from programgarden_community.plugins.relative_strength import relative_strength_condition


def make_rows(closes, symbol, exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "close": c,
        }
        for i, c in enumerate(closes)
    ]


LOOKBACK = 10
DAYS = 40

SPY_CLOSES = [100.0 * (1.001 ** i) for i in range(DAYS)]

AAPL_CLOSES = []
_price = 100.0
for _i in range(DAYS):
    _price *= 0.999 if _i < 25 else 1.02
    AAPL_CLOSES.append(_price)


def _data_upto(n):
    return make_rows(SPY_CLOSES[:n], "SPY") + make_rows(AAPL_CLOSES[:n], "AAPL")


async def _aapl_rs_raw(n):
    result = await relative_strength_condition(
        data=_data_upto(n),
        fields={"lookback": LOOKBACK, "benchmark_symbol": "SPY", "rank_method": "raw", "threshold": 0.0, "direction": "above"},
    )
    sr = next((r for r in result["symbol_results"] if r.get("symbol") == "AAPL"), None)
    return sr.get("rs_score") if sr else None


def _first_cross_length() -> int:
    for n in range(LOOKBACK + 2, DAYS + 1):
        prev = asyncio.run(_aapl_rs_raw(n - 1))
        curr = asyncio.run(_aapl_rs_raw(n))
        if prev is not None and curr is not None and prev <= 0 < curr:
            return n
    raise AssertionError("cross not found")


CROSS_LEN = _first_cross_length()


class TestRelativeStrengthCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await relative_strength_condition(
            data=_data_upto(CROSS_LEN),
            fields={"lookback": LOOKBACK, "benchmark_symbol": "SPY", "rank_method": "raw", "threshold": 0.0, "direction": "cross_above"},
        )
        passed_syms = [s["symbol"] for s in result["passed_symbols"]]
        assert "AAPL" in passed_syms

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_above(self):
        n = min(CROSS_LEN + 3, DAYS)
        result = await relative_strength_condition(
            data=_data_upto(n),
            fields={"lookback": LOOKBACK, "benchmark_symbol": "SPY", "rank_method": "raw", "threshold": 0.0, "direction": "cross_above"},
        )
        passed_syms = [s["symbol"] for s in result["passed_symbols"]]
        assert "AAPL" not in passed_syms

    @pytest.mark.asyncio
    async def test_cross_above_insufficient_data_does_not_pass(self):
        """직전 봉 시점에는 lookback을 채우지 못해(딱 lookback+1개) 크로스는 통과하지 않는다."""
        result = await relative_strength_condition(
            data=_data_upto(LOOKBACK + 1),
            fields={"lookback": LOOKBACK, "benchmark_symbol": "SPY", "rank_method": "raw", "threshold": 0.0, "direction": "cross_above"},
        )
        passed_syms = [s["symbol"] for s in result["passed_symbols"]]
        assert "AAPL" not in passed_syms
