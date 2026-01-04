# Aurora EdgeOS - Android Mobile Runtime (3I)

## Overview
Companion mobile app scaffolds with secure token authentication.

## Recommended Pattern

Build a companion Android app that authenticates with Aurora REST API on local network using AURORA_API_TOKEN.

Android app acts as remote controller and UI, not as the primary runtime (companion model).

## Gradle Stub

Create a new Android project with:
- Minimum SDK: 24 (Android 7.0)
- Use Retrofit or OkHttp for REST API calls
- Store AURORA_API_TOKEN securely in Android Keystore

## Example REST Client

```kotlin
interface AuroraApi {
    @GET("/api/status")
    suspend fun getStatus(): Response<StatusResponse>

    @POST("/api/command")
    suspend fun sendCommand(@Body command: CommandRequest): Response<CommandResponse>
}
```
