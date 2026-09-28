from __future__ import annotations

import json
from pathlib import Path

from pathparity.cli import main


def test_scan_list_emits_machine_readable_report(tmp_path: Path, capsys: object) -> None:
    manifest = tmp_path / "paths.txt"
    manifest.write_text("CON.txt\ndocs/README.md\ndocs/readme.md\n", encoding="utf-8")

    exit_code = main(["scan-list", str(manifest), "--format", "json"])

    assert exit_code == 1
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    report = json.loads(output)
    assert report["status"] == "block"
    assert report["summary"]["findings"] == 2


def test_scan_list_clean_report_returns_zero(tmp_path: Path, capsys: object) -> None:
    manifest = tmp_path / "paths.txt"
    manifest.write_text("src/main.py\nREADME.md\n", encoding="utf-8")

    exit_code = main(["scan-list", str(manifest), "--format", "json"])

    assert exit_code == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert json.loads(output)["status"] == "clean"
