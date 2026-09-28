# Security policy

## Scope

PathParity is a local, read-only path analyzer. It does not connect to a service, execute a
command, follow symlinks, or modify the scanned tree. A security report should still explain how a
crafted path, manifest, or invocation could violate those guarantees.

## Reporting a vulnerability

Please use GitHub’s private security advisory flow for this repository. Include:

1. the affected version or commit;
2. a minimal reproduction that does not contain secrets or personal data;
3. the expected safety property and the observed behavior; and
4. any safe mitigation you already tested.

Do not open a public issue for an exploitable path traversal, command execution, secret exposure,
or unintended filesystem mutation until a fix or coordinated disclosure is available.

## Security boundaries

- Treat reports as advisory output, not proof that a destination is safe.
- Keep scan inputs untrusted and bounded in CI.
- Do not add network calls, subprocess execution, automatic fixes, or credential handling without a
  separate threat-model review.
