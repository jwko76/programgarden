# [Bug/Fix] 워크플로우 정상 완료 시 ResourceContext/RiskTracker 리소스 누수

> ✅ **해결됨 (2026-07-24)** — `src/programgarden/programgarden/executor.py`의
> `WorkflowJob._run()` `finally` 블록에 리소스 정리 호출 추가. 패키지 `programgarden`
> v1.29.0 → v1.29.1. 회귀 테스트 2건 추가(`test_resource_cleanup_on_completion.py`).

- **파일**: `src/programgarden/programgarden/executor.py`
- **함수**: `WorkflowJob._run()` (finally 블록), `stop()`/`cancel()`/`force_stop()`
- **버전**: 발견 시점 1.29.0(현재 최신), 수정 후 1.29.1
- **발견 경위**: MonitoringLSStock OCI 운영 서버(`stock-monitor` 컨테이너, 메모리 캡 2GiB)를
  재배포한 지 15분 만에 `docker stats` 기준 메모리 86%→94%, CPU 98%→152%로 계속 증가하는
  것을 라이브로 관측 → 코드 추적으로 programgarden 엔진 자체의 리소스 정리 누락 버그로 확인.

## 요약

`WorkflowJob._run()`이 워크플로우를 실행할 때마다(`executor.execute()` → `run_workflow()`
경로) `ResourceContext`(CPU/메모리 사용률 기반 스로틀링용, `AdaptiveThrottle` + `ResourceMonitor`
각각 백그라운드 asyncio 태스크 보유)를 새로 만들어 시작한다. 이 리소스는 `stop()`을 호출해야만
멈추는데, **워크플로우가 스스로 끝까지 실행되어 "completed"/"failed"/"cancelled" 상태로
자연 종료되는 정상 경로(`_run()`의 `finally` 블록)에는 그 호출이 빠져 있었다.** 정리는 오직
외부에서 명시적으로 부르는 `stop()`/`cancel()`/`force_stop()`에만 있었다.

HWM(고점 대비 낙폭) 추적을 쓰는 워크플로우의 `WorkflowRiskTracker` flush loop도 동일한
누락 패턴을 갖고 있어 같이 수정했다.

## 원인

`ResourceContext.stop()`(`resource/context.py:140-148`)과
`WorkflowRiskTracker.stop_flush_loop()`(`database/workflow_risk_tracker.py:995-1011`)는
각각 `AdaptiveThrottle`(2초 주기 `while self._running: await asyncio.sleep(2); ...`,
`throttle.py:174,191-198`)과 `ResourceMonitor`(1초 주기 동일 패턴, `monitor.py:93`),
`_flush_loop`(`while True: await asyncio.sleep(FLUSH_INTERVAL); ...`,
`workflow_risk_tracker.py:922-925`) 백그라운드 asyncio 태스크를 취소하는 유일한 경로다.

`_run()`의 `finally` 블록(수정 전, executor.py 약 17171-17179행)은 브로커 fill 구독,
MarketStatusNode JIF 구독, persistent 노드, 리스너만 정리했고 `context.resource`/
`context.risk_tracker` 정리가 없었다. 반면 `stop()`(18787-18793)/`cancel()`(18826-18831)/
`force_stop()`(18884-18901)에는 각각 인라인으로 중복 구현돼 있었다 — "정상 완료 경로"와
"외부 중단 경로"가 서로 다른 정리 로직을 갖게 된 것이 근본 원인.

`while self._running`/`while True` 루프는 `asyncio.create_task()`로 이벤트 루프에
스케줄되므로, 아무도 취소하지 않으면 **영원히 실행되는 태스크**가 된다. 이벤트 루프가
이 태스크를 계속 참조하기 때문에 GC도 되지 않는다.

MonitoringLSStock 등 소비 서비스는 `job = await pg.run_async(...)` 후 `job.status`가
"completed"가 될 때까지 폴링만 하고(타임아웃이 나도 마찬가지) **`job.stop()`/`cancel()`을
호출하지 않는 패턴**이 흔했다 — 이 패턴에서 워크플로우를 실행할 때마다(배치 스캔이면
반복 사이클마다) orphan 태스크가 계속 쌓인다.

## 왜 기존 테스트가 못 잡았나

`test_listener_cleanup.py`는 워크플로우가 자연 완료된 뒤에도 **항상 `job.stop()`을 명시
호출**해서 정리를 검증하는 패턴이다. 이 패턴에서는 `stop()`이 리소스를 정리하므로 테스트가
항상 통과했고, "아무도 stop()을 안 부르는" 실제 프로덕션 시나리오는 커버되지 않았다.

## 수정

`stop()`/`cancel()`/`force_stop()`에 중복돼 있던 정리 로직을 공용 private 헬퍼로 추출하고,
`_run()`의 `finally`에도 동일하게 적용했다.

```python
async def _cleanup_resource_context(self) -> None:
    """ResourceContext(AdaptiveThrottle + ResourceMonitor 백그라운드 태스크) 정지."""
    if self.context.resource:
        try:
            await self.context.resource.stop()
            logger.debug(f"ResourceContext stopped for job {self.job_id}")
        except Exception as e:
            logger.warning(f"Failed to stop ResourceContext: {e}")

async def _cleanup_risk_tracker(self) -> None:
    """RiskTracker flush loop 정지 (최종 flush는 stop_flush_loop() 내부에서 처리)."""
    if self.context.risk_tracker:
        try:
            await self.context.risk_tracker.stop_flush_loop()
        except Exception as e:
            logger.warning(f"Failed to stop risk tracker: {e}")
```

`_run()`의 `finally`:

```python
finally:
    await self._cleanup_broker_fill_subscriptions()
    await self._cleanup_jif_subscriptions()
    await self.context.cleanup_persistent_nodes()
    await self._cleanup_risk_tracker()      # 신규
    await self._cleanup_resource_context()  # 신규
    await self.context.cleanup_listeners()
```

`stop()`/`cancel()`/`force_stop()`의 기존 인라인 블록은 위 두 헬퍼 호출로 교체했다(순수
리팩터링, 동작 동일). `ResourceContext.stop()`과 `WorkflowRiskTracker.stop_flush_loop()`는
이미 멱등(`if not self._started: return` / `_flush_task is not None` 체크)이라, `_run()`이
먼저 정리하고 이후 호출자가 `stop()`을 또 불러도(기존 테스트 패턴) 안전하다.

## 회귀 테스트

`src/programgarden/tests/test_resource_cleanup_on_completion.py` 신규 — `job.stop()`/
`cancel()`을 **전혀 호출하지 않고** 자연 완료만 기다린 뒤 백그라운드 태스크가 정리됐는지
직접 검증(실제 프로덕션 시나리오 재현):

```python
async def test_resource_context_stopped_without_explicit_stop(executor):
    job = await executor.execute(SIMPLE_WORKFLOW, job_id="test-resource-leak")
    await asyncio.wait_for(job._task, timeout=5.0)   # stop()/cancel() 호출 없음

    assert job.context.resource.is_started is False
    assert job.context.resource.throttle._task is None or job.context.resource.throttle._task.done()
    assert job.context.resource.monitor._task is None or job.context.resource.monitor._task.done()
```

RiskTracker용 테스트는 `WorkflowRiskTracker(features={"hwm"}, ...)`를 job에 직접 연결해
`start_flush_loop()`을 호출한 뒤 동일하게 검증.

### 테스트 결과 (WSL `.venv-bithumb`)

수정 전 — 버그 재현:
```
FAILED test_resource_context_stopped_without_explicit_stop
  assert True is False  (resource.is_started가 여전히 True)
FAILED test_risk_tracker_flush_loop_stopped_without_explicit_stop
  assert (<Task pending ...> is None or False)  (_flush_task가 여전히 pending)
```

수정 후: 신규 2건 + `test_listener_cleanup.py` 7건 전부 통과(9 passed).
programgarden 전체 스위트: 25 failed → 23 failed로 감소(신규 2건 통과분), 나머지 실패는
`litellm`/`aiosqlite` 모듈 미설치, `examples/hkex_futures_bot/workflow.json` 누락 등
기존 환경 문제로 이번 수정과 무관함을 직접 확인(회귀 아님).

## 영향 범위

- 모든 워크플로우 실행에 영향(범용) — `ResourceContext`는 모든 `run_workflow()` 호출마다
  생성됨. `WorkflowRiskTracker`는 HWM/트레일링스탑 등 위험관리 기능을 쓰는 워크플로우에만
  해당(더 좁은 범위).
- 반복 실행(스케줄 배치, 폴링 기반 백테스트/추천 서비스)일수록 누적 속도가 빠름 —
  MonitoringLSStock의 `strategy_recommend_service`(1시간마다 종목×전략 스펙 조합 실행)가
  실제 프로덕션에서 이 버그를 촉발한 사례.
- 리소스 사용량 증가는 psutil 폴링 오버헤드(스로틀 2초/모니터 1초 주기)와 각 인스턴스가
  보유한 사용량 히스토리 버퍼 누적에서 온다 — 방치 시 컨테이너 메모리 캡에 도달해 OOM-kill
  위험.
