# [Fix] MovingAverageCross `time_series.short_ma` 인덱스 정렬 버그 수정 보고서

- **대상 버그**: [ma_cross_time_series_short_ma_lag.md](./ma_cross_time_series_short_ma_lag.md)
- **파일**: `src/community/programgarden_community/plugins/ma_cross/__init__.py`
- **버전**: 플러그인 `MA_CROSS_SCHEMA.version` 3.1.0 → **3.1.1**, 패키지 `programgarden-community` 1.17.0 → **1.17.1**
- **해결일**: 2026-07-24

## 요약

`ma_cross_condition()`이 반환하는 `values[].time_series[]`의 각 행 `short_ma`가
`(long_period - 2·short_period + 1)`봉만큼 과거의 stale한 값을 가리키던 버그를 수정했다
(기본값 `short_period=5, long_period=20` 기준 11봉 지연). `long_ma`, `symbol_results`,
`passed_symbols`/`result`는 원래부터 정상이었고 `time_series`의 `short_ma`만 잘못됐다.

## 원인

`calculate_sma_series(prices, period)`가 반환하는 배열의 인덱스 `k`는 원본 `prices`의
인덱스 `(period - 1 + k)`에 대응한다. `long_ma`는 이 정렬을 올바르게 반영했지만
(`long_ma_series[i - (long_period - 1)]`), `short_ma`는 잘못된 오프셋을 썼다.

```python
# 수정 전 (147행)
short_idx = i - (long_period - short_period)
```

## 수정

`long_ma`와 동일한 정렬 방식으로 맞췄다.

```python
# 수정 후 (147행)
short_idx = i - (short_period - 1)
```

`prev_short = short_ma_series[short_idx - 1]`(158행 근처)은 `short_idx` 계산이 고쳐지면서
코드 변경 없이 자동으로 함께 정상화됐다.

## 회귀 테스트

`src/community/tests/test_ma_cross_plugin.py`에 `time_series`의 각 행 `short_ma`가
그 시점 기준 실제 슬라이딩 윈도우 평균과 일치하는지 전수 검증하는 테스트를 추가했다
(기존 테스트들은 최종 시점 `symbol_results`만 간접 검증해 이 버그를 못 잡았다).

```python
@pytest.mark.asyncio
async def test_time_series_short_ma_matches_actual_window(self):
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
```

### 테스트 결과 (WSL `.venv-bithumb`)

수정 전 — 버그 재현, 예상대로 11봉 지연 확인:

```
FAILED tests/test_ma_cross_plugin.py::TestMaCrossTrigger::test_time_series_short_ma_matches_actual_window
AssertionError: row 0(date=20260120): short_ma=194.0, expected=183.0
assert 11.0 < 0.01
1 failed, 4 passed
```

수정 후:

```
tests/test_ma_cross_plugin.py::TestMaCrossTrigger::test_golden_cross_passes_only_at_crossing PASSED
tests/test_ma_cross_plugin.py::TestMaCrossTrigger::test_golden_cross_silent_after_holding_bullish PASSED
tests/test_ma_cross_plugin.py::TestMaCrossTrigger::test_dead_cross_silent_while_bullish_holds PASSED
tests/test_ma_cross_plugin.py::TestMaCrossTrigger::test_insufficient_series_fails_cross PASSED
tests/test_ma_cross_plugin.py::TestMaCrossTrigger::test_time_series_short_ma_matches_actual_window PASSED
5 passed
```

community 전체 스위트 (`tests/`) 재실행: **1270 passed**, MA Cross 관련 회귀 0건.
실패 28건은 전부 기존에 알려진 `openpyxl` 미설치로 인한 파일 파서(pdf/docx/xlsx) 테스트이며
이번 변경과 무관하다(회귀 아님).

## 형제 플러그인 점검 — MACD

버그 리포트가 "확인되지 않은 추측성 권고"로 남긴 `plugins/macd/__init__.py`를 직접
대조 검토했다. **동일한 버그 없음, 코드 변경 불필요.**

`ma_cross`는 `short_ma_series`와 `long_ma_series`를 독립적으로 미리 계산한 뒤
`i - offset` 형태의 수동 인덱스 산술로 두 배열을 나중에 정렬하는 구조라, 그 오프셋 산식
자체가 틀리면 버그가 생긴다(이번 케이스). 반면 MACD의 `calculate_macd_series()`는 매
시점마다 `prices[:i]` 누적 슬라이스를 통째로 다시 `calculate_macd()`에 넣어 계산하는
구조라, "독립적으로 계산한 두 시리즈를 나중에 인덱스로 짜맞추는" 단계 자체가 없다.
`bar_idx = macd_start_idx + i`가 `macd_series[i]`와 정확히 1:1 대응함을 확인했다
(성능상 O(n²) 재계산 비효율은 있으나 별개 사안이며 이번 수정 범위 밖).

## 영향 범위

- `symbol_results`(현재 시점 요약), `passed_symbols`/`result`(현재 크로스 판정)는
  애초에 이 버그의 영향을 받지 않았음 — **실거래 알림 로직에는 영향 없음**.
- `time_series`를 근거로 과거 시점을 재구성하는 소비 코드(백테스트, 차트 오버레이 등)만
  영향을 받는다. MonitoringLSStock의 AI 추천 상세 모달 이동평균선 오버레이 기능 구현
  중 발견됨.
- 이 플러그인을 실거래 워크플로우에 쓰는 세션은 발견 시점 기준 없었음(원본 버그
  리포트 참조).
