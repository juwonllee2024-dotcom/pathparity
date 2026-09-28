# Contributing to PathParity

Thanks for helping make cross-platform projects less surprising.

## Local setup

```powershell
python -m pip install -e .[dev]
python -m pytest -q
ruff check .
mypy src
```

## Design rules

- Keep the core scanner deterministic, standard-library-only, and read-only.
- Add a failing test before production behavior (RED → minimal GREEN → cleanup).
- Prefer a stable finding code over a clever message; integrations depend on codes.
- Never follow symlinks or execute repository content during a scan.
- Changes that mutate a tree need a separate proposal, explicit preview, and rollback story.
- Update `CHANGELOG.md` and the verification record for user-visible behavior.

## Pull requests

Explain the user pain, the portability rule, and a smallest reproducible example. Run the same
commands used by CI and include their results in the pull request description.
