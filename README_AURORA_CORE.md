# Aurora Core — Quick start (PACK 1)

Requirements:
 - Python 3.11+
 - pip install psutil websockets

Install:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install psutil websockets
```

Create example plugin:
```bash
mkdir -p aurora_modules/example-plugin
cp -r aurora_core/plugin_template/* aurora_modules/example-plugin/
```

Run core:
```bash
python3 aurora_os.py
# or ./tools/aurora_cli_wrapper.sh start
```

Check logs:
```
aurora_logs/orchestrator.log
aurora_logs/example-plugin.out.log
```

Edge test:
```bash
python3 aurora_core/edge_runtime.py
# in separate shell after core started
```

Notes:

For production, run behind systemd or in a container.

Use the Updater.stage_archive() and Updater.activate_staging() to test safe updates.

For heavy sandboxing use containers or cgroups.

---

# How to test immediately (copy/paste)

1. From project root:
```bash
# 1) install deps
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install psutil websockets

# 2) create plugin
mkdir -p aurora_modules/example-plugin
cp aurora_core/plugin_template/* aurora_modules/example-plugin/

# 3) run core
python3 aurora_os.py
```

In another terminal (after core started), test edge:
```bash
python3 aurora_core/edge_runtime.py
# It will connect to auroralink (ws://127.0.0.1:9801) and respond to pings.
```

Inspect logs:
```bash
tail -F aurora_logs/orchestrator.log aurora_logs/example-plugin.out.log
```

Security, sandboxing & production notes (must-read)

The code above uses best-effort local sandboxing. For real safety-critical systems ALWAYS:

Run plugins in containers (Docker) or real OS sandboxes (cgroups, seccomp, AppArmor).

Sign updates and verify signatures before activating.

Use hardware-backed keys (TPM, HSM) to sign and verify packages.

Enforce strict network firewall rules — AuroraLink should be LAN-only unless configured and secured.

For vehicles, satellites, aircraft: use the companion computer pattern (run Aurora in a container on a companion device; gateway to controllers must be certified and require human approvals).

Use monitoring & alerting (Prometheus + Grafana) in production.

Extension points (what PACK 2/3 will add)

After you verify this core, PACK 2/3 will add:

Full node + edge installers (native, docker, systemd, launchd)

Multi-arch Docker builds & Docker Compose

Edge runtime prebuilds for Raspberry Pi / Jetson (ARM)

Sign-and-verify updater tooling

More advanced AuroraLink (P2P discovery, mDNS, NAT traversal, DTLS)

PM2 / process manager integration (optional)

Dashboard + REST control (FastAPI) if you want embedded UI later
