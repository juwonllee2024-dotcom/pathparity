# Founder note — PathParity

## Today's problem

Cross-platform teams publish a tree on one filesystem and discover too late that another developer,
CI runner, archive extractor, or AI coding workspace cannot materialize it. The failure is especially
frustrating when the author’s own operating system cannot create the bad name, making ordinary local
testing blind.

## First user

The first user is a maintainer of a cross-platform open-source repository, especially one with
generated fixtures, archives, datasets, or agent-produced files. The first ten can be found in
repository issue threads about Windows checkout failures and in projects that advertise Windows/macOS
support. No outreach or account changes are performed by this MVP.

## Confirmed facts

1. [Microsoft’s WSL case-sensitivity guide](https://github.com/MicrosoftDocs/WSL/blob/main/WSL/case-sensitivity.md)
   states that Linux can distinguish `FOO.txt` and `foo.txt` while typical Windows-mounted folders
   are case-insensitive.
2. [.NET’s Windows requirements](https://github.com/dotnet/runtime/blob/main/docs/workflow/requirements/windows-requirements.md)
   documents Git checkout failures from Windows path limits and the separate Git long-path setting.
3. [SWE-agent #1518](https://github.com/SWE-agent/SWE-agent/issues/1518) reports a current,
   concrete checkout failure on default Git-for-Windows caused by a deep tracked path.
4. [Git’s security advisory](https://github.com/git/git/security/advisories/GHSA-4qvh-qvv7-frc7)
   shows that platform path handling can be a security boundary, not just a cosmetic nuisance.

## Innovation hypothesis

“A deterministic preflight that understands logical names before checkout will catch failures that
platform-local file walks cannot see.”

The one-line difference is the manifest mode: users can scan names that their current filesystem
cannot create.

## User value

- **Time:** catch the problem before a teammate spends time debugging a failed checkout.
- **Stress:** replace a vague OS-specific error with a path and stable reason code.
- **Trust:** show that the report was local, read-only, and deterministic.

## Business hypothesis

The free MIT CLI is the distribution wedge. A hosted CI annotation, policy packs, or organization
reporting layer could eventually be paid, but no revenue is assumed and no payment system is built.
The 7-day signal is whether maintainers keep the command in CI after one useful catch.

## Today's progress

- Built a Python MVP with directory and manifest inputs.
- Added seven deterministic checks, text/JSON output, and exit codes.
- Added tests, cross-platform CI, security policy, contribution guide, license, examples, and a
  verification record.
- Published the repository and v0.1.0 release after local verification, then repaired the CI build
  backend and prepared v0.1.1.

## Still unproven

- How often a maintainer encounters a problem that these seven checks catch.
- Whether a report causes a repository to adopt the tool rather than fix the file manually.
- Whether the name and one-line promise earn organic sharing.
- Whether any paid layer is needed or wanted.

## Hope grounded in evidence

The problem produces visible, reproducible failures in current GitHub issue threads, while the MVP
is small enough to run offline in CI. That combination gives the project a concrete adoption test,
even though it does not guarantee popularity or 100,000 stars.

## One experiment for tomorrow

Run `pathparity scan-list` against one public cross-platform repository’s tracked-name list and see
whether the findings are actionable, false-positive-free, and easy to paste into an issue.
