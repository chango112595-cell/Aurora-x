# Aurora EdgeOS - iOS Mobile Runtime (3I)

## Overview
iOS companion pattern (no jailbreaking required).

## Recommended Pattern

Build an app that talks to companion device over local network or uses Cloud-assisted mode if device can't see companion.

## Xcode Project Stub

Create a new iOS project with:
- Minimum iOS: 15.0
- Use URLSession for REST API calls
- Store AURORA_API_TOKEN in Keychain

## Example REST Client

```swift
func fetchStatus() async throws -> StatusResponse {
    let url = URL(string: "http://\(auroraHost):9701/api/status")!
    var request = URLRequest(url: url)
    request.addValue("Bearer \(auroraToken)", forHTTPHeaderField: "Authorization")

    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(StatusResponse.self, from: data)
}
```
