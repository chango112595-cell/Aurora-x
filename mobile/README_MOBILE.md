# Aurora EdgeOS - Mobile Runtime (3I)

## Overview
Companion mobile app scaffolds for Android & iOS with secure token authentication.

## Files

- `android/` - Gradle stub + REST client example
- `ios/` - Xcode project stub explanation
- `termux/termux_helper.sh` - Termux installer for Android (local runtime)

## Android

Build a companion Android app that authenticates with Aurora REST API on local network using AURORA_API_TOKEN. Android app acts as remote controller and UI, not as the primary runtime (companion model).

## iOS

Build an app that talks to companion device over local network or uses Cloud-assisted mode if device can't see companion.

## Termux (Android)

For local runtime on Android, use Termux:

```bash
./mobile/termux/termux_helper.sh
```
