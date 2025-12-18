# Aurora EdgeOS - ESP32 IoT Runtime (3E)

## Overview
ESP32 MicroPython/ESP-IDF stubs with OTA update safe flow.

## Build + Flash Steps

### MicroPython
1. Flash MicroPython firmware to ESP32
2. Copy `main.py` to device using ampy or rshell:
   ```bash
   ampy --port /dev/ttyUSB0 put main.py
   ```

### ESP-IDF
```bash
idf.py build
idf.py -p PORT flash
```

## Safety Notice

ESP firmware updates must verify signatures if devices are in the field.
