
import json

from ci_failure_intelligence.cli import main


def test_cli_produces_valid_json(
    tmp_path, monkeypatch, capsys
):
    log_file = tmp_path / "sample.log"
    log_file.write_text(
        "AssertionError: expected 100, got 90\n"
        "ModuleNotFoundError: No module named 'requests'\n"
    )

    monkeypatch.setattr(
        "sys.argv",
        ["ci-inspect", str(log_file), "--format", "json"],
    )

    main()

    output = capsys.readouterr().out
    report = json.loads(output)

    assert report["total_failure_events"] == 2
    assert report["unique_failure_groups"] == 2
    assert len(report["failures"]) == 2


def test_cli_handles_no_failures(
    tmp_path, monkeypatch, capsys
):
    log_file = tmp_path / "clean.log"
    log_file.write_text("Build started\nBuild completed\n")

    monkeypatch.setattr(
        "sys.argv",
        ["ci-inspect", str(log_file), "--format", "json"],
    )

    main()

    report = json.loads(capsys.readouterr().out)

    assert report["total_failure_events"] == 0
    assert report["unique_failure_groups"] == 0
    assert report["failures"] == []
