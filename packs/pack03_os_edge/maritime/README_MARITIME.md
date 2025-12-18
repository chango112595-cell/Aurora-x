# Aurora EdgeOS - Maritime Runtime (3D)

## Overview
NMEA2000 / NMEA0183 bridge, AIS ingest, and boat-safety recommendation pipeline.

## Files

- `nmea_bridge.py` - NMEA0183 reader/writer
- `nmea2000_stub.py` - NMEA2000 placeholder (needs specific hardware)
- `ais_ingest.py` - AIS parsing and alerting
- `install-maritime.sh` - Installer

## Installation

```bash
./maritime/install-maritime.sh
```

## Usage

```bash
# Start NMEA bridge
python3 maritime/nmea_bridge.py

# Start AIS ingest (simulation)
python3 maritime/ais_ingest.py
```

## Notes

For NMEA2000 you'll need a CAN-to-NMEA2000 interface (e.g., CAN transceiver with Seatalk/NMEA2000 stack). Use companion computer.
