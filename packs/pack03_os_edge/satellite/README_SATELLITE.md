# Aurora EdgeOS - Satellite Runtime (3G)

## Overview
Companion pattern for spacecraft: uplink package generator, ground-signed uplink flow, fail-safe execution, simulated SAT link.

## Files

- `ground/uplink_generator.py` - Build signed uplink packages
- `ground/send_uplink_stub.py` - Stub to send via certified ground station
- `companion/satellite_agent.py` - Companion agent that receives uplink (simulated)

## Usage

```bash
# Generate uplink package
python3 satellite/ground/uplink_generator.py

# Sign the package
gpg --detach-sign satellite/packages/uplink_*.json
```

## Notes

Satellite uplink must go through certified ground station uplink chain; this is only companion-side tooling.
