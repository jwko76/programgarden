# 시그널 알림 중복 방지 적용 가이드 (monitorlsstock 등 소비 프로젝트용)

> 대상: 이 프레임워크로 조건 감시 + 텔레그램 알림을 운용하는 프로젝트
> (예: monitorlsstock). "같은 시그널 알림이 계속 온다" 문제의 해결 절차.
> 작성: 2026-07-12, 갱신: 2026-07-13, feature/signal-cross-trigger

---

## 1. 문제 원인

조건 플러그인의 `below`/`above`(과매도/과매수)는 **레벨 트리거**다.
조건이 **유지되는 동안 매 평가마다** 시그널이 발생한다.

```
RSI가 30 아래에 3시간 머묾 × 5분 주기 ScheduleNode 폴링
= 동일 알림 36건
```

기존에는 ThrottleNode로 억제하려 해도 `interval_sec` 상한이 300초(5분)여서
사실상 막을 수 없었다.

## 2. 요구 버전

| 패키지 | 최소 버전 | 변경 내용 |
|--------|----------|----------|
| programgarden-community | **1.15.0** | RSI v3.1.0 + 오실레이터 7종(§7) 크로스 트리거, MACD/MA Cross 크로스 버그 수정 |
| programgarden-core | **1.17.0** | ThrottleNode v1.1.0 — `interval_sec` 상한 300 → 86,400초 |

업데이트 (editable 설치 기준):

```bash
cd <framework-repo> && git pull
pip install -U -e src/core -e src/community
# programgarden 엔진도 쓰는 경우: -e src/programgarden
```

## 3. 적용법 — 워크플로우 JSON 한 줄 변경

알림용 ConditionNode의 `direction`을 크로스 모드로 바꾼다.

**변경 전** (과매도 유지 중 매 폴링마다 알림):

```json
{
  "id": "rsi", "type": "ConditionNode", "plugin": "RSI",
  "items": { "from": "{{ nodes.candles.time_series }}", "extract": { "...": "..." } },
  "fields": { "period": 14, "threshold": 30, "direction": "below" }
}
```

**변경 후** (임계값 하향 돌파 순간 1회만):

```json
  "fields": { "period": 14, "threshold": 30, "direction": "cross_below" }
```

- `cross_below`: 직전 캔들 RSI ≥ threshold **이고** 현재 캔들 < threshold
- `cross_above`: 직전 캔들 RSI ≤ threshold **이고** 현재 캔들 > threshold
- 매매 로직(조건 유지 중 계속 실행이 필요한 경우)은 기존 `below`/`above` 유지

## 4. ⚠️ 중요: 캔들 주기 vs 폴링 주기

크로스 트리거는 **캔들 단위**로 중복을 제거한다 (직전 캔들과 현재 캔들 비교).
플러그인은 평가 간 상태를 저장하지 않으므로, **캔들 1개가 갱신되는 동안
여러 번 폴링하면 그 안에서는 여전히 반복**될 수 있다:

```
일봉 + 5분 폴링: 오늘 캔들이 돌파 상태로 유지되는 동안
매 폴링이 같은 "어제≥30 → 오늘<30" 비교를 반복 → 당일 내 중복 발생
```

해결 2가지 (하나만 적용해도 됨):

**(a) 폴링 주기 ≥ 캔들 주기로 맞추기** — 가장 깔끔함
```
5분봉 감시 → ScheduleNode cron "*/5 * * * *"   (봉당 1회 평가)
일봉 감시  → ScheduleNode cron "10 16 * * 1-5" (장 마감 후 1회)
```

**(b) ThrottleNode를 캔들 주기만큼 걸기** — 폴링을 못 줄일 때
```json
{ "id": "throttle", "type": "ThrottleNode", "mode": "skip", "interval_sec": 86400 }
```
연결: `rsi → throttle → telegram`. 이제 상한이 24시간이라 일봉 주기도 커버된다.

## 5. 패턴 요약

| 용도 | 권장 구성 |
|------|----------|
| 시그널 알림 (돌파 순간 통지) | `direction: cross_below/cross_above` + 필요시 ThrottleNode(캔들 주기) |
| 정기 리포트 (예: 1시간마다 시세) | 레벨 무관, `ThrottleNode(interval_sec=3600)` 또는 ScheduleNode cron |
| 매매 로직 (조건 유지 중 계속 판단) | 기존 `below`/`above` 유지 + 주문 노드 앞 ThrottleNode(짧게) |

주의: 긴 ThrottleNode는 쿨다운 동안 **새로운 이벤트도 함께 차단**한다.
알림의 1차 수단은 크로스 트리거, Throttle은 보조 수단으로만.

## 6. 적용 후 검증

```python
from programgarden import ProgramGarden
pg = ProgramGarden()

r = pg.validate(workflow)                     # 정적 검증 (direction 오타 등)
assert r.is_valid, [str(e) for e in r.errors]

job = pg.run(workflow, context={"dry_run": True}, wait=True, timeout=60)
# dry_run: 주문/알림 실호출 없이 시뮬레이션 — 시그널 발생 경로 확인
```

운영 확인 체크리스트:
- [ ] 과매도 진입 시 알림 1건 수신
- [ ] 과매도 유지 중(다음 캔들) 추가 알림 없음
- [ ] 회복(≥30) 후 재돌파 시 알림 다시 수신
- [ ] 매매용 ConditionNode는 레벨 트리거 그대로인지 확인

## 7. 다른 지표 크로스 모드 현황 (2026-07-19 기준)

**레벨형 지표 — 크로스 모드 지원 (v1.15.0)**

| 플러그인 | 크로스 enum 값 |
|---------|----------------|
| RSI | `cross_below` / `cross_above` |
| WilliamsR | `cross_oversold` / `cross_overbought` |
| CCI | `cross_oversold` / `cross_overbought` |
| MFI | `cross_below` / `cross_above` |
| ConnorsRSI | `cross_below` / `cross_above` |
| UltimateOscillator | `cross_below` / `cross_above` |
| ZScore | `cross_below` / `cross_above` |
| MeanReversion | `cross_oversold` / `cross_overbought` |

**밴드/레벨 터치형 지표 — 크로스 모드 지원 (v1.16.0, Phase 2)**

| 플러그인 | 크로스 enum 값 |
|---------|----------------|
| BollingerBands | `cross_below_lower` / `cross_above_upper` |
| VWAP | `cross_above` / `cross_below` |
| CMF | `cross_accumulation` / `cross_distribution` |
| RelativeStrength | `cross_above` / `cross_below` |

밴드형은 "가격 vs 밴드값" 비교라 직전 캔들의 밴드·가격이 모두 필요. RelativeStrength는
population 전체(벤치마크 포함) 랭킹을 한 봉 이전 시점으로 재계산해 비교(`_rank_relative_strength`
헬퍼) — 데이터가 `lookback+1`개뿐이면(직전 시점엔 lookback을 못 채움) prev 점수가 없어
크로스는 통과하지 않는다.

**모니터링 지표 — 크로스 모드 지원 (v1.17.0, Phase 3 — 선택 항목)**

| 플러그인 | 크로스 enum 값 |
|---------|----------------|
| SharpeRatioMonitor | `cross_above` / `cross_below` |
| SortinoRatio | `cross_above` / `cross_below` |
| CalmarRatio | `cross_above` / `cross_below` |
| CorrelationAnalysis | `cross_above` / `cross_below` |

이 4종은 매매 신호가 아니라 전략/포트폴리오 상태 모니터링용이라 실제 알림 중복 사례는
없었지만, Phase 0~2와 동일 패턴으로 예방적 확장. 각 지표는 롤링 lookback window
기준 단일 값만 계산하는 구조라 "직전 값"이 따로 없어서, `prices[:-1]`로 한 봉 앞선
window를 다시 계산하거나(sharpe/sortino/calmar), population을 한 봉 이전 시점으로
재계산하는 `_compute_symbol_max_corr(trim=1)`(correlation_analysis)로 비교한다.
CalmarRatio의 `inf` 값(연속 상승으로 낙폭이 0에 수렴할 때 발생)은 크로스 판정에서도
유한값이 아니므로 제외.

**이미 크로스 이벤트형이라 그대로 쓰면 되는 지표** — Stochastic(`oversold`/`overbought`는
%K/%D 교차 기준이라 이미 엣지 트리거), MACD(`bullish_cross`/`bearish_cross`, v3.1.0에서
버그 수정 — 과거엔 레벨 체크였음), MovingAverageCross(`golden`/`dead`, 마찬가지로
v3.1.0에서 버그 수정), Aroon(`cross_up`/`cross_down`), CoppockCurve(`zero_cross`),
TRIX(`bullish_cross`/`bearish_cross`), VortexIndicator(`bullish_cross`/`bearish_cross`),
ParabolicSAR(`bullish_reversal`/`bearish_reversal`), SqueezeMomentum(`squeeze_fire_long`/
`squeeze_fire_short`).

> ⚠️ MACD `bullish_cross`/`bearish_cross`와 MovingAverageCross `golden`/`dead`를
> v1.14.0 이하에서 이미 쓰고 있었다면, v1.15.0으로 올리면 **알림 빈도가 줄어든다**
> (버그 수정으로 돌파 순간에만 통과하도록 바뀜 — 의도된 동작에 가까워진 것).

> ⚠️ MovingAverageCross v1.17.1(플러그인 v3.1.1)에서 별개의 버그가 하나 더 수정됐다 —
> 위 v1.15.0 수정은 **실제 알림 판정**(`passed_symbols`/`result`)에 관한 것이었고, 이번
> 것은 `values[].time_series[]`(차트 오버레이·백테스트용 과거 시계열 재구성)에만 있던
> 인덱스 정렬 버그다. 알림 판정 로직 자체는 v1.15.0 이후 항상 정상이었으므로 실거래
> 알림에는 영향이 없었지만, `time_series`의 `short_ma`를 근거로 크로스를 재구성하는
> 소비 코드(차트 표시, 백테스트)가 있었다면 v1.17.1로 올려야 한다.
> `docs/bug_reports/ma_cross_time_series_short_ma_lag.md` 참조.
