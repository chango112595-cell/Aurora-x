# Aurora-X iOS Wrapper (Production-Ready Template)

This directory contains a **real SwiftUI wrapper** that loads the Aurora-X web UI
inside a secure `WKWebView`. It supports:

- Configurable base URL (local device, LAN, or reverse proxy)
- Optional API key header injection for protected deployments
- Offline-friendly UI (falls back to a local “Service Unavailable” view)

## 1) Create the wrapper project

```bash
./create-ios-wrapper.sh
```

This will generate:

```
installers/ios/AuroraXWebWrapper/
  AuroraXWebWrapper.xcodeproj (placeholder folder, created by Xcode)
  AuroraXWebWrapper/
    AuroraXWebWrapperApp.swift
    ContentView.swift
```

> Open `AuroraXWebWrapper/` in Xcode and create a new iOS app project,
> then replace the default `ContentView.swift` and `App` file with the generated ones.

## 2) Configure the Aurora endpoint

In `ContentView.swift`, update:

```swift
let baseURL = URL(string: "https://your-aurora-host.example.com")!
```

If you need API key auth, set:

```swift
let apiKey = "YOUR_API_KEY"
```

## 3) Run on device

- Ensure the Aurora server is reachable by the iOS device.
- Enable HTTPS for production deployments (recommended).
- Build and run from Xcode.

## 4) Production notes

- Use TLS and certificate pinning if hosting Aurora on the public internet.
- If deploying internally, use a VPN or private reverse proxy.
- Disable `WKWebView` JavaScript injection unless needed.

This wrapper is ready for production hardening (MDM distribution, enterprise
signing, or TestFlight pipelines).
