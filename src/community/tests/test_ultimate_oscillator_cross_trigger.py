"""UltimateOscillator 크로스 트리거 검증 (v1.1.0) — cross_below/cross_above가 임계값 돌파 순간에만 통과하는지 확인"""

import pytest
from programgarden_community.plugins.ultimate_oscillator import (
    ultimate_oscillator_condition,
    calculate_ultimate_oscillator,
)


def make_rows(closes, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "high": c * 1.005,
            "low": c * 0.995,
            "close": c,
        }
        for i, c in enumerate(closes)
    ]


P1, P2, P3 = 7, 14, 28
OVERSOLD = 30.0
OVERBOUGHT = 70.0
FLAT = [100.0] * 30
DECLINE = [FLAT[-1] - i * 2.0 for i in range(1, 20)]
RALLY = [DECLINE[-1] + i * 3.0 for i in range(1, 20)]
CLOSES = FLAT + DECLINE + RALLY


def _series():
    highs = [c * 1.005 for c in CLOSES]
    lows = [c * 0.995 for c in CLOSES]
    return calculate_ultimate_oscillator(highs, lows, CLOSES, P1, P2, P3)


def _first_cross_price_index(target: float, direction: str) -> int:
    series = _series()
    prev_idx, prev_v = None, None
    for i, v in enumerate(series):
        if v is None:
            continue
        if prev_v is not None:
            if direction == "down" and prev_v > target and v <= target:
                return i
            if direction == "up" and prev_v < target and v >= target:
                return i
        prev_idx, prev_v = i, v
    raise AssertionError(f"cross not found for target={target} direction={direction}")


OVERSOLD_CROSS_IDX = _first_cross_price_index(OVERSOLD, "down")
OVERBOUGHT_CROSS_IDX = _first_cross_price_index(OVERBOUGHT, "up")


class TestUltimateOscillatorCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_passes_only_at_crossing(self):
        result = await ultimate_oscillator_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 1]),
            fields={"period1": P1, "period2": P2, "period3": P3, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_below"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_staying_low(self):
        result = await ultimate_oscillator_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 3]),
            fields={"period1": P1, "period2": P2, "period3": P3, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_below"},
        )
        sr = result["symbol_results"][0]
        assert sr["uo"] < OVERSOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await ultimate_oscillator_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 1]),
            fields={"period1": P1, "period2": P2, "period3": P3, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_high(self):
        result = await ultimate_oscillator_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 3]),
            fields={"period1": P1, "period2": P2, "period3": P3, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["uo"] > OVERBOUGHT
        assert result["result"] is False
