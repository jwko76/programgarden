"""
리소스 정리 테스트 (정상 완료 경로)

`test_listener_cleanup.py`는 워크플로우가 자연 완료된 뒤에도 항상 `job.stop()`을
명시적으로 호출해서 정리를 검증한다. 하지만 실제 프로덕션 호출자(MonitoringLSStock의
workflow_engine_service 등)는 `job.status`가 "completed"가 될 때까지 폴링만 하고
`stop()`/`cancel()`을 절대 호출하지 않는 경우가 흔하다.

`ResourceContext`(AdaptiveThrottle + ResourceMonitor 백그라운드 asyncio 태스크)와
`WorkflowRiskTracker`의 flush loop는 과거 `stop()`/`cancel()`/`force_stop()`에서만
정리됐고, `WorkflowJob._run()`의 정상 완료 `finally` 블록에는 그 호출이 빠져 있었다
(2026-07-24 OCI 운영 서버에서 메모리/CPU가 계속 증가하는 리소스 누수로 발견).

이 파일은 `stop()`/`cancel()`을 전혀 호출하지 않고 자연 완료만 기다린 뒤에도
백그라운드 태스크가 정리되는지 검증한다.
"""

import asyncio

import pytest

from programgarden.executor import WorkflowExecutor
from programgarden.database.workflow_risk_tracker import WorkflowRiskTracker


SIMPLE_WORKFLOW = {
    "id": "test-workflow",
    "name": "테스트 워크플로우",
    "nodes": [
        {"id": "start", "type": "StartNode"},
    ],
    "edges": [],
}


@pytest.fixture
def executor():
    return WorkflowExecutor()


@pytest.mark.asyncio
async def test_resource_context_stopped_without_explicit_stop(executor):
    """job.stop()/cancel()을 호출하지 않아도 ResourceContext가 정리돼야 한다."""
    job = await executor.execute(SIMPLE_WORKFLOW, job_id="test-resource-leak")
    await asyncio.wait_for(job._task, timeout=5.0)

    assert job.context.resource is not None
    assert job.context.resource.is_started is False
    assert job.context.resource.throttle._task is None or job.context.resource.throttle._task.done()
    assert job.context.resource.monitor._task is None or job.context.resource.monitor._task.done()


@pytest.mark.asyncio
async def test_risk_tracker_flush_loop_stopped_without_explicit_stop(executor, tmp_path):
    """job.stop()/cancel()을 호출하지 않아도 RiskTracker flush loop가 정리돼야 한다."""
    job = await executor.execute(SIMPLE_WORKFLOW, job_id="test-risk-leak")
    tracker = WorkflowRiskTracker(
        db_path=str(tmp_path / "risk.db"),
        job_id="test-risk-leak",
        product="overseas_stock",
        provider="ls",
        trading_mode="live",
        features={"hwm"},
    )
    job.context._workflow_risk_tracker = tracker
    tracker.start_flush_loop()

    await asyncio.wait_for(job._task, timeout=5.0)

    assert tracker._flush_task is None or tracker._flush_task.done()
