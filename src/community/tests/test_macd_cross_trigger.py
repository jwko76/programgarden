"""
MACD 크로스 트리거 검증 (v3.1.0 버그 수정)

bullish_cross/bearish_cross는 히스토그램이 시각화상 이름 그대로 "크로스"여야 하는데,
기존 구현은 histogram>0/macd>0 레벨 체크였다 — 양수 구간 내내 반복 통과해 알림 중복을
유발했다. 이 테스트는 돌파 순간에만 통과하고 유지 구간에서는 침묵하는지 확인한다.
"""

import pytest
from programgarden_community.plugins.macd import macd_condition, calculate_macd_series


def make_rows(closes, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "open": c,
            "high": c,
            "low": c,
            "close": c,
            "volume": 1000,
        }
        for i, c in enumerate(closes)
    ]


def _build_reversal_prices():
    """완만한 하락 → 가속 하락 → 강한 반등 — 히스토그램이 음수에서 양수로 전환되는 종가 시리즈

    (단순 선형 하락은 fast/slow EMA 격차가 상수로 수렴해 histogram이 0 근처에
    머물 뿐 음수로 벌어지지 않는다 — 가속 구간을 넣어야 실제 음수 히스토그램이 나온다.)
    """
    mild = [200.0 - i * 0.5 for i in range(30)]
    steep = [mild[-1] - i * 3.0 for i in range(1, 16)]
    up = [steep[-1] + i * 4.0 for i in range(1, 26)]
    return mild + steep + up


FAST, SLOW, SIGNAL = 12, 26, 9
PRICES = _build_reversal_prices()


def _first_bullish_cross_index() -> int:
    series = calculate_macd_series(PRICES, FAST, SLOW, SIGNAL)
    series_start = len(PRICES) - len(series)
    for i in range(1, len(series)):
        if series[i - 1]["histogram"] < 0 and series[i]["histogram"] >= 0:
            return series_start + i
    raise AssertionError("테스트 데이터에서 bullish cross가 발생하지 않음 — PRICES 조정 필요")


CROSS_IDX = _first_bullish_cross_index()


class TestMacdCrossTrigger:
    @pytest.mark.asyncio
    async def test_bullish_cross_passes_only_at_crossing(self):
        result = await macd_condition(
            data=make_rows(PRICES[: CROSS_IDX + 1]),
            fields={"fast_period": FAST, "slow_period": SLOW, "signal_period": SIGNAL, "signal_type": "bullish_cross"},
        )
        assert result["result"] is True
        sr = result["symbol_results"][0]
        assert sr["prev_histogram"] < 0 and sr["histogram"] >= 0

    @pytest.mark.asyncio
    async def test_bullish_cross_silent_after_holding_positive(self):
        """돌파 이후 며칠 더 지나 히스토그램이 여전히 양수여도 재통과하면 안 됨"""
        result = await macd_condition(
            data=make_rows(PRICES[: CROSS_IDX + 5]),
            fields={"fast_period": FAST, "slow_period": SLOW, "signal_period": SIGNAL, "signal_type": "bullish_cross"},
        )
        sr = result["symbol_results"][0]
        assert sr["histogram"] > 0
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_bearish_cross_silent_while_uptrend_holds(self):
        result = await macd_condition(
            data=make_rows(PRICES[: CROSS_IDX + 5]),
            fields={"fast_period": FAST, "slow_period": SLOW, "signal_period": SIGNAL, "signal_type": "bearish_cross"},
        )
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_insufficient_series_fails_cross(self):
        result = await macd_condition(
            data=make_rows(PRICES[: SLOW + SIGNAL]),  # 크로스 판정에 필요한 이전 값 미확보
            fields={"fast_period": FAST, "slow_period": SLOW, "signal_period": SIGNAL, "signal_type": "bullish_cross"},
        )
        assert result["result"] is False
