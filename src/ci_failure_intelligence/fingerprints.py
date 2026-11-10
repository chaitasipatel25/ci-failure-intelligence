
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import PurePosixPath

from ci_failure_intelligence.parser import FailureEvent


@dataclass(frozen=True)
class FailureGroup:
    fingerprint: str
    category: str
    occurrences: int
    first_seen_line: int
    examples: tuple[str, ...]

def normalize_message(message: str) -> str:
    """Remove timestamps and normalize spacing while preserving line breaks."""
    normalized = re.sub(
        r"\b\d{4}-\d{2}-\d{2}T"
        r"\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\b",
        "",
        message,
    )

    lines = [
        re.sub(r"[ \t]+", " ", line).strip()
        for line in normalized.splitlines()
    ]
    return "\n".join(line for line in lines if line)

def normalize_for_fingerprint(message: str) -> str:
    """Normalize volatile paths, line numbers, and whitespace for stable fingerprints."""
    normalized = normalize_message(message)

    def normalize_frame(match):
        path = match.group(1).replace("\\", "/")
        function = match.group(2)
        parts = PurePosixPath(path).parts

        if "src" in parts:
            relative_path = "/".join(parts[parts.index("src"):])
        elif "tests" in parts:
            relative_path = "/".join(parts[parts.index("tests"):])
        else:
            relative_path = "/".join(parts[-2:])

        return f'File "{relative_path}", in {function}'

    normalized = re.sub(
        r'File "([^"]+)", line \d+, in ([^\s]+)',
        normalize_frame,
        normalized,
    )

    return re.sub(r"\s+", " ", normalized).strip()

def fingerprint_event(event: FailureEvent) -> str:
    """Generate a stable fingerprint for a failure event."""

    signature = (
        f"{event.category}:"
        f"{normalize_for_fingerprint(event.message)}"
    )

    return hashlib.sha256(
        signature.encode("utf-8")
    ).hexdigest()[:12]


def group_failures(
    events: list[FailureEvent],
) -> list[FailureGroup]:
    """Group equivalent failures by stable fingerprint."""

    grouped = defaultdict(list)

    for event in events:
        grouped[fingerprint_event(event)].append(event)

    results = []

    for fingerprint, group in grouped.items():
        results.append(
            FailureGroup(
                fingerprint=fingerprint,
                category=group[0].category,
                occurrences=len(group),
                first_seen_line=min(
                    event.line_number for event in group
                ),
                examples=tuple(
                    dict.fromkeys(
                        normalize_message(event.message)
                        for event in group
                    )
                ),
            )
        )

    return sorted(
        results,
        key=lambda item: item.first_seen_line,
    )
