from __future__ import annotations

from pathlib import Path

from pathparity.scanner import analyze_paths, scan_directory


def codes(findings: list[dict[str, object]]) -> set[str]:
    return {str(finding["code"]) for finding in findings}


def test_analyze_paths_finds_cross_platform_breakage() -> None:
    findings = analyze_paths(
        [
            "CON.txt",
            "docs/README.md",
            "docs/readme.md",
            "bad:name.txt",
            "folder/notes. ",
            "cafe\u0301.txt",
            "caf\u00e9.txt",
        ],
        platforms={"windows", "macos", "linux"},
    )

    assert {
        "windows-reserved-name",
        "windows-invalid-character",
        "windows-trailing-dot-space",
        "case-collision",
        "macos-normalization-collision",
    } <= codes(findings)


def test_clean_directory_has_no_findings(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")

    assert scan_directory(tmp_path, {"windows", "macos", "linux"}) == []


def test_platform_filter_avoids_unrequested_rules() -> None:
    findings = analyze_paths(["CON.txt", "docs/README.md", "docs/readme.md"], {"linux"})

    assert findings == []
