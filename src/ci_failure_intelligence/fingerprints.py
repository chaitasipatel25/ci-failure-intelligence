
import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass

from ci_failure_intelligence.parser import FailureEvent


@dataclass(frozen=True)
class FailureGroup:
    fingerprint: str
    category: str
    occurrences: int
    first_seen_line: int
    examples: tuple[str, ...]


def normalize_message(message: str) -> str:
    """Normalize harmless formatting differences."""

    normalized = message.strip()

    # Remove ISO-style timestamps.
    normalized = re.sub(
        r"\b\d{4}-\d{2}-\d{2}T"
        r"\d{2}:\d{2}:\d{2}(?:\.\d+)?Z\b",
        "",
        normalized,
    )

    # Normalize whitespace.
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def fingerprint_event(event: FailureEvent) -> str:
    """Generate a stable fingerprint for a failure event."""

    normalized = normalize_message(event.message)

    signature = f"{event.category}:{normalized}"

    return hashlib.sha256(
        signature.encode("utf-8")
    ).hexdigest()[:12]


def group_failures(
    events: list[FailureEvent],
) -> list[FailureGroup]:
    """Group failure events by their fingerprints."""

    grouped = defaultdict(list)

    for event in events:
        fingerprint = fingerprint_event(event)
        grouped[fingerprint].append(event)

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
