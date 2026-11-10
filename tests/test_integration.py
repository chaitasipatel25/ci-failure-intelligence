
from pathlib import Path

from ci_failure_intelligence.parser import parse_log
from ci_failure_intelligence.fingerprints import group_failures


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "repeated_failures.log"
)


def test_repeated_ci_failures_are_grouped():
    log_content = FIXTURE_PATH.read_text()

    events = parse_log(log_content)
    groups = group_failures(events)

    assert len(events) == 3
    assert len(groups) == 2

    repeated_group = next(
        group for group in groups
        if group.occurrences == 2
    )

    assert repeated_group.category == "TEST_FAILURE"
    assert repeated_group.first_seen_line == 3
    assert len(repeated_group.examples) == 1
