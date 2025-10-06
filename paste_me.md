# Aurora-X Ultra: Autonomous Code Synthesis Engine

## 🚀 Project Overview

Aurora-X Ultra is a Python-based autonomous code synthesis engine with offline-first architecture. It features corpus recording with JSONL/SQLite persistence, learning capabilities with auto-tuning seed bias, comprehensive HTML reports with run tracking and regression detection, baseline comparisons, and a live Task Tracker system with floating HUD.

## ✨ Key Features

### Core Engine
- **Autonomous Code Synthesis**: Generates Python functions from natural language descriptions
- **Offline-First Architecture**: No external dependencies, runs completely offline
- **Multi-Run Synthesis**: Configurable synthesis rounds with performance tracking
- **Automatic Test Generation**: Creates test cases to validate synthesized code

### Learning & Memory System
- **Corpus Recording**: JSONL and SQLite persistence for synthesis results
- **Seed Bias Learning**: Auto-tunes selection based on historical performance
- **Jaccard Similarity**: Intelligent function matching and retrieval
- **Weighted Scoring**: 0.6 signature + 0.4 Jaccard + 0.1 perfect bonus

### Comprehensive Reporting
- **HTML Reports**: Rich visualization with graphs and metrics
- **Regression Detection**: Automatic comparison with baselines
- **Visual Badges**: Red "REGRESSIONS ⚠" or green "No regressions ✓"
- **Graph Visualizations**: Function relationships and performance metrics

### Task Tracker System
- **Live Progress Monitoring**: Floating HUD with real-time updates
- **Multi-Phase Tracking**: Foundation Core (100%), Learning & Memory (91.7%), Adaptive Learning (0%)
- **Web Interface**: Embedded tracker in Aurora reports
- **CLI Integration**: Update tasks via command-line flags

## 📁 Project Structure

```
aurora-x/
├── aurora_x/              # Main synthesis engine
│   ├── main.py            # Core synthesis logic
│   ├── serve.py           # Web server for tracker
│   ├── corpus/            # Corpus storage system
│   │   ├── store.py       # SQLite/JSONL storage
│   │   └── corpus.db      # Learning database
│   ├── learn/             # Learning algorithms
│   │   └── weights.py     # Seed bias weighting
│   └── html/              # Report generation
│       └── report_gen.py  # HTML report builder
│
├── tools/                 # Utility scripts
│   ├── update_progress.py           # Task update tool
│   ├── check_progress_regression.py # CI regression check
│   ├── rollback_history.py         # Snapshot rollback
│   └── export_to_csv.py            # CSV export
│
├── runs/                  # Synthesis output
│   ├── latest/           # Most recent run
│   │   ├── report.html   # Main report with HUD
│   │   ├── scores.json   # Performance metrics
│   │   └── corpus.jsonl  # Learning data
│   └── baselines/        # Baseline comparisons
│
├── progress.json         # Task tracking source of truth
├── MASTER_TASK_LIST.md   # Auto-generated task list
├── Makefile              # Build automation
└── tracker.html          # Quick access to tracker
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- SQLite3
- Make (for automation)

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd aurora-x

# Install dependencies
pip install -r requirements.txt

# Run initial synthesis
make run

# Start task tracker server
make serve PORT=8888

# View progress
make progress
```

## 📊 Task Tracker Usage

### Web Interface
The tracker embeds a floating HUD in the top-right corner of Aurora reports:

1. **Start the server**: `make serve PORT=8888`
2. **Open browser**: http://localhost:8888/
3. **Interact with HUD**: Click to expand, update tasks

### CLI Commands

```bash
# View current progress
make progress

# Update specific task
python -m aurora_x.main --update-task T02f=75

# Auto-calculate progress
python -m aurora_x.main --update-task T02f=auto

# Increment progress
python -m aurora_x.main --update-task T02f=+10

# Bump version and snapshot
make progress-bump
```

### Task ID Reference

| Phase | Task ID | Description | Current |
|-------|---------|-------------|---------|
| **Foundation Core** | | | 100% |
| | T01 | Core synthesis engine | 100% |
| | T01a | Basic function generation | 100% |
| | T01b | Test validation framework | 100% |
| | T01c | Error handling & recovery | 100% |
| **Learning & Memory** | | | 91.7% |
| | T02 | Corpus recording system | 100% |
| | T02a | JSONL persistence | 100% |
| | T02b | SQLite integration | 100% |
| | T02c | Similarity scoring | 100% |
| | T02d | Query optimization | 100% |
| | T02e | Export functionality | 100% |
| | T02f | Import/merge capability | 50% |
| **Adaptive Learning** | | | 0% |
| | T03 | Auto-tuning system | 0% |
| | T03a | Performance metrics | 0% |
| | T03b | Seed bias adjustment | 0% |
| | T03c | Learning curves | 0% |

## 🔧 Makefile Targets

```bash
# Core Operations
make run              # Run synthesis with defaults
make run-heavy        # Extended synthesis (1000 rounds)
make clean           # Clean output directories

# Progress Management  
make progress        # Show current progress
make progress-auto   # Auto-calculate all tasks
make progress-bump   # Create snapshot & bump version

# Reporting & Analysis
make report          # Generate HTML report
make compare-latest  # Compare with previous run
make compare-baseline NAME=v1.0  # Compare with baseline

# CI/CD Integration
make check-progress-ci  # Verify no regressions
make export-csv      # Export progress to CSV

# Development Server
make serve PORT=8888 # Start tracker server
```

## 🎯 Current Progress: 63.9%

### Phase Breakdown
- ✅ **Foundation Core**: 100% Complete
  - Core synthesis engine fully operational
  - Test validation framework working
  - Error handling implemented

- 🚀 **Learning & Memory**: 91.7% Complete  
  - Corpus recording with JSONL/SQLite
  - Similarity scoring algorithms
  - Query optimization done
  - Import/merge capability in progress (50%)

- ⏳ **Adaptive Learning**: 0% Pending
  - Auto-tuning system planned
  - Performance metrics framework
  - Seed bias adjustment algorithm

## 🔍 Key Components

### 1. Synthesis Engine (`aurora_x/main.py`)
- Generates Python functions from descriptions
- Validates with auto-generated tests
- Tracks performance metrics
- Supports multi-round synthesis

### 2. Corpus Storage (`aurora_x/corpus/store.py`)
- SQLite with Write-Ahead Logging
- JSONL export/import
- Jaccard similarity matching
- Offset-based pagination

### 3. Learning System (`aurora_x/learn/weights.py`)
- Seed bias calculation
- Historical performance analysis
- Auto-tuning algorithms
- Weight persistence

### 4. Report Generator (`aurora_x/html/report_gen.py`)
- Interactive HTML reports
- Embedded task tracker HUD
- Performance visualizations
- Regression detection badges

### 5. Web Server (`aurora_x/serve.py`)
- Live progress dashboard
- RESTful API endpoints
- WebSocket support
- Static file serving

## 📈 Regression Detection

Aurora-X automatically detects regressions by comparing:
- Function scores between runs
- Graph structure changes  
- Overall success rates
- Performance metrics

Visual indicators in reports:
- 🔴 **REGRESSIONS ⚠ X** - Functions with score decreases
- 🟢 **No regressions ✓** - All functions stable or improved

## 🚦 CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Run Aurora-X Synthesis
  run: make run
  
- name: Check for Regressions
  run: make check-progress-ci
  
- name: Export Results
  run: make export-csv
  
- name: Upload Artifacts
  uses: actions/upload-artifact@v2
  with:
    name: aurora-reports
    path: runs/latest/
```

## 📝 Environment Variables

```bash
# Corpus Export
export AURORA_EXPORT_ENABLED=true
export AURORA_POST_URL=http://localhost:5000/api/corpus
export AURORA_API_KEY=dev-key-123

# Learning Configuration
export AURORA_LEARNING_RATE=0.1
export AURORA_BIAS_DECAY=0.95

# Server Settings
export AURORA_PORT=8888
export AURORA_HOST=0.0.0.0
```

## 🎮 Interactive Features

### Floating HUD
- **Collapsible Design**: Minimizes to corner icon
- **Real-time Updates**: Progress refreshes automatically
- **Quick Actions**: Update tasks without leaving report
- **Visual Indicators**: Color-coded progress bars

### Dashboard Views
- **Overview**: Total progress and phase status
- **Details**: Task-by-task breakdown
- **History**: Progress over time
- **Graphs**: Performance visualizations

## 🔄 History & Rollback

```bash
# View history
ls history/

# Rollback to snapshot
python tools/rollback_history.py --snapshot 20241006_084500

# Create manual snapshot
cp progress.json history/manual_$(date +%Y%m%d_%H%M%S).json
```

## 📊 Export Formats

### CSV Export
```bash
make export-csv
# Creates: progress_export_YYYYMMDD_HHMMSS.csv
```

### JSONL Corpus
```bash
# Export learning data
sqlite3 aurora_x/corpus/corpus.db ".mode json" "SELECT * FROM corpus" > export.jsonl
```

### HTML Reports
- Self-contained with embedded CSS/JS
- Includes tracker HUD
- Printable format
- Mobile responsive

## 🏗️ Architecture Highlights

1. **Offline-First**: No external API dependencies
2. **Modular Design**: Separate concerns for synthesis, learning, reporting
3. **Event-Driven**: Progress updates trigger regeneration
4. **Stateless Server**: All state in files/database
5. **Progressive Enhancement**: Tracker degrades gracefully

## 🤝 Contributing

Aurora-X is designed for extensibility:

1. **Add New Tasks**: Edit `progress.json`
2. **Custom Reports**: Extend `report_gen.py`
3. **Learning Algorithms**: Modify `weights.py`
4. **Storage Backends**: Implement `ICorpusStore`

## 📜 License

MIT License - See LICENSE file for details

## 🎯 Next Steps

1. Complete import/merge capability (T02f - 50% → 100%)
2. Start Adaptive Learning phase (T03)
3. Implement performance metrics (T03a)
4. Build seed bias adjustment (T03b)
5. Create learning curves visualization (T03c)

## 🔗 Quick Links

- **Tracker**: http://localhost:8888/
- **Latest Report**: `runs/latest/report.html`
- **Progress Data**: `progress.json`
- **Task List**: `MASTER_TASK_LIST.md`

---

**Current Version**: 1.0.0  
**Overall Progress**: 63.9%  
**Last Updated**: October 2025

Built with Python, SQLite, and modern web technologies.  
Optimized for Replit deployment with zero external dependencies.