
import json

from ci_failure_intelligence.fingerprints import FailureGroup
from ci_failure_intelligence.reports import (
    build_report,
    render_json,
    render_markdown,
    render_text,
)


def sample_groups():
    return [
        FailureGroup(
            fingerprint="abc123",
            category="TEST_FAILURE",
            occurrences=2,
            first_seen_line=5,
            examples=("AssertionError: expected 100, got 90",),
        )
    ]


def test_json_report_contains_group_information():
    report = json.loads(render_json(sample_groups()))

    assert report["total_failure_events"] == 2
    assert report["unique_failure_groups"] == 1
    assert report["failures"][0]["occurrences"] == 2


def test_markdown_report_contains_summary():
    output = render_markdown(sample_groups())

    assert "# CI Failure Intelligence" in output
    assert "TEST_FAILURE" in output
    assert "abc123" in output


def test_text_report_contains_summary():
    output = render_text(sample_groups())

    assert "Total failure events: 2" in output
    assert "Occurrences: 2" in output


def test_empty_report_is_supported():
    report = build_report([])

    assert report["total_failure_events"] == 0
    assert report["unique_failure_groups"] == 0
    assert report["failures"] == []
