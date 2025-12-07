# Aurora EdgeOS - Aviation Runtime (3C)

## Overview
RTOS partitioning skeleton with companion-computer pattern for avionics-safe process supervision.

## Key Points

- Companion computer pattern: collect telemetry, prepare signed uplink packages, human signs, separate certified uplink system performs actual uplink.
- Do not auto-send flight-critical commands.
- Use HSM-backed signing for uplink packages.

## Files

- `companion_gateway.py` - Companion computer gateway (safe; does not send flight controls)
- `flight_package.py` - Signed uplink package generator
- `rtos_partition/template.c` - Templates for RTOS partition skeleton (FreeRTOS/Zephyr placeholders)
- `install-aviation.sh` - Installer script

## Installation

```bash
./aviation/install-aviation.sh
```

## Usage

```bash
# Start companion gateway
python3 aviation/companion_gateway.py

# Create uplink packages
python3 aviation/flight_package.py
```

## Safety Notice

Important: For aviation, coordinate with flight-safety engineers. Use this only as a development skeleton. Real RTOS integration needs formal verification and DO-178C style process.
