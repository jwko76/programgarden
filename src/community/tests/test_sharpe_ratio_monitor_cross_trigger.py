"""
SharpeRatioMonitor 크로스 트리거 검증 (v1.1.0)

cross_above/cross_below가 샤프비율이 기준값을 돌파하는 순간에만 통과하고 유지
구간에서는 침묵하는지 확인한다. 샤프비율은 롤링 lookback 구간 계산이라 직전 봉
시점 값은 prices[:-1]로 한 봉 앞선 window를 다시 계산해서 구한다.
"""

import pytest
from programgarden_community.plugins.sharpe_ratio_monitor import (
    sharpe_ratio_monitor_condition,
    calculate_sharpe,
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
RISK_FREE = 0.04
THRESHOLD = 1.0


def _build_closes():
    price = 100.0
    closes = [price]
    # 낮은 샤프: 등락을 반복하는 무추세 구간
    for i in range(30):
        r = 0.006 if i % 2 == 0 else -0.006
        price *= (1 + r)
        closes.append(price)
    # 높은 샤프: 꾸준한 상승 추세
    for _ in range(30):
        price *= 1.006
        closes.append(price)
    return closes


CLOSES = _build_closes()


def _first_cross_length() -> int:
    for n in range(LOOKBACK + 2, len(CLOSES) + 1):
        prev = calculate_sharpe(CLOSES[: n - 1], LOOKBACK, RISK_FREE)["sharpe_ratio"]
        curr = calculate_sharpe(CLOSES[:n], LOOKBACK, RISK_FREE)["sharpe_ratio"]
        if prev is not None and curr is not None and prev <= THRESHOLD < curr:
            return n
    raise AssertionError("cross not found")


CROSS_LEN = _first_cross_length()


class TestSharpeRatioMonitorCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        result = await sharpe_ratio_monitor_condition(
            data=make_rows(CLOSES[:CROSS_LEN]),
            fields={"lookback": LOOKBACK, "risk_free_rate": RISK_FREE, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        assert result["result"] is True

    @pytest.mark.asyncio
    async def test_cross_above_silent_while_staying_above(self):
        n = min(CROSS_LEN + 3, len(CLOSES))
        result = await sharpe_ratio_monitor_condition(
            data=make_rows(CLOSES[:n]),
            fields={"lookback": LOOKBACK, "risk_free_rate": RISK_FREE, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        sr = result["symbol_results"][0]
        assert sr["sharpe_ratio"] > THRESHOLD
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_insufficient_data_does_not_pass(self):
        """직전 봉 시점 window가 없으면(데이터 = lookback+1개뿐) 크로스는 통과하지 않는다."""
        result = await sharpe_ratio_monitor_condition(
            data=make_rows(CLOSES[: LOOKBACK + 1]),
            fields={"lookback": LOOKBACK, "risk_free_rate": RISK_FREE, "threshold": THRESHOLD, "direction": "cross_above"},
        )
        assert result["result"] is False
