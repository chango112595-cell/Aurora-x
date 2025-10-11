"""
Flask Timer UI Application - Dark Aurora Theme
A countdown timer with smooth animations and neon glow effects
"""
from flask import Flask
import os


def format_mmss(ms: int) -> str:
    """Convert milliseconds to MM:SS format.
    
    Args:
        ms: Time in milliseconds
        
    Returns:
        Time formatted as MM:SS string
    """
    if ms < 0:
        return "00:00"
    
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    # Cap at 99:59
    if minutes > 99:
        return "99:59"
        
    return f"{minutes:02d}:{seconds:02d}"


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    @app.route("/")
    def index():
        """Serve the timer UI with inline HTML/CSS/JS."""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora Timer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Courier New', monospace;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(ellipse at center, #1a1a2e 0%, #0f0f1e 50%, #000 100%);
            color: #00ffcc;
            overflow: hidden;
        }
        
        .container {
            text-align: center;
            padding: 40px;
            background: rgba(10, 10, 30, 0.8);
            border-radius: 20px;
            box-shadow: 
                0 0 60px rgba(0, 255, 204, 0.3),
                inset 0 0 30px rgba(0, 255, 204, 0.1);
            backdrop-filter: blur(10px);
            position: relative;
            animation: pulse-glow 3s ease-in-out infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 60px rgba(0, 255, 204, 0.3), inset 0 0 30px rgba(0, 255, 204, 0.1); }
            50% { box-shadow: 0 0 80px rgba(0, 255, 204, 0.5), inset 0 0 40px rgba(0, 255, 204, 0.2); }
        }
        
        h1 {
            font-size: 2.5rem;
            margin-bottom: 30px;
            text-shadow: 0 0 20px rgba(0, 255, 204, 0.8);
            animation: text-glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes text-glow {
            from { text-shadow: 0 0 20px rgba(0, 255, 204, 0.8); }
            to { text-shadow: 0 0 30px rgba(0, 255, 204, 1), 0 0 40px rgba(0, 255, 204, 0.5); }
        }
        
        .timer-display {
            font-size: 5rem;
            font-weight: bold;
            margin: 30px 0;
            letter-spacing: 0.1em;
            text-shadow: 
                0 0 30px #00ffcc,
                0 0 60px #00ffcc;
            font-family: 'Courier New', monospace;
        }
        
        .input-group {
            margin: 30px 0;
        }
        
        input[type="number"] {
            padding: 12px 20px;
            font-size: 1.2rem;
            background: rgba(0, 255, 204, 0.1);
            border: 2px solid #00ffcc;
            border-radius: 10px;
            color: #00ffcc;
            width: 150px;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        input[type="number"]:focus {
            outline: none;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.5);
            background: rgba(0, 255, 204, 0.2);
        }
        
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {
            opacity: 1;
            color: #00ffcc;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
        }
        
        button {
            padding: 12px 30px;
            font-size: 1.1rem;
            background: linear-gradient(135deg, rgba(0, 255, 204, 0.2), rgba(0, 255, 204, 0.1));
            border: 2px solid #00ffcc;
            border-radius: 10px;
            color: #00ffcc;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        button:hover {
            background: linear-gradient(135deg, rgba(0, 255, 204, 0.4), rgba(0, 255, 204, 0.2));
            box-shadow: 
                0 0 20px rgba(0, 255, 204, 0.6),
                inset 0 0 10px rgba(0, 255, 204, 0.3);
            transform: translateY(-2px);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .aurora-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            opacity: 0.3;
            background: 
                radial-gradient(ellipse at top left, transparent, rgba(0, 255, 204, 0.2) 50%, transparent),
                radial-gradient(ellipse at bottom right, transparent, rgba(255, 0, 204, 0.2) 50%, transparent);
            animation: aurora-shift 10s ease-in-out infinite;
        }
        
        @keyframes aurora-shift {
            0%, 100% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(5deg) scale(1.1); }
        }
    </style>
</head>
<body>
    <div class="aurora-bg"></div>
    <div class="container">
        <h1>⏱ Aurora Timer</h1>
        <div class="timer-display" id="display">00:00</div>
        <div class="input-group">
            <input type="number" id="secondsInput" min="0" max="5999" placeholder="Seconds" value="60">
        </div>
        <div class="button-group">
            <button id="startBtn">Start</button>
            <button id="pauseBtn">Pause</button>
            <button id="resetBtn">Reset</button>
        </div>
    </div>
    
    <script>
        let timerState = {
            isRunning: false,
            isPaused: false,
            startTime: null,
            pausedTime: 0,
            totalTime: 0,
            animationId: null
        };
        
        const display = document.getElementById('display');
        const secondsInput = document.getElementById('secondsInput');
        const startBtn = document.getElementById('startBtn');
        const pauseBtn = document.getElementById('pauseBtn');
        const resetBtn = document.getElementById('resetBtn');
        
        function formatTime(ms) {
            if (ms < 0) return "00:00";
            const totalSeconds = Math.floor(ms / 1000);
            const minutes = Math.floor(totalSeconds / 60);
            const seconds = totalSeconds % 60;
            return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
        
        function updateTimer(timestamp) {
            if (!timerState.isRunning) return;
            
            const elapsed = timestamp - timerState.startTime + timerState.pausedTime;
            const remaining = Math.max(0, timerState.totalTime - elapsed);
            
            display.textContent = formatTime(remaining);
            
            if (remaining > 0) {
                timerState.animationId = requestAnimationFrame(updateTimer);
            } else {
                // Timer finished
                timerState.isRunning = false;
                display.style.animation = 'text-glow 0.5s ease-in-out 3';
                setTimeout(() => {
                    display.style.animation = '';
                }, 1500);
            }
        }
        
        startBtn.addEventListener('click', () => {
            if (!timerState.isRunning) {
                const seconds = parseInt(secondsInput.value) || 0;
                if (seconds <= 0) return;
                
                timerState.totalTime = seconds * 1000;
                timerState.startTime = performance.now();
                timerState.pausedTime = 0;
                timerState.isRunning = true;
                timerState.isPaused = false;
                
                timerState.animationId = requestAnimationFrame(updateTimer);
            }
        });
        
        pauseBtn.addEventListener('click', () => {
            if (timerState.isRunning) {
                if (!timerState.isPaused) {
                    // Pause
                    timerState.isPaused = true;
                    timerState.isRunning = false;
                    timerState.pausedTime += performance.now() - timerState.startTime;
                    cancelAnimationFrame(timerState.animationId);
                    pauseBtn.textContent = 'Resume';
                } else {
                    // Resume
                    timerState.isPaused = false;
                    timerState.isRunning = true;
                    timerState.startTime = performance.now();
                    pauseBtn.textContent = 'Pause';
                    timerState.animationId = requestAnimationFrame(updateTimer);
                }
            }
        });
        
        resetBtn.addEventListener('click', () => {
            timerState.isRunning = false;
            timerState.isPaused = false;
            timerState.startTime = null;
            timerState.pausedTime = 0;
            timerState.totalTime = 0;
            cancelAnimationFrame(timerState.animationId);
            display.textContent = '00:00';
            pauseBtn.textContent = 'Pause';
        });
    </script>
</body>
</html>'''
    
    @app.route("/health")
    def health():
        """Health check endpoint."""
        return {"status": "healthy", "app": "timer_ui"}, 200
    
    return app


# Unit tests for format_mmss
def test_format_mmss():
    """Test the format_mmss helper function."""
    # Test basic cases
    assert format_mmss(0) == "00:00", "Zero milliseconds should be 00:00"
    assert format_mmss(1000) == "00:01", "1000ms should be 00:01"
    assert format_mmss(60000) == "01:00", "60000ms should be 01:00"
    assert format_mmss(61000) == "01:01", "61000ms should be 01:01"
    
    # Test edge cases
    assert format_mmss(-1000) == "00:00", "Negative values should return 00:00"
    assert format_mmss(5999000) == "99:59", "5999000ms should be 99:59"
    assert format_mmss(10000000) == "99:59", "Values over 99:59 should cap at 99:59"
    
    print("✅ All format_mmss tests passed!")


if __name__ == "__main__":
    # Run tests
    test_format_mmss()
    
    # Start the Flask app
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting Aurora Timer on port {port}")
    print(f"🌟 Open http://localhost:{port} to view the timer")
    app.run(host="0.0.0.0", port=port, debug=False)