"""
SortinoRatio 크로스 트리거 검증 (v1.1.0)

cross_above/cross_below가 소르티노비율이 기준값을 돌파하는 순간에만 통과하고 유지
구간에서는 침묵하는지 확인한다.
"""

import pytest
from programgarden_community.plugins.sortino_ratio import (
    sortino_ratio_condition,
    calculate_sortino,
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


LOOKBACK = 20
MAR = 0.0
THRESHOLD = 1.5


def _build_closes():
    price = 100.0
    closes = [price]
    # 낮은 소르티노: 하락이 잦은 무추세 구간
    for i in range(30):
        r = 0.004 if i % 2 == 0 else -0.008
        price *= (1 + r)
        closes.append(price)
    # 높은 소르티노: 꾸준한 상승 추세(하방 변동 거의 없음)
    for _ in range(30):
        price *= 1.006
        closes.append(price)
    return closes


CLOSES = _build_closes()


def _first_cross_length() -> int:
    for n in range(LOOKBACK + 2, len(CLOSES) + 1):
        prev = calculate_sortino(CLOSES[: n - 1], LOOKBACK, MAR)["sortino_ratio"]
        curr = calculate_sortino(CLOSES[:n], LOOKBACK, MAR)["sortino_ratio"]
        if prev is not None and curr is not None and prev <= THRESHOLD < curr:
            return n
    raise AssertionError("cross not found")


CROSS_LEN = _first_cross_length()


class TestSortinoRatioCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await sortino_ratio_condition(
            data=make_rows(CLOSES[:CROSS_LEN]),
            fields={"lookback": LOOKBACK, "mar": MAR, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_above(self):
        n = min(CROSS_LEN + 3, len(CLOSES))
        result = await sortino_ratio_condition(
            data=make_rows(CLOSES[:n]),
            fields={"lookback": LOOKBACK, "mar": MAR, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["sortino_ratio"] > THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_insufficient_data_does_not_pass(self):
        """직전 봉 시점 window가 없으면(데이터 = lookback+1개뿐) 크로스는 통과하지 않는다."""
        result = await sortino_ratio_condition(
            data=make_rows(CLOSES[: LOOKBACK + 1]),
            fields={"lookback": LOOKBACK, "mar": MAR, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        assert result["result"] is False
