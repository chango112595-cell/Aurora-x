# Aurora EdgeOS - Automotive Runtime (3B)

## Overview
CAN bus bridge, safe command queue, UDS wrapper, and ECU suggestion workflow with human-signed approval.

## Key Points

- Use companion computer (Raspberry Pi / NUC) connected to vehicle CAN bus via CAN transceiver.
- Never auto-execute unapproved suggestions.
- Use `ecu_suggestor.py` to review and sign suggestions.
- Support for ISO-TP/UDS provided via udsoncan + python-can.

## Files

- `can_bridge.py` - CAN bridge + safe suggestion queue
- `uds_service.py` - UDS helper (reads only unless signed)
- `ecu_suggestor.py` - Suggestion/approval workflow (human approval required)
- `install-automotive.sh` - Installer + dependencies
- `Dockerfile` - Automotive Docker runtime

## Installation

```bash
./automotive/install-automotive.sh
```

## Usage

```bash
# Start CAN bridge (simulates if python-can not available)
python3 automotive/can_bridge.py

# Create a suggestion
python3 -c "from automotive.can_bridge import store_suggestion; store_suggestion({'test':1})"

# Review and approve suggestions
python3 automotive/ecu_suggestor.py
```

## Safety Notice

For safety-critical systems (ECUs), the code must not auto-flash or bypass certified update chains. This uses a companion-computer pattern: Aurora prepares signed "suggestion packages"; humans must review and sign before any ECU/firmware changes.
