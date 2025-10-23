# tools/discord_cli.py
# Simple CLI wrapper so Makefile can send Discord messages.
import sys

try:
    from tools.notify_discord import error, info, send_text, success, warning
except Exception:
    # Fallback no-op if notify_discord isn't present
    def _print(msg):
        print(msg)
        return True

    success = error = warning = info = send_text = _print


def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/discord_cli.py <success|error|warning|info|text> <message...>")
        sys.exit(1)
    kind = sys.argv[1].lower()
    msg = " ".join(sys.argv[2:])
    fn = {"success": success, "error": error, "warning": warning, "info": info, "text": send_text}.get(kind, send_text)
    ok = fn(msg)
    print("sent" if ok else "failed")


if __name__ == "__main__":
    main()
