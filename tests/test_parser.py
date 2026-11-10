from pathlib import Path

from ci_failure_intelligence.parser import parse_log


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "sample_ci.log"
)


def test_parser_detects_expected_failures():
    log_content = FIXTURE_PATH.read_text()

    failures = parse_log(log_content)

    assert len(failures) == 3

    categories = [failure.category for failure in failures]

    assert categories == [
        "TEST_FAILURE",
        "DEPENDENCY_FAILURE",
        "INFRASTRUCTURE_FAILURE",
    ]


def test_parser_preserves_original_error_message():
    log_content = FIXTURE_PATH.read_text()

    failures = parse_log(log_content)

    assert "AssertionError" in failures[0].message
    assert "expected 100, got 90" in failures[0].message


def test_parser_records_correct_line_numbers():
    log_content = FIXTURE_PATH.read_text()

    failures = parse_log(log_content)

    assert failures[0].line_number == 3
    assert failures[1].line_number == 6
    assert failures[2].line_number == 9


def test_parser_handles_empty_logs():
    assert parse_log("") == []


def test_parser_ignores_unrecognized_lines():
    log_content = """
    Starting build...
    Downloading dependencies...
    Build completed successfully.
    """

    assert parse_log(log_content) == []

def test_database_timeout_is_infrastructure_failure():
    log = "psycopg.OperationalError: connection timed out"

    failures = parse_log(log)

    assert len(failures) == 1
    assert failures[0].category == "INFRASTRUCTURE_FAILURE"


def test_generic_timeout_is_timeout():
    log = "Request timed out after 30 seconds"

    failures = parse_log(log)

    assert len(failures) == 1
    assert failures[0].category == "TIMEOUT"


def test_parser_preserves_stack_trace_context():
    log = (
        "Starting test execution\n"
        "Traceback (most recent call last):\n"
        '  File "/app/tests/test_payment.py", line 42, in test_total\n'
        "    assert calculate_total(90) == 100\n"
        '  File "/app/src/payment.py", line 18, in calculate_total\n'
        "    return amount\n"
        "AssertionError: expected 100, got 90\n"
        "Build failed.\n"
    )

    failures = parse_log(log)

    assert len(failures) == 1

    failure = failures[0]

    assert failure.category == "TEST_FAILURE"
    assert failure.line_number == 7
    assert "test_payment.py" in failure.message
    assert "payment.py" in failure.message
    assert "AssertionError" in failure.message
