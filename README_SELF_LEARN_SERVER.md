
# Aurora-X Self-Learning Server

The Self-Learning Server is a dedicated, independent service that runs Aurora-X's continuous learning daemon with its own API and monitoring capabilities.

## Features

- **Independent Operation**: Runs on port 5002, separate from main Aurora-X server
- **Dedicated Directories**: Uses `specs_learning/` and `runs_learning/` to avoid conflicts
- **REST API**: Full API for monitoring and control
- **Background Mode**: Can run as a background process

## Quick Start

### Start the Server

```bash
# Foreground mode (for development)
make self-learn-server

# Background mode (for production)
make self-learn-bg
```

### Check Status

```bash
# Via Makefile
make self-learn-status

# Via curl
curl http://0.0.0.0:5002/stats
```

### Stop the Server

```bash
make self-learn-stop
```

## API Endpoints

### `GET /health`
Health check endpoint

**Response:**
```json
{
  "ok": true,
  "service": "self-learning",
  "status": "running",
  "port": 5002,
  "timestamp": 1234567890.0
}
```

### `GET /stats`
Get self-learning statistics

**Response:**
```json
{
  "ok": true,
  "stats": {
    "status": "running",
    "total_runs": 42,
    "successful_runs": 38,
    "failed_runs": 4,
    "started_at": "2025-10-25T04:00:00",
    "last_run_time": "2025-10-25T05:30:00"
  },
  "spec_dir": "specs_learning",
  "output_dir": "runs_learning"
}
```

### `POST /start`
Start the self-learning daemon

**Query Parameters:**
- `sleep_seconds` (int, default: 300) - Seconds between runs
- `max_iters` (int, default: 50) - Max synthesis iterations
- `beam` (int, default: 20) - Beam search width

### `POST /stop`
Stop the self-learning daemon

### `GET /recent-runs?limit=10`
Get recent self-learning runs

## Directory Structure

```
specs_learning/     # Specs for self-learning (independent)
runs_learning/      # Self-learning output runs (independent)
runs/               # Main Aurora-X runs (unchanged)
specs/              # Main Aurora-X specs (unchanged)
```

## Integration with Main Aurora-X

The self-learning server is completely independent:
- Different port (5002 vs 5001)
- Different directories
- Separate processes
- No file conflicts

You can run both simultaneously:
```bash
# Terminal 1: Main Aurora-X
make serve-v3

# Terminal 2: Self-Learning
make self-learn-server
```

## Server Manager Integration

The server manager now monitors all three services:
```bash
make server-status
```

Output:
```
📡 PORT STATUS:
  Port 5000: 🟢 IN USE (Main Web)
  Port 5001: 🟢 IN USE (Bridge)
  Port 5002: 🟢 IN USE (Self-Learning)

🏥 HEALTH CHECKS:
  Main Web Server: 🟢 HEALTHY
  Python Bridge: 🟢 HEALTHY
  Self-Learning Server: 🟢 HEALTHY
```

## Environment Variables

- `SELF_LEARN_PORT`: Port for self-learning server (default: 5002)

## Logs

When running in background mode, logs are stored at:
```
/tmp/self_learn.log
```

View logs:
```bash
tail -f /tmp/self_learn.log
```
