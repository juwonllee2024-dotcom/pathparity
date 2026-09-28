"""Pure, read-only portability checks for file-tree paths."""

from __future__ import annotations

import os
import unicodedata
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Literal, TypedDict

Platform = Literal["windows", "macos", "linux"]
Severity = Literal["block", "review"]
SUPPORTED_PLATFORMS: frozenset[str] = frozenset({"windows", "macos", "linux"})
WINDOWS_RESERVED = frozenset(
    {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
)
WINDOWS_INVALID_CHARACTERS = frozenset('<>:"|?*')
SKIPPED_METADATA_DIRECTORIES = frozenset({".git", ".hg", ".svn"})


class Finding(TypedDict):
    code: str
    platform: str
    severity: Severity
    path: str
    related_paths: list[str]
    message: str


def _components(path: str) -> tuple[str, ...]:
    normalized = path.replace("\\", "/")
    return tuple(part for part in normalized.split("/") if part not in {"", "."})


def _finding(
    code: str,
    platform: str,
    severity: Severity,
    path: str,
    message: str,
    related_paths: Iterable[str] = (),
) -> Finding:
    return {
        "code": code,
        "platform": platform,
        "severity": severity,
        "path": path,
        "related_paths": sorted(set(related_paths)),
        "message": message,
    }


def _validate_platforms(platforms: set[str]) -> None:
    unknown = platforms - SUPPORTED_PLATFORMS
    if unknown:
        names = ", ".join(sorted(unknown))
        raise ValueError(f"unsupported platform(s): {names}")
    if not platforms:
        raise ValueError("at least one platform is required")


def analyze_paths(
    paths: Iterable[str],
    platforms: set[str],
    symlink_paths: Iterable[str] = (),
) -> list[Finding]:
    """Analyze logical relative paths without touching or changing the filesystem."""

    _validate_platforms(platforms)
    normalized_paths = sorted({path.replace("\\", "/").lstrip("./") for path in paths if path.strip()})
    symlinks = {path.replace("\\", "/").lstrip("./") for path in symlink_paths}
    findings: list[Finding] = []

    for path in normalized_paths:
        components = _components(path)
        if "windows" in platforms:
            reserved_components = [
                component
                for component in components
                if component.rstrip(" .").split(".", 1)[0].casefold() in WINDOWS_RESERVED
            ]
            invalid_components = [
                component
                for component in components
                if any(character in WINDOWS_INVALID_CHARACTERS or ord(character) < 32 for character in component)
            ]
            trailing_components = [
                component for component in components if component not in {".", ".."} and component != component.rstrip(" .")
            ]
            if reserved_components:
                findings.append(
                    _finding(
                        "windows-reserved-name",
                        "windows",
                        "block",
                        path,
                        f"Windows reserves this name: {', '.join(reserved_components)}",
                    )
                )
            if invalid_components:
                findings.append(
                    _finding(
                        "windows-invalid-character",
                        "windows",
                        "block",
                        path,
                        f"Windows rejects characters in: {', '.join(invalid_components)}",
                    )
                )
            if trailing_components:
                findings.append(
                    _finding(
                        "windows-trailing-dot-space",
                        "windows",
                        "block",
                        path,
                        f"Windows trims trailing dots/spaces in: {', '.join(trailing_components)}",
                    )
                )
            if len(path) > 240:
                findings.append(
                    _finding(
                        "windows-long-path",
                        "windows",
                        "review",
                        path,
                        f"Relative path is {len(path)} characters; leave room for the destination folder.",
                    )
                )
        if path in symlinks:
            findings.append(
                _finding(
                    "symlink",
                    "all",
                    "review",
                    path,
                    "Symlinks can change meaning or be unsupported in a clone/archive destination.",
                )
            )

    sibling_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    normalized_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for path in normalized_paths:
        components = _components(path)
        if not components:
            continue
        parent = "/".join(components[:-1])
        name = components[-1]
        sibling_groups[(parent, name.casefold())].append(path)
        normalized_groups[(parent, unicodedata.normalize("NFD", name))].append(path)

    if "windows" in platforms or "macos" in platforms:
        for (_, _), group in sorted(sibling_groups.items()):
            if len(group) > 1:
                findings.append(
                    _finding(
                        "case-collision",
                        "windows/macos",
                        "review",
                        group[0],
                        "These sibling paths differ only by case on a case-insensitive filesystem.",
                        group[1:],
                    )
                )
    if "macos" in platforms:
        for (_, _), group in sorted(normalized_groups.items()):
            if len(group) > 1 and len({name for name in group}) > 1:
                if len({name.casefold() for name in group}) == 1:
                    continue
                findings.append(
                    _finding(
                        "macos-normalization-collision",
                        "macos",
                        "review",
                        group[0],
                        "These sibling paths normalize to the same Unicode spelling on macOS.",
                        group[1:],
                    )
                )

    return sorted(findings, key=lambda finding: (finding["path"], finding["code"], finding["platform"]))


def scan_directory(root: Path, platforms: set[str]) -> list[Finding]:
    """Collect a directory tree without following symlinks, then analyze it."""

    _validate_platforms(platforms)
    if root.is_symlink():
        raise ValueError("refusing to scan a symlink as the root")
    if not root.is_dir():
        raise ValueError(f"directory not found: {root}")

    paths: list[str] = []
    symlink_paths: list[str] = []
    for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        for name in list(directory_names):
            candidate = current_path / name
            relative = candidate.relative_to(root).as_posix()
            if name in SKIPPED_METADATA_DIRECTORIES:
                directory_names.remove(name)
            elif candidate.is_symlink():
                symlink_paths.append(relative)
                directory_names.remove(name)
            else:
                paths.append(relative)
        for name in file_names:
            candidate = current_path / name
            relative = candidate.relative_to(root).as_posix()
            paths.append(relative)
            if candidate.is_symlink():
                symlink_paths.append(relative)
    return analyze_paths(paths, platforms, symlink_paths)


def build_report(source: str, platforms: set[str], findings: list[Finding]) -> dict[str, object]:
    """Build the stable JSON shape used by the CLI and integrations."""

    blocks = sum(finding["severity"] == "block" for finding in findings)
    reviews = len(findings) - blocks
    status = "block" if blocks else "review" if reviews else "clean"
    return {
        "tool": "pathparity",
        "version": "0.1.0",
        "source": source,
        "platforms": [platform for platform in ("windows", "macos", "linux") if platform in platforms],
        "status": status,
        "summary": {"findings": len(findings), "blocks": blocks, "reviews": reviews},
        "findings": findings,
    }
