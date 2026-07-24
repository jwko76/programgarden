# [Bug] MovingAverageCross(`ma_cross`) `time_series`의 `short_ma`가 실제 값보다 지연됨

> ✅ **해결됨 (2026-07-24)** — `plugins/ma_cross/__init__.py` 147행 `short_idx` 계산을
> `i - (short_period - 1)`로 수정, 플러그인 v3.1.1 / community v1.17.1로 릴리스.
> 형제 플러그인 MACD도 함께 점검했으나 구조적으로 이 버그가 발생할 수 없어 변경 없음.
> 회귀 테스트 1건 추가(`test_time_series_short_ma_matches_actual_window`). 상세 내용은
> [ma_cross_time_series_short_ma_lag_fix.md](./ma_cross_time_series_short_ma_lag_fix.md) 참조.
> 아래 원본 분석 내용은 이력으로 보존한다.

- **파일**: `src/community/programgarden_community/plugins/ma_cross/__init__.py`
- **함수**: `ma_cross_condition()`, 147행 부근 (`short_idx = i - (long_period - short_period)`)
- **버전**: 3.1.0 (현재 최신, `MA_CROSS_SCHEMA.version`)
- **발견 경위**: MonitoringLSStock(소비 서비스)에서 AI 추천 상세 모달에 전략 근거
  지표(이동평균선)를 오버레이하는 기능을 구현하던 중, 테스트용 골든크로스
  데이터를 아무리 만들어도 크로스가 감지되지 않거나 방향이 뒤바뀌는 현상을
  발견 → 원인 추적 결과 이 플러그인 자체의 버그로 확인됨.
- **실거래 영향**: MonitoringLSStock 쪽에서 실측한 결과, 현재 이 플러그인을
  실거래 워크플로우에 쓰는 세션은 없어 즉각적인 실거래 피해는 없었음. 다만
  `time_series`를 백테스트·차트 표시에 쓰는 소비 코드가 있다면 영향 받음.

## 요약

`ma_cross_condition()`이 반환하는 `values[].time_series[]`의 각 행에는
`short_ma`(그 날짜 시점의 단기 이동평균)가 들어있어야 하는데, 실제로는
**`(long_period - short_period)`봉만큼 과거의 stale한 값**이 들어간다.
`long_ma`는 정상이다. 이 때문에 `time_series`를 근거로 골든/데드크로스를
재구성하면(백테스트, 차트 오버레이 등) 크로스가 감지되지 않거나, 심할 경우
**가격이 상승 중인데 데드크로스(매도) 신호가 나오는 등 방향이 뒤집힌** 결과가
나온다.

`symbol_results`(현재 시점 요약값, `short_ma_series[-1]` 등 음수 인덱스로
계산)는 이 버그의 영향을 받지 않아 정상이다. `passed_symbols`/`result`(현재
크로스 여부 판정)도 `symbol_results`의 값을 쓰므로 정상이다. **오직
`time_series`의 과거 각 행 재구성만 잘못됐다.**

## 원인

```python
# 147행 부근, ma_cross_condition() 내부
ma_start_idx = long_period - 1
for i in range(ma_start_idx, len(symbol_data)):
    row = symbol_data[i]
    short_idx = i - (long_period - short_period)          # ← 버그
    short_ma = short_ma_series[short_idx] if 0 <= short_idx < len(short_ma_series) else 0
    long_ma = long_ma_series[i - ma_start_idx] if i - ma_start_idx < len(long_ma_series) else 0
```

`calculate_sma_series(prices, period)`는 `prices` 인덱스 `period-1`부터
시작하는 배열을 반환한다. 즉 `series[k]`는 원본 `prices`의 인덱스
`(period - 1 + k)`에 대응한다.

- **`long_ma`는 맞다**: `long_ma_series[i - ma_start_idx]`
  = `long_ma_series[i - (long_period-1)]`
  → 원본 인덱스 `(long_period-1) + (i-(long_period-1)) = i` ✅ (현재 행 i와 일치)

- **`short_ma`가 틀렸다**: `short_ma_series[i - (long_period-short_period)]`
  → 원본 인덱스 `(short_period-1) + i - (long_period-short_period)
    = i - long_period + 2·short_period - 1`
  → 현재 행 `i`와의 차이 = `long_period - 2·short_period + 1`

즉 `short_ma`가 항상 **`(long_period - 2·short_period + 1)`봉만큼 과거** 값을
가리킨다. 기본값(`short_period=5, long_period=20`)이면 **11봉 지연**이다.

**올바른 식**은 `long_ma`와 동일한 패턴이어야 한다:

```python
short_idx = i - (short_period - 1)   # long_ma와 동일한 정렬 방식
```

`prev_short = short_ma_series[short_idx - 1]`(158행 근처)도 `short_idx`
계산이 고쳐지면 자동으로 함께 정상화된다.

## 재현 (최소 예제)

```python
import asyncio
from programgarden_community.plugins.ma_cross import ma_cross_condition

def make_rows(n=40, symbol="TEST", exchange="TEST"):
    rows = []
    for i in range(n):
        close = 50000.0 if i < 25 else 50000.0 + (i - 24) * 300.0
        rows.append({"date": f"2026-{1+i//28:02d}-{1+i%28:02d}",
                      "symbol": symbol, "exchange": exchange, "close": close})
    return rows

async def main():
    result = await ma_cross_condition(
        data=make_rows(40),
        fields={"short_period": 5, "long_period": 20, "cross_type": "golden"},
    )
    ts = result["values"][0]["time_series"]
    for row in ts:
        print(row["date"], row["close"], "short_ma=", row["short_ma"],
              "long_ma=", row["long_ma"], "signal=", row["signal"])

asyncio.run(main())
```

가격은 24번째 봉까지 50000.0으로 평평하다가, 25번째 봉부터 하루 +300씩
꾸준히 상승한다(횡보 → 완만한 상승 전환 — 실제 시장에서도 흔한 패턴).

### 실측 vs 기대값 (일부 발췌, `short_period=5, long_period=20`)

| i (0-idx) | close | `short_ma` (실제 출력, 버그) | `short_ma` (정답) | `long_ma` |
|---|---|---|---|---|
| 19 | 50000.0 | 50000.0 | 50000.0 | 50000.0 |
| 24 | 50000.0 | 50000.0 | 50000.0 | 50000.0 |
| 25 | 50300.0 | **50000.0** | **50060.0** | 50015.0 |
| 26 | 50600.0 | **50000.0** | **50180.0** | 50045.0 |
| 27 | 50900.0 | **50000.0** | **50360.0** | 50090.0 |
| 28 | 51200.0 | **50000.0** | **50600.0** | 50150.0 |
| 29 | 51500.0 | **50000.0** | **50900.0** | 50225.0 |
| 36 | 53600.0 | 50060.0 (11봉 전 값, i=25 시점 정답과 일치) | 50060.0 | 51170.0 |

i=25에서 `signal="sell"`(데드크로스)이 찍힌다 — **가격이 막 상승세로
전환하는 시점에 매도 신호가 나오는 것**으로, 이 버그가 단순 표시 오류를
넘어 신호 판정 자체를 오염시키는 것을 보여준다(정답 MA5=50060 > MA20=50015
이므로 원래는 상승 유지, 크로스 없음이어야 함).

`i=25`일 때 버그 코드가 읽는 인덱스는 `25 - (20-5) = 10`이 아니라
`short_ma_series` 배열 기준 인덱스 `10`이며, 이는 원본 `prices` 인덱스
`(5-1)+10 = 14`에 해당(여전히 평평한 구간) — 위 유도식의
`i - long_period + 2*short_period - 1 = 25-20+10-1 = 14`와 일치.

## 왜 기존 테스트가 못 잡았나

`src/community/tests/test_ma_cross_plugin.py`(v3.1.0 크로스 트리거 버그
수정 시 추가된 테스트)는 전부 `result["symbol_results"][0]`의 값
(`short_ma`/`long_ma`/`prev_short_ma`/`prev_long_ma`)만 검증한다. 이 값들은
`short_ma_series[-1]`/`short_ma_series[-2]`처럼 **끝에서부터 음수 인덱스**로
계산되어 이번 버그의 영향을 받지 않는다. `time_series`의 각 행(과거 시점
재구성)을 검증하는 테스트가 하나도 없어서, `time_series`에만 있는 이
인덱스 버그가 릴리스를 통과했다.

CHANGELOG.md의 `[1.15.0]` 항목은 "`time_series`의 signal 마킹은 돌파
기준으로 올바르게 구현돼 있었다"고 기술하는데, 이는 **비교 로직(전 봉 vs
현재 봉)** 자체는 맞다는 뜻이고, 이번에 발견된 건 그 비교에 들어가는
**입력값(short_ma) 자체가 잘못 정렬**되어 있다는, 별개의 버그다.

## 제안하는 수정

```python
short_idx = i - (short_period - 1)
```

수정 후 위 재현 스크립트를 다시 돌려 `short_ma`가 매 행마다 그 시점의
실제 5봉 평균과 일치하는지, i=25에서 signal이 `None`(또는 실제 상승
지속이므로 크로스 없음)으로 나오는지 확인 권장.

## 제안하는 회귀 테스트

`test_ma_cross_plugin.py`에 `time_series`의 **과거 임의 시점** 값을
직접 검증하는 테스트 추가 권장(현재는 최종 시점만 간접 검증됨):

```python
def test_time_series_short_ma_matches_actual_window():
    """time_series의 각 행 short_ma가 그 시점 기준 실제 5봉 평균과 일치해야 함
    (회귀 방지 — short_idx 인덱스 정렬 버그, 2026-07-24 발견)."""
    result = asyncio.run(ma_cross_condition(
        data=make_rows(PRICES),
        fields={"short_period": SHORT, "long_period": LONG, "cross_type": "golden"},
    ))
    ts = result["values"][0]["time_series"]
    for row_idx, row in enumerate(ts):
        original_idx = (LONG - 1) + row_idx  # time_series는 ma_start_idx부터 시작
        expected = sum(PRICES[original_idx - SHORT + 1: original_idx + 1]) / SHORT
        assert abs(row["short_ma"] - expected) < 0.01, \
            f"row {row_idx}(date={row['date']}): short_ma={row['short_ma']}, expected={expected}"
```

## 참고 — 형제 플러그인 점검 권장

같은 `[1.15.0]` 릴리스에서 함께 수정됐다고 기록된 `macd` 플러그인
(`plugins/macd/__init__.py`)도 여러 이동평균 시리즈를 조합해 `time_series`를
만드는 구조라면 비슷한 인덱스 정렬 실수가 있을 수 있어 한 번 점검해볼
가치가 있음(이번 조사에서 macd 코드 자체는 확인하지 않았음 — 추측성 권고).
