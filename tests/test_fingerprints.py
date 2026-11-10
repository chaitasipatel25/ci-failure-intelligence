
from ci_failure_intelligence.parser import FailureEvent
from ci_failure_intelligence.fingerprints import (
    fingerprint_event,
    group_failures,
)


def test_identical_failures_have_same_fingerprint():
    first = FailureEvent(
        3, "TEST_FAILURE",
        "AssertionError: expected 100, got 90"
    )

    second = FailureEvent(
        10, "TEST_FAILURE",
        "AssertionError: expected 100, got 90"
    )

    assert fingerprint_event(first) == fingerprint_event(second)


def test_different_values_have_different_fingerprints():
    first = FailureEvent(
        3, "TEST_FAILURE",
        "AssertionError: expected 100, got 90"
    )

    second = FailureEvent(
        10, "TEST_FAILURE",
        "AssertionError: expected 200, got 180"
    )

    assert fingerprint_event(first) != fingerprint_event(second)


def test_different_categories_have_different_fingerprints():
    first = FailureEvent(3, "TIMEOUT", "Connection timed out")
    second = FailureEvent(
        10, "INFRASTRUCTURE_FAILURE",
        "Connection timed out"
    )

    assert fingerprint_event(first) != fingerprint_event(second)


def test_group_failures_counts_occurrences():
    events = [
        FailureEvent(3, "TEST_FAILURE", "AssertionError: expected 100, got 90"),
        FailureEvent(5, "TEST_FAILURE", "AssertionError: expected 200, got 180"),
        FailureEvent(10, "TEST_FAILURE", "AssertionError: expected 100, got 90"),
    ]

    groups = group_failures(events)

    assert len(groups) == 2
    assert sum(group.occurrences for group in groups) == 3

    repeated = [
        group for group in groups
        if group.occurrences > 1
    ]

    assert len(repeated) == 1
    assert repeated[0].occurrences == 2
    assert repeated[0].first_seen_line == 3

def test_empty_events_return_no_groups():
    assert group_failures([]) == []

def test_stack_trace_fingerprint_ignores_absolute_paths():
    first = FailureEvent(
        8,
        "TEST_FAILURE",
        'Traceback (most recent call last):\n'
        '  File "/app/src/payment.py", line 18, in calculate_total\n'
        'AssertionError: expected 100, got 90',
    )

    second = FailureEvent(
        12,
        "TEST_FAILURE",
        'Traceback (most recent call last):\n'
        '  File "/build/agent-42/src/payment.py", line 23, in calculate_total\n'
        'AssertionError: expected 100, got 90',
    )

    assert fingerprint_event(first) == fingerprint_event(second)

def test_stack_trace_fingerprint_preserves_function_names():
    first = FailureEvent(
        8,
        "TEST_FAILURE",
        'File "/app/src/payment.py", line 18, in calculate_total\n'
        'AssertionError: expected 100, got 90',
    )

    second = FailureEvent(
        8,
        "TEST_FAILURE",
        'File "/app/src/payment.py", line 18, in calculate_discount\n'
        'AssertionError: expected 100, got 90',
    )

    assert fingerprint_event(first) != fingerprint_event(second)


def test_stack_trace_fingerprint_ignores_build_paths_and_line_numbers():
    first = FailureEvent(
        8,
        "TEST_FAILURE",
        'File "/app/src/payment.py", line 18, in calculate_total\n'
        "AssertionError: expected 100, got 90",
    )

    second = FailureEvent(
        12,
        "TEST_FAILURE",
        'File "/build/agent-42/src/payment.py", line 23, in calculate_total\n'
        "AssertionError: expected 100, got 90",
    )

    assert fingerprint_event(first) == fingerprint_event(second)


def test_stack_trace_fingerprint_preserves_function_names():
    first = FailureEvent(
        8,
        "TEST_FAILURE",
        'File "/app/src/payment.py", line 18, in calculate_total\n'
        "AssertionError: expected 100, got 90",
    )

    second = FailureEvent(
        8,
        "TEST_FAILURE",
        'File "/app/src/payment.py", line 18, in calculate_discount\n'
        "AssertionError: expected 100, got 90",
    )

    assert fingerprint_event(first) != fingerprint_event(second)
