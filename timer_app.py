# pylint: disable=redefined-outer-name
from flask import Flask, render_template_string
from textwrap import dedent

HTML = dedent(
    """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Timer UI</title>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
body {
    background: #232946;
    color: #fffffe;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
}
.timer-container {
    background: #121629;
    border-radius: 16px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    padding: 32px 48px;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.timer-display {
    font-size: 4rem;
    font-weight: bold;
    letter-spacing: 0.1em;
    margin-bottom: 32px;
}
.timer-buttons {
    display: flex;
    gap: 16px;
}
.timer-btn {
    background: #eebbc3;
    color: #232946;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 1.2rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}
.timer-btn:hover {
    background: #f6c7cf;
}
</style>
</head>
<body>
<div class="timer-container">
    <div class="timer-display" id="timer">00:00</div>
    <div class="timer-buttons">
        <button class="timer-btn" id="startBtn">Start</button>
        <button class="timer-btn" id="stopBtn">Stop</button>
        <button class="timer-btn" id="resetBtn">Reset</button>
    </div>
</div>
<script>
let timerInterval = null;
let timeMs = 0;
let running = false;

function formatMMSS(ms) {
    ms = Math.max(0, ms);
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function updateDisplay() {
    document.getElementById('timer').textContent = formatMMSS(timeMs);
}

function startTimer() {
    if (running) return;
    running = true;
    timerInterval = setInterval(() => {
        timeMs += 1000;
        updateDisplay();
    }, 1000);
}

function stopTimer() {
    running = false;
    clearInterval(timerInterval);
}

function resetTimer() {
    stopTimer();
    timeMs = 0;
    updateDisplay();
}

document.getElementById('startBtn').onclick = startTimer;
document.getElementById('stopBtn').onclick = stopTimer;
document.getElementById('resetBtn').onclick = resetTimer;

updateDisplay();
</script>
</body>
</html>
"""
)


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
