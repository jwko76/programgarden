"""
Bollinger Bands 크로스 트리거 검증 (v3.1.0)

cross_below_lower/cross_above_upper가 밴드 돌파 순간에만 통과하고 유지 구간에서는
침묵하는지 확인한다. 밴드는 "가격 vs 밴드값" 비교라 직전 캔들의 밴드·가격이 모두 필요.
"""

import pytest
from programgarden_community.plugins.bollinger_bands import (
    bollinger_condition,
    calculate_bollinger_series,
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


PERIOD = 5
STD_DEV = 1.0
FLAT = [100.0] * 6
DECLINE = [FLAT[-1] - i * 3.0 for i in range(1, 8)]
RALLY = [DECLINE[-1] + i * 6.0 for i in range(1, 10)]
CLOSES = FLAT + DECLINE + RALLY


def _series():
    return calculate_bollinger_series(CLOSES, PERIOD, STD_DEV)


def _first_cross_index(direction: str) -> int:
    series = _series()
    start = PERIOD - 1
    for i in range(1, len(series)):
        prev_price = CLOSES[start + i - 1]
        curr_price = CLOSES[start + i]
        prev_bb = series[i - 1]
        curr_bb = series[i]
        if direction == "down" and prev_price >= prev_bb["lower"] and curr_price < curr_bb["lower"]:
            return start + i
        if direction == "up" and prev_price <= prev_bb["upper"] and curr_price > curr_bb["upper"]:
            return start + i
    raise AssertionError(f"cross not found for direction={direction}")


BELOW_CROSS_IDX = _first_cross_index("down")
ABOVE_CROSS_IDX = _first_cross_index("up")


class TestBollingerBandsCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_lower_passes_only_at_crossing(self):
        result = await bollinger_condition(
            data=make_rows(CLOSES[: BELOW_CROSS_IDX + 1]),
            fields={"period": PERIOD, "std_dev": STD_DEV, "position": "cross_below_lower"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_below_lower_silent_while_staying_below(self):
        result = await bollinger_condition(
            data=make_rows(CLOSES[: BELOW_CROSS_IDX + 3]),
            fields={"period": PERIOD, "std_dev": STD_DEV, "position": "cross_below_lower"},
        )
        sr = result["symbol_results"][0]
        assert sr["current_price"] < sr["lower"]
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_upper_passes_only_at_crossing(self):
        result = await bollinger_condition(
            data=make_rows(CLOSES[: ABOVE_CROSS_IDX + 1]),
            fields={"period": PERIOD, "std_dev": STD_DEV, "position": "cross_above_upper"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_upper_silent_while_staying_above(self):
        result = await bollinger_condition(
            data=make_rows(CLOSES[: ABOVE_CROSS_IDX + 3]),
            fields={"period": PERIOD, "std_dev": STD_DEV, "position": "cross_above_upper"},
        )
        sr = result["symbol_results"][0]
        assert sr["current_price"] > sr["upper"]
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_below_lower_insufficient_data_does_not_pass(self):
        """직전 캔들의 밴드값이 없으면(데이터 = period개뿐) 크로스는 통과하지 않는다."""
        result = await bollinger_condition(
            data=make_rows(CLOSES[:PERIOD]),
            fields={"period": PERIOD, "std_dev": STD_DEV, "position": "cross_below_lower"},
        )
        assert result["result"] is False
