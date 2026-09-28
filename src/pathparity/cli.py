"""Command-line interface for PathParity."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from .scanner import Finding, analyze_paths, build_report, scan_directory


def _platforms(value: str) -> set[str]:
    selected = {name.strip().lower() for name in value.split(",") if name.strip()}
    allowed = {"windows", "macos", "linux"}
    unknown = selected - allowed
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown platform(s): {', '.join(sorted(unknown))}")
    if not selected:
        raise argparse.ArgumentTypeError("choose at least one platform")
    return selected


def _add_common_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument(
        "--platform",
        type=_platforms,
        default={"windows", "macos", "linux"},
        help="comma-separated targets (default: windows,macos,linux)",
    )
    command.add_argument("--format", choices=("text", "json"), default="text")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pathparity",
        description="Find file-tree paths that work here but break on another OS.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    scan = commands.add_parser("scan", help="scan a directory without changing it")
    scan.add_argument("directory", type=Path)
    _add_common_arguments(scan)
    scan_list = commands.add_parser("scan-list", help="scan a newline-delimited path manifest")
    scan_list.add_argument("manifest", type=Path)
    _add_common_arguments(scan_list)
    return parser


def _read_manifest(path: Path) -> list[str]:
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(f"cannot read manifest {path}: {error}") from error
    paths: list[str] = []
    for line in content.splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            paths.append(line)
    return paths


def _text_report(report: dict[str, object]) -> str:
    summary = cast(dict[str, int], report["summary"])
    platforms = cast(list[str], report["platforms"])
    lines = [
        "PathParity",
        f"Status: {cast(str, report['status']).upper()}",
        f"Source: {report['source']}",
        f"Platforms: {', '.join(platforms)}",
        f"Findings: {summary['findings']} (blocks: {summary['blocks']}, reviews: {summary['reviews']})",
    ]
    findings = cast(list[Finding], report["findings"])
    if findings:
        lines.append("")
        lines.append("Findings:")
        for finding in findings:
            related = finding["related_paths"]
            suffix = f"; also: {', '.join(related)}" if related else ""
            lines.append(
                f"- [{str(finding['severity']).upper()}] {finding['code']} — {finding['path']}{suffix}\n"
                f"  {finding['message']}"
            )
    else:
        lines.append("\nNo portability findings.")
    return "\n".join(lines)


def _exit_code(report: dict[str, object]) -> int:
    return 0 if report["status"] == "clean" else 1


def main(argv: Sequence[str] | None = None) -> int:
    try:
        reconfigure = getattr(sys.stdout, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            findings: list[Finding] = scan_directory(args.directory, args.platform)
            source = str(args.directory)
        else:
            paths = _read_manifest(args.manifest)
            findings = analyze_paths(paths, args.platform)
            source = str(args.manifest)
        report = build_report(source, args.platform, findings)
    except ValueError as error:
        parser.error(str(error))
        return 2

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True))
    else:
        print(_text_report(report))
    return _exit_code(report)
