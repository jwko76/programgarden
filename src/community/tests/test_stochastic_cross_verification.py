"""
Stochastic 크로스 트리거 확인 (Phase 1 조사 결과)

Phase 1 계획은 stochastic에 RSI 스타일의 cross_oversold/cross_overbought를
새로 추가하는 것이었으나, 코드를 확인해보니 기존 oversold/overbought
방향이 이미 "%K가 %D를 교차하는 순간"에만 통과하는 엣지 트리거였다 —
레벨 유지 중에는 재통과하지 않는다. 그래서 stochastic 플러그인 자체는
수정하지 않았다. 이 테스트는 그 사실을 회귀 방지용으로 고정한다.
"""

import pytest
from programgarden_community.plugins.stochastic import stochastic_condition


def make_rows(closes, symbol="AAPL", exchange="NASDAQ"):
    return [
        {
            "date": f"2026{(i // 28) + 1:02d}{(i % 28) + 1:02d}",
            "symbol": symbol,
            "exchange": exchange,
            "open": c,
            "high": c * 1.01,
            "low": c * 0.99,
            "close": c,
            "volume": 1000,
        }
        for i, c in enumerate(closes)
    ]


# 꾸준한 하락(과매도 진입) 후 완만한 반등 — %K가 %D를 상향 돌파하는 지점을 만든다
DOWN = [200.0 - i * 3.0 for i in range(20)]
BOUNCE = [DOWN[-1] + i * 1.0 for i in range(1, 10)]
CLOSES = DOWN + BOUNCE


class TestStochasticAlreadyEdgeTriggered:
    @pytest.mark.asyncio
    async def test_oversold_passes_at_kd_cross(self):
        result = await stochastic_condition(
            data=make_rows(CLOSES[:21]),
            fields={"k_period": 14, "d_period": 3, "threshold": 20, "direction": "oversold"},
        )
        assert result["result"] is True
        sr = result["symbol_results"][0]
        assert sr["k"] < 20  # 과매도 구간 안에서 발생

    @pytest.mark.asyncio
    async def test_oversold_silent_on_next_bar_without_new_cross(self):
        """돌파 다음 봉에서 %K가 여전히 %D 위에 있어도(새 크로스 아님) 재통과하지 않음"""
        result = await stochastic_condition(
            data=make_rows(CLOSES[:22]),
            fields={"k_period": 14, "d_period": 3, "threshold": 20, "direction": "oversold"},
        )
        assert result["result"] is False
