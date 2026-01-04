Aurora Ops Runbook - quick run steps
1. Ensure prerequisites: python3, docker, docker-compose
2. Run: bash ops/run_all_deploy.sh
3. Monitor logs: docker-compose logs -f or tail -f logs/*
4. To rollback: use deploy/rollback.sh with tag