"""CCI 크로스 트리거 검증 (v1.1.0) — cross_oversold/cross_overbought가 임계값 돌파 순간에만 통과하는지 확인"""

import pytest
from programgarden_community.plugins.cci import cci_condition, calculate_cci_series


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


PERIOD = 20
THRESHOLD = 100.0
FLAT = [100.0] * 22
DECLINE = [FLAT[-1] - i * 3.0 for i in range(1, 10)]
RALLY = [DECLINE[-1] + i * 6.0 for i in range(1, 12)]
CLOSES = FLAT + DECLINE + RALLY


def _series():
    highs = [c * 1.002 for c in CLOSES]
    lows = [c * 0.998 for c in CLOSES]
    return calculate_cci_series(highs, lows, CLOSES, PERIOD)


def _first_cross_price_index(target: float, direction: str) -> int:
    series = _series()
    start = PERIOD - 1
    for i in range(1, len(series)):
        prev_v = series[i - 1]["cci"]
        curr_v = series[i]["cci"]
        if direction == "down" and prev_v > target and curr_v <= target:
            return start + i
        if direction == "up" and prev_v < target and curr_v >= target:
            return start + i
    raise AssertionError(f"cross not found for target={target} direction={direction}")


OVERSOLD_CROSS_IDX = _first_cross_price_index(-THRESHOLD, "down")
OVERBOUGHT_CROSS_IDX = _first_cross_price_index(THRESHOLD, "up")


class TestCciCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_oversold_passes_only_at_crossing(self):
        result = await cci_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_oversold"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_oversold_silent_while_staying_low(self):
        result = await cci_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 3]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_oversold"},
        )
        sr = result["symbol_results"][0]
        assert sr["cci"] <= -THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_overbought_passes_only_at_crossing(self):
        result = await cci_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_overbought"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_overbought_silent_while_staying_high(self):
        result = await cci_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 3]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_overbought"},
        )
        sr = result["symbol_results"][0]
        assert sr["cci"] >= THRESHOLD
        assert result["result"] is False
