
import argparse
import json
from pathlib import Path

from ci_failure_intelligence.parser import parse_log
from ci_failure_intelligence.fingerprints import group_failures


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and group CI failures."
    )

    parser.add_argument(
        "log_file",
        help="Path to the CI log file",
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()
    log_path = Path(args.log_file)

    if not log_path.is_file():
        parser.error(f"Log file not found: {log_path}")

    log_content = log_path.read_text(encoding="utf-8")

    events = parse_log(log_content)
    groups = group_failures(events)

    report = {
        "total_failure_events": len(events),
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

    if args.format == "json":
        print(json.dumps(report, indent=2))
        return

    print("\nCI Failure Intelligence")
    print("=" * 50)
    print(f"Total failure events: {len(events)}")
    print(f"Unique failure groups: {len(groups)}")

    if not groups:
        print("\nNo recognizable failures found.")
        return

    print("\nFailure Summary")
    print("-" * 50)

    for group in groups:
        print(f"\nCategory: {group.category}")
        print(f"Occurrences: {group.occurrences}")
        print(f"First seen: line {group.first_seen_line}")
        print(f"Fingerprint: {group.fingerprint}")

        for example in group.examples:
            print(f"  Example: {example}")


if __name__ == "__main__":
    main()
