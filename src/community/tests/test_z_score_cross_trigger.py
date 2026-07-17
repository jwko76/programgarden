"""Z-Score 크로스 트리거 검증 (v1.1.0) — cross_below/cross_above가 임계값 돌파 순간에만 통과하는지 확인"""

import pytest
from programgarden_community.plugins.z_score import z_score_condition, calculate_z_score_series


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


LOOKBACK = 20
ENTRY = 2.0
FLAT = [100.0] * 20
DECLINE = [FLAT[-1] - i * 1.5 for i in range(1, 10)]
RALLY = [DECLINE[-1] + i * 3.0 for i in range(1, 12)]
CLOSES = FLAT + DECLINE + RALLY


def _series():
    return calculate_z_score_series(CLOSES, LOOKBACK)


def _first_cross_price_index(target: float, direction: str) -> int:
    series = _series()
    start = LOOKBACK - 1
    for i in range(1, len(series)):
        prev_v = series[i - 1]["z_score"]
        curr_v = series[i]["z_score"]
        if direction == "down" and prev_v >= target and curr_v < target:
            return start + i
        if direction == "up" and prev_v <= target and curr_v > target:
            return start + i
    raise AssertionError(f"cross not found for target={target} direction={direction}")


CROSS_BELOW_IDX = _first_cross_price_index(-ENTRY, "down")
CROSS_ABOVE_IDX = _first_cross_price_index(ENTRY, "up")


class TestZScoreCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_passes_only_at_crossing(self):
        result = await z_score_condition(
            data=make_rows(CLOSES[: CROSS_BELOW_IDX + 1]),
            fields={"lookback": LOOKBACK, "entry_threshold": ENTRY, "direction": "cross_below"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_staying_low(self):
        result = await z_score_condition(
            data=make_rows(CLOSES[: CROSS_BELOW_IDX + 3]),
            fields={"lookback": LOOKBACK, "entry_threshold": ENTRY, "direction": "cross_below"},
        )
        sr = result["symbol_results"][0]
        assert sr["z_score"] < -ENTRY
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await z_score_condition(
            data=make_rows(CLOSES[: CROSS_ABOVE_IDX + 1]),
            fields={"lookback": LOOKBACK, "entry_threshold": ENTRY, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_high(self):
        result = await z_score_condition(
            data=make_rows(CLOSES[: CROSS_ABOVE_IDX + 3]),
            fields={"lookback": LOOKBACK, "entry_threshold": ENTRY, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["z_score"] > ENTRY
        assert result["result"] is False
