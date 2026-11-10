
import json

from ci_failure_intelligence.fingerprints import FailureGroup


def build_report(groups: list[FailureGroup]) -> dict:
    total_events = sum(group.occurrences for group in groups)

    return {
        "total_failure_events": total_events,
        "unique_failure_groups": len(groups),
        "failures": [
            {
                "fingerprint": group.fingerprint,
                "category": group.category,
                "occurrences": group.occurrences,
                "first_seen_line": group.first_seen_line,
                "examples": list(group.examples),
            }
            for group in groups
        ],
    }


def render_json(groups: list[FailureGroup]) -> str:
    return json.dumps(build_report(groups), indent=2)


def render_text(groups: list[FailureGroup]) -> str:
    report = build_report(groups)

    lines = [
        "CI Failure Intelligence",
        "=" * 50,
        f"Total failure events: {report['total_failure_events']}",
        f"Unique failure groups: {report['unique_failure_groups']}",
    ]

    if not groups:
        lines.append("\nNo recognizable failures found.")
        return "\n".join(lines)

    lines.extend(["", "Failure Summary", "-" * 50])

    for group in groups:
        lines.extend([
            "",
            f"Category: {group.category}",
            f"Occurrences: {group.occurrences}",
            f"First seen: line {group.first_seen_line}",
            f"Fingerprint: {group.fingerprint}",
        ])

        for example in group.examples:
            lines.append("  Example:")
            lines.extend(f"    {line}" for line in example.splitlines())

    return "\n".join(lines)


def render_markdown(groups: list[FailureGroup]) -> str:
    report = build_report(groups)

    lines = [
        "# CI Failure Intelligence",
        "",
        f"- **Total failure events:** {report['total_failure_events']}",
        f"- **Unique failure groups:** {report['unique_failure_groups']}",
        "",
    ]

    if not groups:
        lines.append("No recognizable failures found.")
        return "\n".join(lines)

    lines.extend([
        "| Category | Occurrences | First seen | Fingerprint |",
        "|---|---:|---:|---|",
    ])

    for group in groups:
        lines.append(
            f"| {group.category} | {group.occurrences} "
            f"| Line {group.first_seen_line} "
            f"| `{group.fingerprint}` |"
        )

    for index, group in enumerate(groups, start=1):
        lines.extend([
            "",
            f"## {index}. {group.category}",
            "",
            f"**Occurrences:** {group.occurrences}",
            "",
        ])

        for example in group.examples:
            lines.extend([
                "```text",
                example,
                "```",
                "",
            ])

    return "\n".join(lines)
