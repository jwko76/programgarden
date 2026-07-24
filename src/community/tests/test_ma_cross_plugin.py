"""
MovingAverageCross 크로스 트리거 검증 (v3.1.0 버그 수정)

golden/dead cross는 이름 그대로 단기/장기 MA가 서로 뒤바뀌는 순간에만 통과해야
하는데, 기존 구현은 "현재 단기 MA가 장기 MA보다 큰가"라는 레벨 체크였다 —
골든크로스 이후 계속 통과해 알림 중복을 유발했다. 이 테스트는 돌파 순간에만
통과하고 유지 구간에서는 침묵하는지 확인한다.
"""

import pytest
from programgarden_community.plugins.ma_cross import ma_cross_condition, calculate_sma_series


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


SHORT, LONG = 5, 20


def _build_reversal_prices():
    """장기 하락 후 급반등 — 단기 MA가 장기 MA를 상향 돌파하는 종가 시리즈"""
    down = [200.0 - i * 1.0 for i in range(30)]
    up = [down[-1] + i * 4.0 for i in range(1, 15)]
    return down + up


PRICES = _build_reversal_prices()


def _first_golden_cross_index() -> int:
    short_series = calculate_sma_series(PRICES, SHORT)
    long_series = calculate_sma_series(PRICES, LONG)
    short_start = SHORT - 1
    long_start = LONG - 1
    for price_idx in range(long_start + 1, len(PRICES)):
        curr_short = short_series[price_idx - short_start]
        curr_long = long_series[price_idx - long_start]
        prev_short = short_series[price_idx - 1 - short_start]
        prev_long = long_series[price_idx - 1 - long_start]
        if prev_short <= prev_long and curr_short > curr_long:
            return price_idx
    raise AssertionError("테스트 데이터에서 golden cross가 발생하지 않음 — PRICES 조정 필요")


CROSS_IDX = _first_golden_cross_index()


class TestMaCrossTrigger:
    @pytest.mark.asyncio
    async def test_golden_cross_passes_only_at_crossing(self):
        result = await ma_cross_condition(
            data=make_rows(PRICES[: CROSS_IDX + 1]),
            fields={"short_period": SHORT, "long_period": LONG, "cross_type": "golden"},
        )
        assert result["result"] is True
        sr = result["symbol_results"][0]
        assert sr["prev_short_ma"] <= sr["prev_long_ma"]
        assert sr["short_ma"] > sr["long_ma"]

    @pytest.mark.asyncio
    async def test_golden_cross_silent_after_holding_bullish(self):
        """돌파 이후 단기 MA가 계속 장기 MA 위에 있어도 재통과하면 안 됨"""
        result = await ma_cross_condition(
            data=make_rows(PRICES[: CROSS_IDX + 5]),
            fields={"short_period": SHORT, "long_period": LONG, "cross_type": "golden"},
        )
        sr = result["symbol_results"][0]
        assert sr["short_ma"] > sr["long_ma"]
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_dead_cross_silent_while_bullish_holds(self):
        result = await ma_cross_condition(
            data=make_rows(PRICES[: CROSS_IDX + 5]),
            fields={"short_period": SHORT, "long_period": LONG, "cross_type": "dead"},
        )
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_insufficient_series_fails_cross(self):
        result = await ma_cross_condition(
            data=make_rows(PRICES[:LONG]),  # prev MA 확보 불가
            fields={"short_period": SHORT, "long_period": LONG, "cross_type": "golden"},
        )
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_time_series_short_ma_matches_actual_window(self):
        """time_series의 각 행 short_ma가 그 시점 기준 실제 short_period봉 평균과 일치해야 함
        (회귀 방지 — short_idx 인덱스 정렬 버그, 2026-07-24 발견)."""
        result = await ma_cross_condition(
            data=make_rows(PRICES),
            fields={"short_period": SHORT, "long_period": LONG, "cross_type": "golden"},
        )
        ts = result["values"][0]["time_series"]
        for row_idx, row in enumerate(ts):
            original_idx = (LONG - 1) + row_idx
            expected = sum(PRICES[original_idx - SHORT + 1: original_idx + 1]) / SHORT
            assert abs(row["short_ma"] - expected) < 0.01, (
                f"row {row_idx}(date={row['date']}): short_ma={row['short_ma']}, expected={expected}"
            )
