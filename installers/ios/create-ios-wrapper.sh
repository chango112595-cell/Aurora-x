#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$ROOT_DIR/AuroraXWebWrapper/AuroraXWebWrapper"

mkdir -p "$TARGET_DIR"

cat > "$TARGET_DIR/AuroraXWebWrapperApp.swift" <<'SWIFT'
import SwiftUI

@main
struct AuroraXWebWrapperApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
SWIFT

cat > "$TARGET_DIR/ContentView.swift" <<'SWIFT'
import SwiftUI
import WebKit

struct ContentView: View {
    private let baseURL = URL(string: "https://your-aurora-host.example.com")!
    private let apiKey: String? = nil

    var body: some View {
        AuroraWebView(baseURL: baseURL, apiKey: apiKey)
            .edgesIgnoringSafeArea(.all)
    }
}

struct AuroraWebView: UIViewRepresentable {
    let baseURL: URL
    let apiKey: String?

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {
        var request = URLRequest(url: baseURL)
        if let apiKey = apiKey {
            request.setValue(apiKey, forHTTPHeaderField: "Authorization")
        }
        uiView.load(request)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            let html = """
            <html><body style='font-family: -apple-system; text-align: center; padding: 40px;'>
            <h1>Aurora-X is unavailable</h1>
            <p>Please check the server and try again.</p>
            </body></html>
            """
            webView.loadHTMLString(html, baseURL: nil)
        }
    }
}
SWIFT

echo "✅ AuroraXWebWrapper template created at $TARGET_DIR"
