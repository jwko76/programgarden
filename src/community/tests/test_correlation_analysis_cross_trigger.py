"""
CorrelationAnalysis 크로스 트리거 검증 (v1.1.0)

cross_above/cross_below가 최대상관계수가 기준값을 돌파하는 순간에만 통과하고 유지
구간에서는 침묵하는지 확인한다. 상관계수는 두 종목(+벤치마크 없음) population
기반이라, 직전 봉 시점 상관계수를 재계산하는 _compute_symbol_max_corr 헬퍼가 필요했다.
"""

import asyncio

import pytest
from programgarden_community.plugins.correlation_analysis import correlation_analysis_condition


def make_rows(prices, symbol, exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "close": p,
        }
        for i, p in enumerate(prices)
    ]


LOOKBACK = 15
THRESHOLD = 0.8


def _build_prices():
    price_a, price_b = 100.0, 100.0
    prices_a, prices_b = [price_a], [price_b]
    # 구간 1: 정반대로 움직이는 음의 상관 구간
    for i in range(25):
        ra = 0.02 if i % 2 == 0 else -0.02
        rb = -ra
        price_a *= (1 + ra)
        price_b *= (1 + rb)
        prices_a.append(price_a)
        prices_b.append(price_b)
    # 구간 2: 완전히 같이 움직이는 양의 상관 구간(변동폭은 매일 다름)
    for i in range(25):
        r = 0.01 + 0.001 * i
        price_a *= (1 + r)
        price_b *= (1 + r)
        prices_a.append(price_a)
        prices_b.append(price_b)
    return prices_a, prices_b


PRICES_A, PRICES_B = _build_prices()


def _data_upto(n):
    return make_rows(PRICES_A[:n], "A") + make_rows(PRICES_B[:n], "B")


async def _max_corr_at(n):
    result = await correlation_analysis_condition(
        data=_data_upto(n),
        fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "above", "method": "pearson"},
    )
    sr = next((r for r in result["symbol_results"] if r.get("symbol") == "A"), None)
    return sr.get("max_correlation") if sr else None


def _first_cross_length() -> int:
    for n in range(LOOKBACK + 2, len(PRICES_A) + 1):
        prev = asyncio.run(_max_corr_at(n - 1))
        curr = asyncio.run(_max_corr_at(n))
        if prev is not None and curr is not None and prev <= THRESHOLD < curr:
            return n
    raise AssertionError("cross not found")


CROSS_LEN = _first_cross_length()


class TestCorrelationAnalysisCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await correlation_analysis_condition(
            data=_data_upto(CROSS_LEN),
            fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "cross_above", "method": "pearson"},
        )
        passed_syms = [s["symbol"] for s in result["passed_symbols"]]
        assert "A" in passed_syms

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_above(self):
        n = min(CROSS_LEN + 3, len(PRICES_A))
        result = await correlation_analysis_condition(
            data=_data_upto(n),
            fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "cross_above", "method": "pearson"},
        )
        passed_syms = [s["symbol"] for s in result["passed_symbols"]]
        assert "A" not in passed_syms

    @pytest.mark.asyncio
    async def test_cross_above_insufficient_data_does_not_pass(self):
        """직전 봉 시점에는 lookback을 채우지 못해(딱 lookback개) 크로스는 통과하지 않는다."""
        result = await correlation_analysis_condition(
            data=_data_upto(LOOKBACK),
            fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "cross_above", "method": "pearson"},
        )
        passed_syms = [s["symbol"] for s in result["passed_symbols"]]
        assert "A" not in passed_syms
