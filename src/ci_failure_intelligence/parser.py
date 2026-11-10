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
    Extract recognizable failures from a CI log.

    Retains traceback context and creates one event
    for each recognized failure.
    """
    failures = []
    traceback_lines = []

    for line_number, line in enumerate(
        log_content.splitlines(), start=1
    ):
        stripped_line = line.strip()

        if not stripped_line:
            continue

        if stripped_line.startswith(
            "Traceback (most recent call last):"
        ):
            traceback_lines = [stripped_line]
            continue

        matched_category = None

        for category, pattern in FAILURE_PATTERNS:
            if pattern.search(stripped_line):
                matched_category = category
                break

        if traceback_lines:
            traceback_lines.append(stripped_line)

            if matched_category:
                failures.append(
                    FailureEvent(
                        line_number=line_number,
                        category=matched_category,
                        message="\n".join(traceback_lines),
                    )
                )
                traceback_lines = []

            continue

        if matched_category:
            failures.append(
                FailureEvent(
                    line_number=line_number,
                    category=matched_category,
                    message=stripped_line,
                )
            )

    return failures
