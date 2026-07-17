"""MFI 크로스 트리거 검증 (v1.1.0) — cross_below/cross_above가 임계값 돌파 순간에만 통과하는지 확인"""

import pytest
from programgarden_community.plugins.mfi import mfi_condition, calculate_mfi_series


def make_rows(closes, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "high": c * 1.002,
            "low": c * 0.998,
            "close": c,
            "volume": 1000,
        }
        for i, c in enumerate(closes)
    ]


PERIOD = 14
OVERSOLD = 20.0
OVERBOUGHT = 80.0
FLAT = [100.0] * 16
DECLINE = [FLAT[-1] - i * 3.0 for i in range(1, 16)]
RALLY = [DECLINE[-1] + i * 4.0 for i in range(1, 16)]
CLOSES = FLAT + DECLINE + RALLY


def _series():
    highs = [c * 1.002 for c in CLOSES]
    lows = [c * 0.998 for c in CLOSES]
    vols = [1000.0] * len(CLOSES)
    return calculate_mfi_series(highs, lows, CLOSES, vols, PERIOD)


def _first_cross_price_index(target: float, direction: str) -> int:
    series = _series()
    start = PERIOD + 1
    for i in range(1, len(series)):
        prev_v, curr_v = series[i - 1], series[i]
        if direction == "down" and prev_v >= target and curr_v < target:
            return start + i - 1
        if direction == "up" and prev_v <= target and curr_v > target:
            return start + i - 1
    raise AssertionError(f"cross not found for target={target} direction={direction}")


OVERSOLD_CROSS_IDX = _first_cross_price_index(OVERSOLD, "down")
OVERBOUGHT_CROSS_IDX = _first_cross_price_index(OVERBOUGHT, "up")


class TestMfiCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_passes_only_at_crossing(self):
        result = await mfi_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 1]),
            fields={"period": PERIOD, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_below"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_staying_low(self):
        result = await mfi_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 3]),
            fields={"period": PERIOD, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_below"},
        )
        sr = result["symbol_results"][0]
        assert sr["mfi"] < OVERSOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await mfi_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 1]),
            fields={"period": PERIOD, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_high(self):
        result = await mfi_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 3]),
            fields={"period": PERIOD, "oversold": OVERSOLD, "overbought": OVERBOUGHT, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["mfi"] > OVERBOUGHT
        assert result["result"] is False
