"""MeanReversion 크로스 트리거 검증 (v1.1.0) — cross_oversold/cross_overbought가 밴드 돌파 순간에만 통과하는지 확인"""

import pytest
from programgarden_community.plugins.mean_reversion import mean_reversion_condition, calculate_mean_reversion_series


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


MA_PERIOD = 20
DEVIATION = 2.0
FLAT = [100.0] * 20
DECLINE = [FLAT[-1] - i * 1.5 for i in range(1, 10)]
RALLY = [DECLINE[-1] + i * 3.0 for i in range(1, 12)]
CLOSES = FLAT + DECLINE + RALLY


def _series():
    return calculate_mean_reversion_series(CLOSES, MA_PERIOD, DEVIATION)


def _first_cross_price_index(direction: str) -> int:
    series = _series()
    start = MA_PERIOD - 1
    for i in range(1, len(series)):
        prev_close = CLOSES[start + i - 1]
        curr_close = CLOSES[start + i]
        prev_band = series[i - 1]
        curr_band = series[i]
        if direction == "oversold" and prev_close >= prev_band["lower"] and curr_close < curr_band["lower"]:
            return start + i
        if direction == "overbought" and prev_close <= prev_band["upper"] and curr_close > curr_band["upper"]:
            return start + i
    raise AssertionError(f"cross not found for direction={direction}")


OVERSOLD_CROSS_IDX = _first_cross_price_index("oversold")
OVERBOUGHT_CROSS_IDX = _first_cross_price_index("overbought")


class TestMeanReversionCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_oversold_passes_only_at_crossing(self):
        result = await mean_reversion_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 1]),
            fields={"ma_period": MA_PERIOD, "deviation": DEVIATION, "direction": "cross_oversold"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_oversold_silent_while_staying_low(self):
        result = await mean_reversion_condition(
            data=make_rows(CLOSES[: OVERSOLD_CROSS_IDX + 3]),
            fields={"ma_period": MA_PERIOD, "deviation": DEVIATION, "direction": "cross_oversold"},
        )
        sr = result["symbol_results"][0]
        assert sr["current_price"] < sr["lower"]
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_overbought_passes_only_at_crossing(self):
        result = await mean_reversion_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 1]),
            fields={"ma_period": MA_PERIOD, "deviation": DEVIATION, "direction": "cross_overbought"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_overbought_silent_while_staying_high(self):
        result = await mean_reversion_condition(
            data=make_rows(CLOSES[: OVERBOUGHT_CROSS_IDX + 3]),
            fields={"ma_period": MA_PERIOD, "deviation": DEVIATION, "direction": "cross_overbought"},
        )
        sr = result["symbol_results"][0]
        assert sr["current_price"] > sr["upper"]
        assert result["result"] is False
