"""ThrottleNode interval_sec 범위 테스트 — 알림 중복 억제용 24시간 상한."""

import pytest
from pydantic import ValidationError

from programgarden_core import ThrottleNode


def test_interval_sec_allows_notification_scale_values():
    """알림 억제 사용례: 1시간·24시간 간격이 허용되어야 한다"""
    assert ThrottleNode(id="t", interval_sec=3600.0).interval_sec == 3600.0
    assert ThrottleNode(id="t", interval_sec=86400.0).interval_sec == 86400.0


def test_interval_sec_default_unchanged():
    assert ThrottleNode(id="t").interval_sec == 5.0


def test_interval_sec_rejects_out_of_range():
    with pytest.raises(ValidationError):
        ThrottleNode(id="t", interval_sec=86400.1)
    with pytest.raises(ValidationError):
        ThrottleNode(id="t", interval_sec=0.05)


def test_field_schema_max_matches_model_constraint():
    schema = ThrottleNode.get_field_schema()
    assert schema["interval_sec"].max_value == 86400.0
