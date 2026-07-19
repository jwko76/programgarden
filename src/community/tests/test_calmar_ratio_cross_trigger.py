"""
CalmarRatio 크로스 트리거 검증 (v1.1.0)

cross_above/cross_below가 칼마비율이 기준값을 돌파하는 순간에만 통과하고 유지
구간에서는 침묵하는지 확인한다.
"""

import pytest
from programgarden_community.plugins.calmar_ratio import (
    calmar_ratio_condition,
    calculate_calmar,
)


def make_rows(closes, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "close": c,
        }
        for i, c in enumerate(closes)
    ]


LOOKBACK = 60
THRESHOLD = 1.0


def _build_closes():
    price = 100.0
    closes = [price]
    # 낮은 칼마: 잦은 큰 낙폭이 섞인 완만한 하락 구간
    for i in range(70):
        r = 0.01 if i % 3 != 0 else -0.03
        price *= (1 + r)
        closes.append(price)
    # 높은 칼마: 꾸준한 상승 + 작은 눌림목만 존재
    for i in range(70):
        r = 0.012 if i % 5 != 0 else -0.002
        price *= (1 + r)
        closes.append(price)
    return closes


CLOSES = _build_closes()


def _is_finite(v):
    return v is not None and v == v and v not in (float("inf"), float("-inf"))


def _first_cross_length() -> int:
    for n in range(LOOKBACK + 2, len(CLOSES) + 1):
        prev = calculate_calmar(CLOSES[: n - 1], LOOKBACK)["calmar_ratio"]
        curr = calculate_calmar(CLOSES[:n], LOOKBACK)["calmar_ratio"]
        if _is_finite(prev) and _is_finite(curr) and prev <= THRESHOLD < curr:
            return n
    raise AssertionError("cross not found")


CROSS_LEN = _first_cross_length()


class TestCalmarRatioCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await calmar_ratio_condition(
            data=make_rows(CLOSES[:CROSS_LEN]),
            fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_above(self):
        n = min(CROSS_LEN + 3, len(CLOSES))
        result = await calmar_ratio_condition(
            data=make_rows(CLOSES[:n]),
            fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["calmar_ratio"] > THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_insufficient_data_does_not_pass(self):
        """직전 봉 시점 window가 없으면(데이터 = lookback+1개뿐) 크로스는 통과하지 않는다."""
        result = await calmar_ratio_condition(
            data=make_rows(CLOSES[: LOOKBACK + 1]),
            fields={"lookback": LOOKBACK, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        assert result["result"] is False
