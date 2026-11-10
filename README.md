# CI Failure Intelligence
[![CI](https://github.com/chaitasipatel25/ci-failure-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/chaitasipatel25/ci-failure-intelligence/actions)

A lightweight CI failure analysis tool that turns noisy build logs into structured, actionable failure reports.

CI pipelines produce large volumes of logs, making it difficult for developers to identify recurring failures, distinguish infrastructure problems from test failures, and understand what needs attention.

**CI Failure Intelligence** provides a deterministic analysis layer that parses CI logs, classifies failures, groups recurring issues using stable fingerprints, and generates reports in text, JSON, and Markdown.

## Why this project?

As engineering organizations scale, CI failures become increasingly difficult to investigate.

Common problems include:
- Repeated failures appearing across builds with slightly different timestamps or paths.
- Infrastructure failures being confused with actual test failures.
- Large logs making it difficult to identify recurring problems.
- Lack of structured failure data for downstream automation and AI-based analysis.

This project explores how a lightweight developer productivity tool can make CI failures easier to understand and investigate.

## Architecture

```text
             CI Log Input
                  |
                  v
             Log Parser
                  |
                  v
          Failure Classifier
                  |
                  v
          Message Normalizer
                  |
                  v
         Failure Fingerprinter
                  |
                  v
          Failure Aggregator
                  |
                  v
           Report Generator
                  |
          +-------+-------+
          |       |       |
        Text    JSON   Markdown
```

## Features

- **Failure classification:** Identifies test, dependency, infrastructure, and timeout failures.
- **Stable fingerprints:** Groups equivalent failures while ignoring volatile timestamps, build paths, and stack trace line numbers.
- **Failure aggregation:** Reports occurrence counts, first-seen line numbers, and representative examples.
- **Multiple output formats:** Generates human-readable text, JSON, and Markdown reports.
- **CLI interface:** Analyze local CI logs or integrate the tool into automation.
- **GitHub Actions integration:** Runs the test suite and publishes a CI failure report as a workflow artifact.

## Example

Input:

```text
2026-11-10T09:30:01Z Starting test execution
FAILED tests/test_payment.py::test_total - AssertionError: expected 100, got 90

Installing dependencies...
ModuleNotFoundError: No module named 'requests'

Starting integration tests...
psycopg.OperationalError: connection timed out
```

Run:

```bash
ci-inspect tests/fixtures/sample_ci.log
```

Example output:

```text
CI Failure Intelligence
==================================================

Total failure events: 3
Unique failure groups: 3

Failure Summary
--------------------------------------------------

Category: TEST_FAILURE
Occurrences: 1
First seen: line 3

Category: DEPENDENCY_FAILURE
Occurrences: 1
First seen: line 6

Category: INFRASTRUCTURE_FAILURE
Occurrences: 1
First seen: line 9
```

## Installation

Requires Python 3.11 or newer.

```bash
git clone https://github.com/chaitasipatel25/ci-failure-intelligence
cd ci-failure-intelligence

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

## Usage

Analyze a CI log:

```bash
ci-inspect path/to/ci.log
```

Generate JSON:

```bash
ci-inspect path/to/ci.log --format json
```

Generate Markdown:

```bash
ci-inspect path/to/ci.log --format markdown
```

Write the report to a file:

```bash
ci-inspect path/to/ci.log \
  --format markdown \
  --output report.md
```

## Development

Run the test suite:

```bash
pytest -v
```

The tests cover parsing, failure classification, fingerprint stability, grouping, reporting, and CLI behavior.

## Design Decisions

**Deterministic analysis first**

Failure classification and grouping are deterministic. This makes the output reproducible and avoids introducing LLM variability into the core analysis path.

**Stable fingerprints**

Fingerprints use normalized failure messages and stack traces, reducing noise from timestamps, build-specific paths, and line-number changes.

**Multiple output formats**

JSON supports downstream integrations, Markdown supports CI artifacts and pull request workflows, and text supports local debugging.

**Separation of concerns**

Parsing, fingerprinting, aggregation, reporting, and CLI behavior are implemented as separate modules so that additional analysis capabilities can be introduced without coupling them to the core pipeline.

## Current Limitations

- Classification relies on predefined patterns and may not recognize every CI framework or failure format.
- Fingerprinting uses normalized text and stack trace information rather than semantic root-cause analysis.
- The current implementation analyzes supplied logs; it does not yet retrieve logs directly from CI providers.
- Reports identify and group failures but do not independently establish their root cause.

## Potential Extensions

- Evidence-backed LLM root-cause analysis with deterministic fallback.
- GitHub Actions and other CI provider integrations.
- Historical failure trends and regression detection.
- Failure ownership and service-level routing.
- Test impact analysis and automated remediation suggestions.

## Technology

Python · pytest · GitHub Actions
