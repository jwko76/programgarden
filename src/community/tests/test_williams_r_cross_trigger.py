"""
Williams %R 크로스 트리거 검증 (v1.1.0)

cross_oversold/cross_overbought가 임계값 돌파 순간에만 통과하고 유지 구간에서는
침묵하는지 확인한다. 부수적으로 overbought_threshold 공식 버그
(threshold+100 → -100-threshold, %R 범위는 -100~0)도 이 버전에서 함께 고쳤다.
"""

import pytest
from programgarden_community.plugins.williams_r import williams_r_condition, calculate_williams_r_series


def make_rows(closes, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "high": c * 1.005,
            "low": c * 0.995,
            "close": c,
            "volume": 1000,
        }
        for i, c in enumerate(closes)
    ]


PERIOD = 5
FLAT = [100.0] * 6
DECLINE = [FLAT[-1] - i * 2.0 for i in range(1, 8)]
RALLY = [DECLINE[-1] + i * 5.0 for i in range(1, 10)]
CLOSES = FLAT + DECLINE + RALLY
THRESHOLD = -80.0
OVERBOUGHT = -20.0


def _series():
    highs = [c * 1.005 for c in CLOSES]
    lows = [c * 0.995 for c in CLOSES]
    return calculate_williams_r_series(highs, lows, CLOSES, PERIOD)


def _first_cross_price_index(target: float, direction: str) -> int:
    series = _series()
    start = PERIOD - 1
    for i in range(1, len(series)):
        prev_wr = series[i - 1]["williams_r"]
        curr_wr = series[i]["williams_r"]
        if direction == "down" and prev_wr > target and curr_wr <= target:
            return start + i
        if direction == "up" and prev_wr < target and curr_wr >= target:
            return start + i
    raise AssertionError(f"cross not found for target={target} direction={direction}")


OVERSOLD_CROSS_IDX = _first_cross_price_index(THRESHOLD, "down")
OVERBOUGHT_CROSS_IDX = _first_cross_price_index(OVERBOUGHT, "up")


class TestWilliamsRCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_oversold_passes_only_at_crossing(self):
        result = await williams_r_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_oversold"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_oversold_silent_while_staying_low(self):
        result = await williams_r_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 3]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_oversold"},
        )
        sr = result["symbol_results"][0]
        assert sr["williams_r"] <= THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_overbought_passes_only_at_crossing(self):
        result = await williams_r_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_overbought"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_overbought_silent_while_staying_high(self):
        result = await williams_r_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 3]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_overbought"},
        )
        sr = result["symbol_results"][0]
        assert sr["williams_r"] >= OVERBOUGHT
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_overbought_threshold_reachable(self):
        """버그 수정 확인: 기본 threshold(-80)에서 overbought_threshold는 -20이어야 하고,
        레벨 트리거 overbought 방향이 실제로 통과할 수 있어야 한다."""
        result = await williams_r_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "overbought"},
        )
        assert result["result"] is True
