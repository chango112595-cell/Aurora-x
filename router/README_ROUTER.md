# Aurora EdgeOS - Router Runtime (3F)

## Overview
OpenWRT package template, UCI-based config installer, secure firewall and NAT rules, containerized router agent.

## Files

- `agent.py` - Router agent for config and telemetry
- `openwrt/` - Files for OpenWRT package
- `install-openwrt-package.sh` - Build/install instructions

## Usage

```bash
python3 router/agent.py
```

## Notes

For routers, prefer containerized agent to avoid modifying base firmware. Use opkg package for OpenWRT.
