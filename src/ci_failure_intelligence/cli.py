
import argparse
from pathlib import Path

from ci_failure_intelligence.parser import parse_log
from ci_failure_intelligence.fingerprints import group_failures
from ci_failure_intelligence.reports import (
    render_json,
    render_markdown,
    render_text,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and group CI failures."
    )

    parser.add_argument("log_file", help="Path to the CI log file")

    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Report format",
    )

    parser.add_argument(
        "--output",
        help="Write report to a file instead of stdout",
    )

    args = parser.parse_args()
    log_path = Path(args.log_file)

    if not log_path.is_file():
        parser.error(f"Log file not found: {log_path}")

    try:
        log_content = log_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        parser.error(f"Could not read log file: {error}")

    events = parse_log(log_content)
    groups = group_failures(events)

    renderers = {
        "text": render_text,
        "json": render_json,
        "markdown": render_markdown,
    }

    output = renderers[args.format](groups)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output + "\n", encoding="utf-8")
        print(f"Report written to {output_path}")
    else:
        print(output)


if __name__ == "__main__":
    main()
