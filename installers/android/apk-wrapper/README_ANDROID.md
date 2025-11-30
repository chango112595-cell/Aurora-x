1) Install Node, npm, Capacitor or Cordova:
   npm i -g @capacitor/cli
   npm init @capacitor/app

2) Create a simple web app that proxies to Aurora dashboard (or embeds static UI).
   - The actual heavy AI runs on companion device or the container.
   - The APK acts as a UI + remote control.

3) Build and sign:
   npx cap add android
   npx cap open android
   Use Android Studio to build signed APK.

Notes:
- Do NOT attempt to embed the full Python runtime into the APK for production.
- Use Termux for development/testing only.
