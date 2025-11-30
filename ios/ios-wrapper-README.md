iOS packaging guidance
- iOS does not allow arbitrary background services. Best pattern:
  - Run Aurora core on a companion device (Raspberry Pi, server).
  - Build an iOS app that authenticates & controls Aurora via the secure REST API.
  - If you need local processing on-device, use CoreML / on-device models within app sandbox.
- For enterprise deploy or device management, use Apple MDM and custom enterprise signing.
