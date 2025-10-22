from flask import Flask, render_template_string
from textwrap import dedent
import math

HTML = dedent("""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Timer UI</title>
<meta name="viewport" content="width=device-width,initial-scale=1" />
<style>
  :root{
    --bg1:#0b1020;
    --bg2:#0b1a2b;
    --neon:#6ef0ff;
    --accent:#9b7aff;
    --shadow: 0 6px 24px rgba(107,90,255,0.12);
    --glass: rgba(255,255,255,0.03);
    font-family: Inter, Roboto, system-ui, -apple-system, "Segoe UI", "Helvetica Neue", Arial;
  }
  html,body{height:100%;margin:0;background:radial-gradient(1200px 600px at 10% 10%, rgba(107,90,255,0.06), transparent),
                         radial-gradient(900px 400px at 90% 90%, rgba(110,240,255,0.03), transparent),
                         linear-gradient(180deg,var(--bg1),var(--bg2)); color:#dfefff;}
  .wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
  .card{width:420px;max-width:95%;background:linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius:12px;padding:24px;box-shadow:var(--shadow);backdrop-filter: blur(6px);}
  h1{margin:0 0 8px 0;font-size:18px;color:#e9fbff;text-shadow:0 2px 8px rgba(110,240,255,0.06)}
  .display{font-size:56px;letter-spacing:2px;text-align:center;padding:8px 0;margin:12px 0;color:var(--neon);text-shadow: 0 0 18px rgba(110,240,255,0.14);}
  .controls{display:flex;gap:8px;justify-content:center;margin-top:12px}
  input[type=number]{width:120px;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);
                     background:var(--glass);color:inherit}
  button{padding:8px 14px;border-radius:8px;border:0;background:linear-gradient(90deg,var(--neon),var(--accent));
         color:#04202a;font-weight:600;cursor:pointer;box-shadow:0 6px 20px rgba(107,90,255,0.12)}
  .muted{font-size:12px;color:rgba(223,239,255,0.6);text-align:center;margin-top:8px}
</style>
</head>
<body>
  <div class="wrap">
    <div class="card" role="main">
      <h1>Timer UI — Aurora</h1>
      <div id="time" class="display">00:00</div>

      <div style="display:flex;gap:8px;justify-content:center;align-items:center;">
        <input id="seconds" type="number" min="0" placeholder="seconds" />
      </div>

      <div class="controls">
        <button id="start">Start</button>
        <button id="pause">Pause</button>
        <button id="reset">Reset</button>
      </div>

      <div class="muted">Client-side timer using requestAnimationFrame for smooth updates.</div>
    </div>
  </div>

<script>
(function(){
  const display = document.getElementById('time');
  const input = document.getElementById('seconds');
  const btnStart = document.getElementById('start');
  const btnPause = document.getElementById('pause');
  const btnReset = document.getElementById('reset');

  let totalMs = 0;         // countdown total in ms
  let remainingMs = 0;     // remaining ms when running
  let running = false;
  let lastPerf = 0;
  let rafId = null;

  function msToMMSS(ms) {
    ms = Math.max(0, Math.floor(ms));
    const totalSec = Math.floor(ms / 1000);
    const mm = Math.floor(totalSec / 60);
    const ss = totalSec % 60;
    return String(mm).padStart(2,'0') + ':' + String(ss).padStart(2,'0');
  }

  function render() {
    display.textContent = msToMMSS(remainingMs);
  }

  function tick(now) {
    if (!running) return;
    if (!lastPerf) lastPerf = now;
    const delta = now - lastPerf;
    lastPerf = now;
    remainingMs = Math.max(0, remainingMs - delta);
    render();
    if (remainingMs <= 0) {
      running = false;
      // optional: flash or notify
      return;
    }
    rafId = requestAnimationFrame(tick);
  }

  btnStart.addEventListener('click', () => {
    const seconds = Number(input.value) || 0;
    if (!running) {
      if (remainingMs <= 0) {
        totalMs = Math.max(0, Math.floor(seconds * 1000));
        remainingMs = totalMs;
      }
      running = true;
      lastPerf = 0;
      if (rafId) cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(tick);
    }
  });

  btnPause.addEventListener('click', () => {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
    lastPerf = 0;
  });

  btnReset.addEventListener('click', () => {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
    rafId = null;
    const seconds = Number(input.value) || 0;
    totalMs = Math.max(0, Math.floor(seconds * 1000));
    remainingMs = totalMs;
    render();
  });

  // initialize
  remainingMs = 0;
  render();
})();
</script>
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
    """Create and configure the Flask app serving the timer UI."""
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template_string(HTML)

    # expose helper for tests or interactive use
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
    # Run the Flask app on port 5000 by default
    app = create_app()
    # note: in production use a proper WSGI server
    app.run(host="0.0.0.0", port=5000, debug=True)
