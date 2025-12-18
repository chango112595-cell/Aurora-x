Android APK wrapper guide (scaffold)
- Approach: create a thin Android app that either:
  1) Runs a local Termux-like runtime via a privileged embedded runtime (complex), OR
  2) Acts as a remote controller to Aurora core running on the local network or companion device (recommended).
- For a direct APK that bundles Aurora core: use Termux + PRoot or Linux on Android techniques (advanced).
- For Play Store distribution, you must follow store policies and obtain proper signing keys.

Recommended: build a companion Android app that talks to aurora REST API (9701) over LAN / mDNS with Bearer token.
