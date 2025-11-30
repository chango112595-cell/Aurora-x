Signing & updater best practices
- Always sign update artifacts with a GPG key or a hardware HSM.
- Store public keys in the device provisioning step.
- Verify signatures and checksums before activating updates.
- Use atomic swap: stage update -> verify -> swap -> restart -> fallback if failed.
- For production, use code signing for binaries and platform-specific signing (MSI/Authenticode, macOS notarize, Android APK signing).
