"""ConnorsRSI 크로스 트리거 검증 (v1.1.0) — cross_below/cross_above가 임계값 돌파 순간에만 통과하는지 확인"""

import pytest
from programgarden_community.plugins.connors_rsi import connors_rsi_condition, calculate_connors_rsi


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


RSI_PERIOD, STREAK_PERIOD, PCT_RANK_PERIOD = 3, 2, 20
THRESHOLD = 10.0
OVERBOUGHT_LEVEL = 100.0 - THRESHOLD

FLAT = [100.0] * 25
DECLINE = [FLAT[-1] - i * 2.0 for i in range(1, 15)]
RALLY = [DECLINE[-1] + i * 6.0 for i in range(1, 20)]
CLOSES = FLAT + DECLINE + RALLY

FIELDS_BASE = {
    "rsi_period": RSI_PERIOD,
    "streak_period": STREAK_PERIOD,
    "pct_rank_period": PCT_RANK_PERIOD,
    "threshold": THRESHOLD,
}


def _crsi_at(n: int):
    r = calculate_connors_rsi(CLOSES[:n], RSI_PERIOD, STREAK_PERIOD, PCT_RANK_PERIOD)
    return r["connors_rsi"] if r else None


def _first_cross_length(target: float, direction: str) -> int:
    min_required = max(RSI_PERIOD, STREAK_PERIOD, PCT_RANK_PERIOD) + 2
    prev = _crsi_at(min_required)
    for n in range(min_required + 1, len(CLOSES) + 1):
        curr = _crsi_at(n)
        if curr is not None and prev is not None:
            if direction == "down" and prev >= target and curr < target:
                return n
            if direction == "up" and prev <= target and curr > target:
                return n
        prev = curr
    raise AssertionError(f"cross not found for target={target} direction={direction}")


CROSS_BELOW_LEN = _first_cross_length(THRESHOLD, "down")
CROSS_ABOVE_LEN = _first_cross_length(OVERBOUGHT_LEVEL, "up")


class TestConnorsRsiCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_passes_only_at_crossing(self):
        result = await connors_rsi_condition(
            data=make_rows(CLOSES[:CROSS_BELOW_LEN]),
            fields={**FIELDS_BASE, "direction": "cross_below"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_staying_low(self):
        result = await connors_rsi_condition(
            data=make_rows(CLOSES[:CROSS_BELOW_LEN + 2]),
            fields={**FIELDS_BASE, "direction": "cross_below"},
        )
        sr = result["symbol_results"][0]
        assert sr["connors_rsi"] < THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await connors_rsi_condition(
            data=make_rows(CLOSES[:CROSS_ABOVE_LEN]),
            fields={**FIELDS_BASE, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_high(self):
        result = await connors_rsi_condition(
            data=make_rows(CLOSES[:CROSS_ABOVE_LEN + 2]),
            fields={**FIELDS_BASE, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["connors_rsi"] > OVERBOUGHT_LEVEL
        assert result["result"] is False
