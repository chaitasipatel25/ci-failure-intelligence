import re
from dataclasses import dataclass


@dataclass(frozen=True)
class FailureEvent:
    line_number: int
    category: str
    message: str


# Deterministic rules for recognizing common CI failures.

FAILURE_PATTERNS = [
    (
        "TEST_FAILURE",
        re.compile(
            r"\b(AssertionError|TestFailed|"
            r"Failed:|pytest\.fail)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "DEPENDENCY_FAILURE",
        re.compile(
            r"\b(ModuleNotFoundError|ImportError)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "INFRASTRUCTURE_FAILURE",
        re.compile(
            r"\b(ConnectionError|ConnectionRefusedError|"
            r"OperationalError)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "TIMEOUT",
        re.compile(
            r"\b(TimeoutError|timed out|"
            r"deadline exceeded)\b",
            re.IGNORECASE,
        ),
    ),
]


def parse_log(log_content: str) -> list[FailureEvent]:
    """
    Extract recognizable failure events from a CI log.

    Returns one event for each matching log line.
    """
    failures = []

    for line_number, line in enumerate(
        log_content.splitlines(), start=1
    ):
        stripped_line = line.strip()

        if not stripped_line:
            continue

        for category, pattern in FAILURE_PATTERNS:
            if pattern.search(stripped_line):
                failures.append(
                    FailureEvent(
                        line_number=line_number,
                        category=category,
                        message=stripped_line,
                    )
                )
                break

    return failures