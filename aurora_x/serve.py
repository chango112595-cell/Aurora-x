#!/usr/bin/env python3
"""Aurora-X Task Tracker web server with HUD and sidebar."""

from __future__ import annotations
import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse

TEMPLATE_DASH = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aurora-X Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0f0f0f;
            color: #e0e0e0;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        
        /* Sidebar */
        .sidebar {
            width: 280px;
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 1px solid #2a2a3e;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .sidebar-header {
            padding: 24px 20px;
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid #2a2a3e;
        }
        
        .sidebar-title {
            font-size: 24px;
            font-weight: 600;
            background: linear-gradient(90deg, #00ff88, #00aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .sidebar-subtitle {
            color: #8888aa;
            font-size: 14px;
        }
        
        .sidebar-nav {
            flex: 1;
            overflow-y: auto;
            padding: 16px 0;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            color: #b0b0c0;
            text-decoration: none;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .nav-item:hover {
            background: rgba(0,255,136,0.1);
            color: #00ff88;
            padding-left: 24px;
        }
        
        .nav-item.active {
            background: rgba(0,255,136,0.15);
            color: #00ff88;
            border-left: 3px solid #00ff88;
        }
        
        .nav-icon {
            margin-right: 12px;
            font-size: 18px;
        }
        
        /* Main Content */
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* HUD Header */
        .hud-header {
            background: linear-gradient(90deg, #1a1a2e 0%, #0f3460 100%);
            border-bottom: 1px solid #2a2a3e;
            padding: 20px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .hud-stats {
            display: flex;
            gap: 32px;
        }
        
        .stat-item {
            display: flex;
            flex-direction: column;
        }
        
        .stat-label {
            font-size: 12px;
            color: #8888aa;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 4px;
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(90deg, #00ff88, #00aaff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hud-actions {
            display: flex;
            gap: 16px;
        }
        
        .btn {
            padding: 10px 20px;
            border: 1px solid #00ff88;
            background: transparent;
            color: #00ff88;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            font-weight: 500;
        }
        
        .btn:hover {
            background: #00ff88;
            color: #0f0f0f;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,255,136,0.3);
        }
        
        /* Content Area */
        .content-area {
            flex: 1;
            overflow-y: auto;
            padding: 32px;
            background: #0a0a0f;
        }
        
        /* Progress Cards */
        .phase-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .phase-card {
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border: 1px solid #2a2a3e;
            border-radius: 12px;
            padding: 24px;
            transition: all 0.3s ease;
        }
        
        .phase-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,255,136,0.1);
            border-color: #00ff88;
        }
        
        .phase-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }
        
        .phase-title {
            font-size: 18px;
            font-weight: 600;
            color: #ffffff;
        }
        
        .phase-status {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-completed {
            background: rgba(0,255,136,0.2);
            color: #00ff88;
        }
        
        .status-in-progress {
            background: rgba(0,170,255,0.2);
            color: #00aaff;
        }
        
        .status-pending {
            background: rgba(255,170,0,0.2);
            color: #ffaa00;
        }
        
        .progress-bar-container {
            background: #0a0a0f;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 12px;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #00ff88, #00aaff);
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        .progress-text {
            text-align: right;
            font-size: 14px;
            color: #8888aa;
            margin-bottom: 16px;
        }
        
        .task-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .task-item {
            padding: 8px 12px;
            background: rgba(0,0,0,0.3);
            border-radius: 6px;
            font-size: 14px;
            color: #b0b0c0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .task-progress {
            font-size: 12px;
            color: #00ff88;
            font-weight: 600;
        }
        
        /* Animation */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #00ff88;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-left: 8px;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #0a0a0f;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #2a2a3e;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #3a3a4e;
        }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <div class="sidebar-title">AURORA-X</div>
            <div class="sidebar-subtitle">Task Tracker HUD</div>
        </div>
        <nav class="sidebar-nav">
            <a href="/dashboard" class="nav-item active">
                <span class="nav-icon">📊</span>
                <span>Dashboard</span>
            </a>
            <a href="/" class="nav-item">
                <span class="nav-icon">📄</span>
                <span>Report</span>
            </a>
            <a href="/progress.json" class="nav-item">
                <span class="nav-icon">📋</span>
                <span>Progress JSON</span>
            </a>
            <a href="/MASTER_TASK_LIST.md" class="nav-item">
                <span class="nav-icon">📝</span>
                <span>Task List</span>
            </a>
        </nav>
    </div>
    
    <div class="main-content">
        <div class="hud-header">
            <div class="hud-stats">
                <div class="stat-item">
                    <div class="stat-label">Overall Progress</div>
                    <div class="stat-value" id="overall-progress">0%</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Phases</div>
                    <div class="stat-value" id="phase-count">0/0</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Status</div>
                    <div class="stat-value">
                        <span id="status-text">Loading</span>
                        <span class="live-indicator"></span>
                    </div>
                </div>
            </div>
            <div class="hud-actions">
                <button class="btn" onclick="refreshData()">Refresh</button>
                <button class="btn" onclick="window.location.href='/'">View Report</button>
            </div>
        </div>
        
        <div class="content-area">
            <div id="phase-container" class="phase-grid">
                <!-- Phase cards will be dynamically inserted here -->
            </div>
        </div>
    </div>
    
    <script>
        let progressData = null;
        
        async function loadProgress() {
            try {
                const response = await fetch('/progress.json');
                progressData = await response.json();
                updateDashboard();
            } catch (error) {
                console.error('Failed to load progress data:', error);
            }
        }
        
        function updateDashboard() {
            if (!progressData) return;
            
            // Calculate overall progress
            let totalProgress = 0;
            let completedPhases = 0;
            
            progressData.phases.forEach(phase => {
                totalProgress += phase.progress;
                if (phase.status === 'completed') completedPhases++;
            });
            
            const overallProgress = (totalProgress / progressData.phases.length).toFixed(1);
            
            // Update header stats
            document.getElementById('overall-progress').textContent = overallProgress + '%';
            document.getElementById('phase-count').textContent = completedPhases + '/' + progressData.phases.length;
            document.getElementById('status-text').textContent = 
                completedPhases === progressData.phases.length ? 'Complete' : 'Active';
            
            // Render phase cards
            const container = document.getElementById('phase-container');
            container.innerHTML = '';
            
            progressData.phases.forEach(phase => {
                const card = createPhaseCard(phase);
                container.appendChild(card);
            });
        }
        
        function createPhaseCard(phase) {
            const card = document.createElement('div');
            card.className = 'phase-card';
            
            const statusClass = phase.status.replace('_', '-');
            const statusText = phase.status.replace('_', ' ');
            
            let tasksHtml = '';
            if (phase.tasks && phase.tasks.length > 0) {
                const visibleTasks = phase.tasks.slice(0, 3);
                visibleTasks.forEach(task => {
                    tasksHtml += `
                        <div class="task-item">
                            <span>${task.name}</span>
                            <span class="task-progress">${task.progress}%</span>
                        </div>
                    `;
                });
                
                if (phase.tasks.length > 3) {
                    tasksHtml += `
                        <div class="task-item" style="opacity: 0.6;">
                            <span>+${phase.tasks.length - 3} more tasks...</span>
                        </div>
                    `;
                }
            }
            
            card.innerHTML = `
                <div class="phase-header">
                    <h3 class="phase-title">${phase.id}: ${phase.name}</h3>
                    <span class="phase-status status-${statusClass}">${statusText}</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar" style="width: ${phase.progress}%"></div>
                </div>
                <div class="progress-text">${phase.progress}% Complete</div>
                <div class="task-list">
                    ${tasksHtml}
                </div>
            `;
            
            return card;
        }
        
        function refreshData() {
            loadProgress();
        }
        
        // Initial load
        loadProgress();
        
        // Auto-refresh every 5 seconds
        setInterval(loadProgress, 5000);
    </script>
</body>
</html>
"""


class AuroraHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for Aurora-X Task Tracker."""
    
    def __init__(self, *args, run_dir: Path, project_root: Path, **kwargs):
        self.run_dir = run_dir
        self.project_root = project_root
        super().__init__(*args, **kwargs)
    
    def _ok(self, content: bytes, content_type: str = "text/html") -> None:
        """Send response with CORS headers."""
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(content)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path == "/":
            # Serve report.html
            report_path = self.run_dir / "report.html"
            if report_path.exists():
                content = report_path.read_bytes()
                self._ok(content, "text/html")
            else:
                self._ok(b"<h1>No report.html found</h1>", "text/html")
        
        elif path == "/dashboard":
            # Serve dashboard HTML
            self._ok(TEMPLATE_DASH.encode("utf-8"), "text/html")
        
        elif path == "/progress.json":
            # Serve progress.json file
            progress_path = self.project_root / "progress.json"
            if progress_path.exists():
                content = progress_path.read_bytes()
                self._ok(content, "application/json")
            else:
                self._ok(b'{"phases": []}', "application/json")
        
        elif path == "/MASTER_TASK_LIST.md":
            # Serve MASTER_TASK_LIST.md file
            task_list_path = self.project_root / "MASTER_TASK_LIST.md"
            if task_list_path.exists():
                content = task_list_path.read_bytes()
                self._ok(content, "text/markdown")
            else:
                self._ok(b"# No task list available", "text/markdown")
        
        else:
            # Try to serve static files from run_dir
            file_path = self.run_dir / path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                content = file_path.read_bytes()
                # Determine content type
                if path.endswith(".html"):
                    content_type = "text/html"
                elif path.endswith(".json"):
                    content_type = "application/json"
                elif path.endswith(".md"):
                    content_type = "text/markdown"
                elif path.endswith(".txt"):
                    content_type = "text/plain"
                else:
                    content_type = "application/octet-stream"
                self._ok(content, content_type)
            else:
                self.send_error(404, "File not found")
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        if path == "/_aurora/update":
            # Handle progress updates
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                updates = data.get('updates', {})
                
                # Update progress.json with the provided updates
                progress_path = self.project_root / "progress.json"
                if progress_path.exists():
                    progress = json.loads(progress_path.read_text())
                    
                    # Apply updates to progress data
                    for task_id, value in updates.items():
                        # Find and update the task/subtask with the given ID
                        for phase in progress['phases']:
                            if phase['id'] == task_id:
                                phase['progress'] = value
                                continue
                            
                            for task in phase.get('tasks', []):
                                if task['id'] == task_id:
                                    task['progress'] = value
                                    break
                                
                                for subtask in task.get('subtasks', []):
                                    if subtask['id'] == task_id:
                                        subtask['progress'] = value
                                        break
                    
                    # Save updated progress
                    progress_path.write_text(json.dumps(progress, indent=2))
                    
                    # Regenerate MASTER_TASK_LIST.md
                    regenerate_master_task_list(self.project_root, progress)
                    
                    response = {"status": "success", "message": "Progress updated"}
                else:
                    response = {"status": "error", "message": "progress.json not found"}
                
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
                
            except Exception as e:
                response = {"status": "error", "message": str(e)}
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
        
        elif self.path == "/api/seed_bias/history":
            # Serve seed bias history from adaptive scheduler
            try:
                # Get global scheduler if available
                from aurora_x.main import _global_adaptive_scheduler
                if _global_adaptive_scheduler:
                    response = {"history": _global_adaptive_scheduler.history}
                else:
                    response = {"history": []}
                
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
                
            except Exception as e:
                response = {"history": []}
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
        
        elif self.path == "/api/adaptive_stats":
            # Serve adaptive scheduler statistics
            try:
                from aurora_x.main import _global_adaptive_scheduler
                if _global_adaptive_scheduler:
                    response = {
                        "summary": _global_adaptive_scheduler.summary(),
                        "iteration": _global_adaptive_scheduler.iteration
                    }
                else:
                    response = {"summary": {}, "iteration": 0}
                
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
                
            except Exception as e:
                response = {"summary": {}, "iteration": 0}
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
        
        elif self.path == "/api/seed_bias":
            # Serve seed bias summary and top reasons
            try:
                from aurora_x.learn import get_seed_store
                seed_store = get_seed_store()
                summary = seed_store.get_summary()
                
                response = {
                    "summary": {
                        "total_seeds": summary["total_seeds"],
                        "avg_bias": round(summary["avg_bias"], 4),
                        "max_bias": round(summary["max_bias"], 4),
                        "min_bias": round(summary["min_bias"], 4),
                        "total_updates": summary["total_updates"],
                        "config": summary["config"]
                    },
                    "top_biases": [
                        {"seed_key": key, "bias": round(bias, 4)}
                        for key, bias in summary.get("top_biases", [])
                    ]
                }
                
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
                
            except Exception as e:
                response = {"status": "error", "message": str(e)}
                self._ok(json.dumps(response).encode('utf-8'), "application/json")
        
        else:
            self.send_error(404, "Endpoint not found")
    
    def log_message(self, format, *args):
        """Override to reduce verbosity."""
        pass


def regenerate_master_task_list(project_root: Path, progress: Dict[str, Any]) -> None:
    """Regenerate MASTER_TASK_LIST.md from progress data."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate overall progress
    total_progress = sum(phase['progress'] for phase in progress['phases']) / len(progress['phases'])
    
    # Build markdown content
    lines = [
        "# 🎯 Aurora-X Task Tracker - MASTER_TASK_LIST",
        "",
        f"*Generated: {now}*",
        "",
        "## 📊 Project Summary",
        "",
        f"**Overall Progress:** 🟡 {total_progress:.1f}%",
        "",
        "## 📈 Phase Progress",
        "",
        "| Phase | Name | Status | Progress |",
        "|-------|------|--------|----------|"
    ]
    
    for phase in progress['phases']:
        status_emoji = "✅" if phase['status'] == 'completed' else "🚀" if phase['status'] == 'in_progress' else "⏳"
        status_text = phase['status'].replace('_', ' ')
        lines.append(f"| {phase['id']} | {phase['name']} | {status_emoji} {status_text} | {phase['progress']:.1f}% |")
    
    lines.extend([
        "",
        "## 📋 Detailed Breakdown",
        ""
    ])
    
    # Add detailed breakdown for each phase
    for phase in progress['phases']:
        status_emoji = "✅" if phase['status'] == 'completed' else "🚀" if phase['status'] == 'in_progress' else "⏳"
        lines.append(f"### {status_emoji} {phase['id']}: {phase['name']} ({phase['progress']:.1f}%)")
        lines.append("")
        
        if phase.get('tasks'):
            lines.append("| Task | Name | Status | Progress | Owner | Priority | Tags |")
            lines.append("|------|------|--------|----------|-------|----------|------|")
            
            for task in phase['tasks']:
                status_emoji = "✅" if task['status'] == 'completed' else "🚀" if task['status'] == 'in_progress' else "⏳"
                status_text = task['status'].replace('_', ' ')
                owner = task.get('owner', '-')
                priority = task.get('priority', '-')
                tags = ', '.join(task.get('tags', [])) if task.get('tags') else '-'
                lines.append(f"| {task['id']} | {task['name']} | {status_emoji} {status_text} | {task['progress']:.1f}% | {owner} | {priority} | {tags} |")
            
            lines.append("")
    
    lines.extend([
        "---",
        "",
        "## 🔄 Update Instructions",
        "",
        "1. Edit `progress.json` with your updates",
        "2. Run `python tools/update_progress.py` to validate and regenerate this file",
        "3. Check for any validation errors or gating violations",
        "4. Commit both files together",
        ""
    ])
    
    # Write to file
    task_list_path = project_root / "MASTER_TASK_LIST.md"
    task_list_path.write_text('\n'.join(lines))


def _watch(project_root: Path) -> None:
    """Monitor progress.json for changes."""
    progress_path = project_root / "progress.json"
    last_modified = 0
    
    while True:
        try:
            if progress_path.exists():
                current_modified = progress_path.stat().st_mtime
                if current_modified > last_modified:
                    last_modified = current_modified
                    print(f"[WATCH] progress.json updated at {datetime.fromtimestamp(current_modified)}")
        except Exception as e:
            print(f"[WATCH] Error: {e}")
        
        time.sleep(2)


def main():
    """Main entry point for the web server."""
    parser = argparse.ArgumentParser(description="Aurora-X Task Tracker Web Server")
    parser.add_argument("--run-dir", type=str, default="./runs/latest",
                      help="Directory containing run artifacts (default: ./runs/latest)")
    parser.add_argument("--port", type=int, default=8080,
                      help="Port to serve on (default: 8080)")
    
    args = parser.parse_args()
    
    run_dir = Path(args.run_dir).resolve()
    project_root = Path.cwd()
    
    # Start file watcher thread
    watcher_thread = threading.Thread(target=_watch, args=(project_root,), daemon=True)
    watcher_thread.start()
    
    # Create custom handler factory
    def handler_factory(*handler_args, **handler_kwargs):
        return AuroraHandler(*handler_args, run_dir=run_dir, project_root=project_root, **handler_kwargs)
    
    # Create and start HTTP server
    server_address = ('0.0.0.0', args.port)
    httpd = HTTPServer(server_address, handler_factory)
    
    print(f"[AURORA-X] Serving on http://0.0.0.0:{args.port}")
    print(f"[AURORA-X] Run directory: {run_dir}")
    print(f"[AURORA-X] Project root: {project_root}")
    print(f"[AURORA-X] Dashboard: http://0.0.0.0:{args.port}/dashboard")
    print(f"[AURORA-X] Report: http://0.0.0.0:{args.port}/")
    print("[AURORA-X] Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[AURORA-X] Shutting down server...")
        httpd.shutdown()
        sys.exit(0)


if __name__ == "__main__":
    main()