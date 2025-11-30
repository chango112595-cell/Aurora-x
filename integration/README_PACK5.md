# PACK 5 — Full Integration Pack (Operator dashboard, updater, marketplace, auto-deploy)

Overview:
- Operator dashboard: integration/dashboard/backend.py + static UI
- Updater service: integration/updater/updater_service.py (staging, verify, promote)
- Marketplace: local catalog to drop plugin tarballs
- Auto-deploy: docker_rollout.sh + CI snippets
- Safety: all upgrades require operator approval for safety-critical devices (configurable)

Quickstart:
1. Start Aurora core (pack1): `python3 aurora_os.py`
2. Start dashboard: `python3 integration/dashboard/backend.py` (port 9711)
3. Start updater service (if desired): `python3 integration/updater/updater_service.py` (port 9710)
4. Use UI: open http://localhost:9711/
5. Upload update tar, stage, and promote via dashboard (or use REST endpoints)

Operator flow (recommended):
- Build update pool via CI (integration/ci/release.yml)
- Download updater artifact (aurora-update.tar.gz) to operator machine
- Upload artifact via dashboard
- Stage artifact (verifies signature)
- Test on a canary device or container
- Approve via dashboard (applies atomic swap / backup)
- Observe logs and audit trail

Security:
- Keep AURORA_API_TOKEN secret for API access.
- Use GPG/HSM for signing releases (CI uses secret GPG_PRIVATE in secrets).
- For cars/aircraft/satellites: require manual signature + verified ground segment.
