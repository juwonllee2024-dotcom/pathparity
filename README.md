# PathParity 🧭

## Find the files that work on your machine — and break on someone else’s OS.

One Linux checkout can hide a Windows-invalid filename. One case-sensitive clone can hide a
macOS/Windows collision. PathParity is a tiny, local-first preflight that finds those traps before
they become a failed clone, broken archive, or “works on my machine” handoff.

```text
pathparity scan .
      ↓
“Your tree contains CON.txt, two files that differ only by case,
 and a path that will exceed Windows’ safe checkout budget.”
```

No account. No cloud. No AI. No file changes.

## Try it in 30 seconds

```powershell
python -m pip install -e .

# Inspect a real directory. This never writes, deletes, renames, or executes anything.
python -m pathparity scan .

# Inspect a Git/archive manifest, including names your current OS cannot create.
python -m pathparity scan-list examples/problem-paths.txt --format json
```

The demo manifest intentionally contains cross-platform hazards, so the command exits `1` and
prints a reviewable report. A clean tree exits `0`; an unreadable input exits `2`.

## What it catches today

| Finding | Why it matters |
| --- | --- |
| `windows-reserved-name` | `CON`, `NUL`, `COM1`, and friends cannot be materialized normally on Windows. |
| `windows-invalid-character` | Windows rejects characters such as `:` and `?` in path components. |
| `windows-trailing-dot-space` | Windows trims trailing dots/spaces, so the name is not stable across machines. |
| `windows-long-path` | A deep checkout can hit the Windows path budget even when the repository is valid elsewhere. |
| `case-collision` | Case-insensitive destinations cannot keep sibling names such as `README.md` and `readme.md` distinct. |
| `macos-normalization-collision` | Different Unicode spellings can normalize to the same name on macOS filesystems. |
| `symlink` | A symlink’s meaning or support can change in a clone, archive, or restricted workspace. |

Choose targets when a repository has a narrower compatibility promise:

```powershell
python -m pathparity scan . --platform windows,linux --format json
```

## Built for trustworthy automation

- **Read-only:** only directory metadata and names are inspected.
- **Offline:** the runtime has zero network, subprocess, or model dependencies.
- **Explicit scope:** scan a directory or provide a newline-delimited path manifest.
- **Deterministic:** stable finding codes, paths, ordering, and exit codes.
- **Machine-readable:** JSON is suitable for CI, release checks, and agent handoffs.
- **Safe default:** `.git`, `.hg`, and `.svn` metadata directories are skipped; symlinks are reported but never followed.

PathParity reports risk. It does not silently rename files, change Git settings, enable long paths,
or claim that a tree is safe for every filesystem. A `review` finding deserves a human decision;
a `block` finding is a compatibility failure for the selected target.

## Commands

```text
pathparity scan DIRECTORY [--platform windows,macos,linux] [--format text|json]
pathparity scan-list MANIFEST [--platform windows,macos,linux] [--format text|json]
```

Manifest rules: one logical relative path per line; blank lines and lines beginning with `#` are
ignored; both `/` and `\` separators are accepted. `scan-list` is useful for Git trees, archive
indexes, build outputs, and generated file lists that cannot be recreated on the current OS.

## Why this exists

Cross-platform path failures are not theoretical:

- [Microsoft’s WSL documentation](https://github.com/MicrosoftDocs/WSL/blob/main/WSL/case-sensitivity.md)
  explains that Linux treats `FOO.txt` and `foo.txt` as distinct while typical Windows-mounted
  directories are case-insensitive.
- [.NET’s Windows requirements](https://github.com/dotnet/runtime/blob/main/docs/workflow/requirements/windows-requirements.md)
  documents clone failures from Windows path limits and the need for Git’s long-path setting.
- [SWE-agent issue #1518](https://github.com/SWE-agent/SWE-agent/issues/1518), opened in August
  2026, shows a current repository whose checkout fails on a default Git-for-Windows setup even
  though the tracked path is only about 180 characters.
- [Git’s `core.protectNTFS` advisory](https://github.com/git/git/security/advisories/GHSA-4qvh-qvv7-frc7)
  demonstrates why platform-specific path handling is also a security boundary.

The useful missing moment is before the failure: a small report that a maintainer can paste into a
pull request, release checklist, or agent handoff.

## Development

```powershell
python -m pip install -e .[dev]
python -m pytest -q
ruff check .
mypy src
python -m build --no-isolation
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the
[verification record](docs/verification/2026-09-28.md).

## Roadmap

1. Git tree input that reads names without checking out the worktree.
2. Archive index adapters for ZIP/TAR without extraction.
3. Optional policy files for a project’s supported operating systems and path budget.
4. Compact CI annotations and a GitHub check-run formatter.

The project will stay local-first and reviewable. Fixes that mutate a tree belong in an explicit,
separate command with a preview and rollback plan.

## License

MIT — see [LICENSE](LICENSE).
