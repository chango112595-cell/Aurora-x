# Remaining work

- Remove remaining hardcoded `localhost` references (run `rg -n "localhost"` and address results in code/scripts/tests/docs).
- Audit tools/scripts that embed localhost defaults (e.g., `tools/*`, `scripts/*`) and parameterize via env vars where appropriate.
- Sweep tests that still assume fixed memory fabric URLs and update to use `AURORA_MEMORY_FABRIC_URL`.
- Review generated module cleanup stubs for any unintended changes.
- Re-validate health/startup scripts in varied environments (CI/VS Code/local).
- Re-run full test suite once remaining host/default changes are complete.
