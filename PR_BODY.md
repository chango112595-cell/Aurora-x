### Summary
Tighten CI and repo hygiene; remove error masking; add basic health test.

### Changes
- Add comprehensive `.gitignore` to exclude build artifacts and secrets.
- Add strict E2E workflow (no continue-on-error; deterministic installs).
- Start FastAPI via `uvicorn aurora_x.serve:app`; wait on `/healthz`; run `pytest`.
- Add `tests/test_health.py`.
- Stop tracking previously committed artifacts (kept locally).

### Follow-ups
- Rotate any secrets/certs that were committed; consider history purge (BFG).
- Commit Python/Node lockfiles; add pre-commit (Ruff/Black, ESLint/Prettier).
- Add `README` quickstart and `.env.example`.
