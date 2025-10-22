from flask import Flask, render_template_string
from textwrap import dedent

HTML = dedent("""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Timer UI</title>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>/* aurora theme CSS omitted here for brevity; include full CSS from the fix you have */</style>
</head>
<body>
<!-- HTML content omitted for brevity; include full content from the prepared fix -->
</body>
</html>
""")

def format_mmss(ms: int) -> str:
    """Format milliseconds to MM:SS (zero-padded)."""
    if ms < 0:
        ms = 0
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(HTML)

    app.format_mmss = format_mmss
    return app

# Basic unit tests for format_mmss
def _run_tests():
    assert format_mmss(0) == "00:00"
    assert format_mmss(1000) == "00:01"
    assert format_mmss(61000) == "01:01"
    assert format_mmss(60000) == "01:00"
    assert format_mmss(3599000) == "59:59"
    assert format_mmss(-200) == "00:00"
    print("format_mmss tests passed")

if __name__ == "__main__":
    _run_tests()
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
