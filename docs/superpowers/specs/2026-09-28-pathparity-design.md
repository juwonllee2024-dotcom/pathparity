# PathParity design — 2026-09-28

## User problem

Maintainers discover cross-platform filename failures after a clone, archive extraction, or agent
handoff has already failed. The current machine is often unable to create the offending name, so a
normal filesystem walk cannot even reproduce the problem.

## Product boundary

PathParity is a read-only, offline preflight. It accepts either a directory or a newline-delimited
logical path manifest. It reports deterministic finding codes and exit status; it never fixes the
tree, runs repository content, follows symlinks, or contacts a service.

## Candidate review

Scores are 1–5 for pain severity, novelty, buildability today, organic shareability, and open-source
fit. They are founder hypotheses, not market facts.

| Candidate | Pain | Novelty | Build | Share | OSS | Total | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| PathParity — cross-OS tree preflight | 5 | 4 | 5 | 4 | 5 | 23 | Build |
| ShellLens — exact argv/quoting preview | 4 | 3 | 5 | 3 | 5 | 20 | Reject: overlaps command translators and shell diagnostics |
| UploadLens — local-file handoff inspection | 4 | 2 | 4 | 3 | 4 | 17 | Reject: crowded by upload/privacy scanners and PromptParcel/FreshSend |
| HandoffCard — portable agent context packet | 4 | 2 | 4 | 3 | 4 | 17 | Reject: overlaps ReproCard/Finish and is hard to explain in one demo |

### Candidate hypotheses

#### PathParity

- **Fact:** Windows and Linux disagree about case sensitivity; Git and major repositories document
  invalid-path and long-path checkout failures.
- **Hypothesis:** a 30-second, local report before publishing or cloning will prevent a high-cost,
  low-frequency failure that ordinary tools surface too late.
- **Different by one thing:** it scans logical manifests, so it can inspect names the current OS
  cannot create.
- **Smallest 7-day experiment:** ask five maintainers to run `scan-list` on a repository/archive
  file list and record whether any finding changes a release or CI decision.

#### ShellLens

- **Fact:** quoting and glob expansion differ across Bash, PowerShell, and cmd.
- **Hypothesis:** previewing the exact argv vector would prevent destructive copy/paste mistakes.
- **Different by one thing:** it would show expansion without executing.
- **Smallest 7-day experiment:** collect ten commands that failed after copy/paste and compare the
  preview to the shell’s actual argv.
- **Decision:** useful, but too close to existing shell translation and command-safety tools for a
  strong first public product.

#### UploadLens

- **Fact:** people worry about sending the wrong local file or hidden secrets to AI tools.
- **Hypothesis:** a visible, local-only inspection receipt would increase confidence before upload.
- **Different by one thing:** an explicit user-selected file would be inspected without auto-send.
- **Smallest 7-day experiment:** measure whether ten AI users abandon or change an attachment after
  seeing a local receipt.
- **Decision:** the problem is real, but the market and this account already contain multiple
  upload, prompt, and file-handoff projects.

#### HandoffCard

- **Fact:** agent sessions lose environment, command, and expected-result context.
- **Hypothesis:** a compact review card would make handoff and bug reproduction less ambiguous.
- **Different by one thing:** every field would be explicit and shareable as plain text/JSON.
- **Smallest 7-day experiment:** ask five developers to replace a free-form handoff with a card and
  count clarification messages.
- **Decision:** valuable but overlaps existing reproduction and action-capsule projects.

## MVP choices

- Python 3.10+, standard library runtime, no network or subprocesses.
- `scan DIRECTORY` for actual trees and `scan-list MANIFEST` for logical trees.
- Seven stable finding codes covering the highest-confidence Windows/macOS hazards plus symlinks.
- Text for humans, JSON for CI and agents.
- Exit `0` clean, `1` findings, `2` invalid input.

## Non-goals

- Automatically rename or delete files.
- Change Git, Windows, macOS, or filesystem settings.
- Claim a tree is universally portable.
- Upload paths or contents to a service.

## Success signal

The first useful proof is not a star count. It is a maintainer saying, “This would have caught my
failed checkout,” then putting the command in CI or a release checklist.
