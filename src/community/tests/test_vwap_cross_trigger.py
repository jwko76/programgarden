"""
VWAP 크로스 트리거 검증 (v1.1.0)

cross_above/cross_below가 가격이 VWAP을 돌파하는 순간에만 통과하고 유지 구간에서는
침묵하는지 확인한다.
"""

import pytest
from programgarden_community.plugins.vwap import vwap_condition, calculate_vwap_series


def make_rows(closes, volume=1000.0, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "close": c,
            "volume": volume,
        }
        for i, c in enumerate(closes)
    ]


DECLINE = [100.0 - i * 3.0 for i in range(1, 11)]
RALLY = [DECLINE[-1] + i * 8.0 for i in range(1, 10)]
CLOSES = [100.0] + DECLINE + RALLY


def _series():
    return calculate_vwap_series(CLOSES, [1000.0] * len(CLOSES))


def _first_cross_index(direction: str) -> int:
    series = _series()
    for i in range(1, len(series)):
        prev_close, curr_close = CLOSES[i - 1], CLOSES[i]
        prev_vwap, curr_vwap = series[i - 1]["vwap"], series[i]["vwap"]
        if direction == "up" and prev_close <= prev_vwap and curr_close > curr_vwap:
            return i
        if direction == "down" and prev_close >= prev_vwap and curr_close < curr_vwap:
            return i
    raise AssertionError(f"cross not found for direction={direction}")


BELOW_CROSS_IDX = _first_cross_index("down")
ABOVE_CROSS_IDX = _first_cross_index("up")


class TestVWAPCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_passes_only_at_crossing(self):
        result = await vwap_condition(
            data=make_rows(CLOSES[: BELOW_CROSS_IDX + 1]),
            fields={"direction": "cross_below"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_staying_below(self):
        result = await vwap_condition(
            data=make_rows(CLOSES[: BELOW_CROSS_IDX + 3]),
            fields={"direction": "cross_below"},
        )
        sr = result["symbol_results"][0]
        assert sr["current_close"] < sr["vwap"]
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await vwap_condition(
            data=make_rows(CLOSES[: ABOVE_CROSS_IDX + 1]),
            fields={"direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_above(self):
        result = await vwap_condition(
            data=make_rows(CLOSES[: ABOVE_CROSS_IDX + 3]),
            fields={"direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["current_close"] > sr["vwap"]
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_insufficient_data_does_not_pass(self):
        """직전 봉이 없으면(데이터 1개뿐) 크로스는 통과하지 않는다."""
        result = await vwap_condition(
            data=make_rows(CLOSES[:1]),
            fields={"direction": "cross_above"},
        )
        assert result["result"] is False
