# Aurora EdgeOS - Android TV Runtime (3H)

## Overview
Android TV companion app stub + smart app scaffolds.

## App Stub Ideas

1. Create an Android TV Leanback app
2. Use REST API to communicate with local Aurora agent
3. Display wallboard and status information

## REST Usage

TV apps should call local `http://<local_ip>:9802/status` and use token-based auth.

```kotlin
// Example Kotlin code for Android TV
val url = URL("http://192.168.1.100:9802/status")
val connection = url.openConnection() as HttpURLConnection
connection.setRequestProperty("Authorization", "Bearer $AURORA_TOKEN")
```
