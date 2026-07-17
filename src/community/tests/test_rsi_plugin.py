"""
RSI 플러그인 테스트 — 레벨(below/above) vs 크로스(cross_below/cross_above) 트리거

크로스 트리거는 임계값을 돌파하는 평가 시점에만 1회 통과하고,
임계값 아래/위에 머무는 동안에는 통과하지 않아야 한다 (알림 중복 방지).
"""

import pytest
from programgarden_community.plugins.rsi import (
    rsi_condition,
    calculate_rsi,
    RSI_SCHEMA,
)


def make_rows(closes, symbol="KRW-BTC", exchange="BITHUMB"):
    """종가 리스트 → 플러그인 입력 행 배열 (oldest-first)"""
    return [
        {
            "date": f"202607{i + 1:02d}",
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


# period=2 기준:
#   마지막 두 delta가 [+1, -5] → RSI ≈ 16.7 (< 30)
#   마지막 두 delta가 [+1, +1] → RSI = 100
#   마지막 두 delta가 [-5, -5] → RSI = 0
UPTREND = [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]           # RSI 100 유지
CROSSING_DOWN = UPTREND + [10.0]                          # 마지막 캔들에서 100 → 16.7 하향 돌파
STAYING_DOWN = UPTREND + [10.0, 5.0]                      # 돌파 후 저지대 유지 (직전도 < 30)


class TestRsiSchema:
    def test_direction_enum_has_cross_modes(self):
        enum = RSI_SCHEMA.fields_schema["direction"]["enum"]
        assert enum == ["below", "above", "cross_below", "cross_above"]


class TestLevelTrigger:
    @pytest.mark.asyncio
    async def test_below_passes_while_oversold(self):
        """레벨 트리거는 과매도 유지 중 매 평가마다 통과 (기존 동작 유지)"""
        for closes in (CROSSING_DOWN, STAYING_DOWN):
            result = await rsi_condition(
                data=make_rows(closes),
                fields={"period": 2, "threshold": 30, "direction": "below"},
            )
            assert result["result"] is True
            assert result["passed_symbols"] == [{"symbol": "KRW-BTC", "exchange": "BITHUMB"}]

    @pytest.mark.asyncio
    async def test_above_passes_while_overbought(self):
        result = await rsi_condition(
            data=make_rows(UPTREND),
            fields={"period": 2, "threshold": 70, "direction": "above"},
        )
        assert result["result"] is True


class TestCrossTrigger:
    @pytest.mark.asyncio
    async def test_cross_below_passes_only_at_crossing(self):
        """하향 돌파 순간에만 통과"""
        result = await rsi_condition(
            data=make_rows(CROSSING_DOWN),
            fields={"period": 2, "threshold": 30, "direction": "cross_below"},
        )
        assert result["result"] is True
        sr = result["symbol_results"][0]
        assert sr["prev_rsi"] >= 30 and sr["rsi"] < 30

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_staying_down(self):
        """저지대 유지 중(직전 캔들도 임계값 아래)에는 통과하지 않음 — 반복 알림 방지"""
        result = await rsi_condition(
            data=make_rows(STAYING_DOWN),
            fields={"period": 2, "threshold": 30, "direction": "cross_below"},
        )
        assert result["result"] is False
        sr = result["symbol_results"][0]
        assert sr["prev_rsi"] < 30 and sr["rsi"] < 30

    @pytest.mark.asyncio
    async def test_cross_below_silent_while_above(self):
        """임계값 위에 머무는 동안에도 통과하지 않음"""
        result = await rsi_condition(
            data=make_rows(UPTREND),
            fields={"period": 2, "threshold": 30, "direction": "cross_below"},
        )
        assert result["result"] is False

    @pytest.mark.asyncio
    async def test_cross_above_passes_only_at_crossing(self):
        """상향 돌파: 저지대에서 급등한 마지막 캔들에서만 통과"""
        downtrend = [15.0, 14.0, 13.0, 12.0, 11.0, 10.0]  # RSI 0 유지
        crossing_up = downtrend + [20.0]                   # 0 → 고RSI 상향 돌파
        result = await rsi_condition(
            data=make_rows(crossing_up),
            fields={"period": 2, "threshold": 70, "direction": "cross_above"},
        )
        assert result["result"] is True

        result2 = await rsi_condition(
            data=make_rows(downtrend),
            fields={"period": 2, "threshold": 70, "direction": "cross_above"},
        )
        assert result2["result"] is False

    @pytest.mark.asyncio
    async def test_cross_signal_marked_once_in_time_series(self):
        """time_series의 signal 마킹도 돌파 캔들 1개에만 붙음"""
        result = await rsi_condition(
            data=make_rows(STAYING_DOWN),
            fields={"period": 2, "threshold": 30, "direction": "cross_below"},
        )
        series = result["values"][0]["time_series"]
        signals = [row for row in series if row["signal"] == "buy"]
        assert len(signals) == 1  # 하향 돌파 캔들(10.0)에만 마킹, 유지 캔들(5.0)에는 없음

    @pytest.mark.asyncio
    async def test_insufficient_data_fails_cross(self):
        """데이터 부족 시 크로스 트리거는 통과하지 않음 (prev RSI 미확보)"""
        result = await rsi_condition(
            data=make_rows([10.0, 11.0]),
            fields={"period": 14, "threshold": 30, "direction": "cross_below"},
        )
        assert result["result"] is False


def test_calculate_rsi_reference_values():
    assert calculate_rsi([10.0, 11.0, 12.0], period=2) == 100.0
    assert calculate_rsi([12.0, 11.0, 10.0], period=2) == 0.0
    assert calculate_rsi([10.0, 11.0, 6.0], period=2) == pytest.approx(16.67, abs=0.01)
