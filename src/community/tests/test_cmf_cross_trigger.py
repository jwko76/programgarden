"""
CMF (Chaikin Money Flow) 크로스 트리거 검증 (v1.1.0)

cross_accumulation/cross_distribution이 매집/분산 구간 진입 순간에만 통과하고
유지 구간에서는 침묵하는지 확인한다.
"""

import pytest
from programgarden_community.plugins.cmf import cmf_condition, calculate_cmf_series


def make_rows(mfms, volume=1000.0, symbol="AAPL", exchange="NASDAQ"):
    rows = []
    price = 100.0
    for i, mfm in enumerate(mfms):
        high = price + 1.0
        low = price - 1.0
        if mfm > 0:
            close = high
        elif mfm < 0:
            close = low
        else:
            close = price
        rows.append({
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })
        price += 0.01
    return rows


PERIOD = 5
THRESHOLD = 0.05
# 중립 구간(mfm=0) -> 매집 구간(mfm=+1) -> 분산 구간(mfm=-1)
MFMS = [0] * 6 + [1] * 7 + [-1] * 10
ROWS = make_rows(MFMS)


def _series():
    highs = [r["high"] for r in ROWS]
    lows = [r["low"] for r in ROWS]
    closes = [r["close"] for r in ROWS]
    vols = [r["volume"] for r in ROWS]
    return calculate_cmf_series(highs, lows, closes, vols, PERIOD)


def _first_cross_index(direction: str) -> int:
    series = _series()
    start = PERIOD - 1
    for i in range(1, len(series)):
        prev_cmf, curr_cmf = series[i - 1]["cmf"], series[i]["cmf"]
        if direction == "up" and prev_cmf <= THRESHOLD and curr_cmf > THRESHOLD:
            return start + i
        if direction == "down" and prev_cmf >= -THRESHOLD and curr_cmf < -THRESHOLD:
            return start + i
    raise AssertionError(f"cross not found for direction={direction}")


ACCUMULATION_CROSS_IDX = _first_cross_index("up")
DISTRIBUTION_CROSS_IDX = _first_cross_index("down")


class TestCMFCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_accumulation_passes_only_at_crossing(self):
        result = await cmf_condition(
            data=make_rows(MFMS[: ACCUMULATION_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_accumulation"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_accumulation_silent_while_staying(self):
        result = await cmf_condition(
            data=make_rows(MFMS[: ACCUMULATION_CROSS_IDX + 3]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_accumulation"},
        )
        sr = result["symbol_results"][0]
        assert sr["cmf"] > THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_distribution_passes_only_at_crossing(self):
        result = await cmf_condition(
            data=make_rows(MFMS[: DISTRIBUTION_CROSS_IDX + 1]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_distribution"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_distribution_silent_while_staying(self):
        result = await cmf_condition(
            data=make_rows(MFMS[: DISTRIBUTION_CROSS_IDX + 3]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_distribution"},
        )
        sr = result["symbol_results"][0]
        assert sr["cmf"] < -THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_accumulation_insufficient_data_does_not_pass(self):
        """직전 CMF 값이 없으면(데이터 = period개뿐) 크로스는 통과하지 않는다."""
        result = await cmf_condition(
            data=make_rows(MFMS[:PERIOD]),
            fields={"period": PERIOD, "threshold": THRESHOLD, "direction": "cross_accumulation"},
        )
        assert result["result"] is False
