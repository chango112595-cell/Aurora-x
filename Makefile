.PHONY: run test clean install open-report compare-latest compare-baseline serve progress progress-auto progress-bump check-progress-ci export-csv install-hook

# Variables
PY ?= python
PORT ?= 8000
OUTDIR ?= runs

install:
        pip install -e .

run:
        python -m aurora_x.main --spec specs/rich_spec.md --seed-bias 0.25

test:
        python -m pytest tests/ -v

dump:
        python -m aurora_x.main --dump-corpus "add(a:int,b:int)->int" --top 5

clean:
        rm -rf runs/*
        rm -rf __pycache__ aurora_x/__pycache__ aurora_x/corpus/__pycache__
        rm -rf .pytest_cache
        rm -rf *.egg-info

open-report:
        @echo "Opening latest synthesis report..."
        @python -c "import webbrowser; webbrowser.open('runs/latest/report.html')"

compare-latest:
        @if [ -z "$(RUN)" ]; then echo "Usage: make compare-latest RUN=runs/run-YYYYMMDD-HHMMSS"; exit 2; fi; \
        if [ ! -d "$(RUN)" ]; then echo "Run directory not found: $(RUN)"; exit 3; fi; \
        if [ ! -L "runs/latest" ] && [ ! -d "runs/latest" ]; then echo "No 'runs/latest' symlink or dir."; exit 4; fi; \
        echo "[compare] latest: runs/latest  vs  target: $(RUN)"; \
        python - <<'PY'
import json, sys, os
from pathlib import Path

target = Path(os.environ.get("RUN"))
latest = Path("runs/latest")
def read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return {}

def edges_of(g):
    e = g.get("edges", {})
    return {(u, v) for u, vs in e.items() for v in vs}

# graph diff
tg = read_json(target/"call_graph.json")
lg = read_json(latest/"call_graph.json")
added = sorted(list(edges_of(tg) - edges_of(lg)))
removed = sorted(list(edges_of(lg) - edges_of(tg)))
gd = {"added": added, "removed": removed, "old_edges": len(edges_of(lg)), "new_edges": len(edges_of(tg))}
Path(target/"graph_diff.json").write_text(json.dumps(gd, indent=2), encoding="utf-8")
print("[compare] graph diff written:", target/"graph_diff.json")

# scores diff
def load_scores(run):
    p = Path(run)/"logs"/"scores.jsonl"
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            o = json.loads(line); fn=o.get("function"); it=int(o.get("iter",-1))
            if fn is None: continue
            prev = out.get(fn)
            if prev is None or it >= prev.get("iter",-1):
                out[fn] = {"passed": int(o.get("passed",0)), "total": int(o.get("total",0)), "iter": it}
        except Exception: pass
    return out

ts = load_scores(target)
ls = load_scores(latest)
allf = sorted(set(ts.keys())|set(ls.keys()))
rows=[]; reg=imp=0
for fn in allf:
    o=ls.get(fn,{"passed":0,"total":0}); n=ts.get(fn,{"passed":0,"total":0})
    dp = int(n["passed"])-int(o["passed"])
    reg += (dp<0); imp += (dp>0)
    rows.append({"function":fn,"old":[o["passed"],o["total"]],"new":[n["passed"],n["total"]],"delta_passed":dp})
sd={"summary":{"regressions":reg,"improvements":imp,"count":len(allf)},"rows":rows}
Path(target/"scores_diff.json").write_text(json.dumps(sd, indent=2), encoding="utf-8")
print("[compare] scores diff written:", target/"scores_diff.json")
PY
        @echo "[compare] open:"
        @echo "  - $(RUN)/graph_diff.json"
        @echo "  - $(RUN)/scores_diff.json"

compare-baseline:
        @if [ -z "$(RUN)" ]; then echo "Error: RUN parameter is missing. Usage: make compare-baseline RUN=runs/run-X BASELINE=runs/run-Y"; exit 2; fi; \
        if [ -z "$(BASELINE)" ]; then echo "Error: BASELINE parameter is missing. Usage: make compare-baseline RUN=runs/run-X BASELINE=runs/run-Y"; exit 2; fi; \
        if [ ! -d "$(RUN)" ]; then echo "Error: RUN directory not found: $(RUN)"; exit 3; fi; \
        if [ ! -d "$(BASELINE)" ]; then echo "Error: BASELINE directory not found: $(BASELINE)"; exit 3; fi; \
        echo "[compare-baseline] baseline: $(BASELINE)  vs  target: $(RUN)"; \
        python - <<'PY'
import json, sys, os
from pathlib import Path

target = Path(os.environ.get("RUN"))
baseline = Path(os.environ.get("BASELINE"))
def read_json(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception:
        return {}

def edges_of(g):
    e = g.get("edges", {})
    return {(u, v) for u, vs in e.items() for v in vs}

# graph diff
tg = read_json(target/"call_graph.json")
bg = read_json(baseline/"call_graph.json")
added = sorted(list(edges_of(tg) - edges_of(bg)))
removed = sorted(list(edges_of(bg) - edges_of(tg)))
gd = {"added": added, "removed": removed, "old_edges": len(edges_of(bg)), "new_edges": len(edges_of(tg))}
Path(target/"graph_diff.json").write_text(json.dumps(gd, indent=2), encoding="utf-8")
print("[compare-baseline] graph diff written:", target/"graph_diff.json")

# scores diff
def load_scores(run):
    p = Path(run)/"logs"/"scores.jsonl"
    out = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        try:
            o = json.loads(line); fn=o.get("function"); it=int(o.get("iter",-1))
            if fn is None: continue
            prev = out.get(fn)
            if prev is None or it >= prev.get("iter",-1):
                out[fn] = {"passed": int(o.get("passed",0)), "total": int(o.get("total",0)), "iter": it}
        except Exception: pass
    return out

ts = load_scores(target)
bs = load_scores(baseline)
allf = sorted(set(ts.keys())|set(bs.keys()))
rows=[]; reg=imp=0
for fn in allf:
    o=bs.get(fn,{"passed":0,"total":0}); n=ts.get(fn,{"passed":0,"total":0})
    dp = int(n["passed"])-int(o["passed"])
    reg += (dp<0); imp += (dp>0)
    rows.append({"function":fn,"old":[o["passed"],o["total"]],"new":[n["passed"],n["total"]],"delta_passed":dp})
sd={"summary":{"regressions":reg,"improvements":imp,"count":len(allf)},"rows":rows}
Path(target/"scores_diff.json").write_text(json.dumps(sd, indent=2), encoding="utf-8")
print("[compare-baseline] scores diff written:", target/"scores_diff.json")
PY
        @echo "[compare-baseline] Comparison complete. Generated files:"
        @echo "  - $(RUN)/graph_diff.json"
        @echo "  - $(RUN)/scores_diff.json"

progress:
        @$(PY) tools/update_progress.py

progress-auto:
        @if [ -z "$(ID)" ]; then echo "Usage: make progress-auto ID=T02"; exit 2; fi; \
        aurorax --update-task $(ID)=auto

progress-bump:
        @if [ -z "$(ID)" ] || [ -z "$(DELTA)" ]; then echo "Usage: make progress-bump ID=T02f DELTA=+5"; exit 2; fi; \
        aurorax --bump $(ID)=$(DELTA)

check-progress-ci:
        @$(PY) tools/check_progress_regression.py

export-csv:
        @$(PY) tools/export_progress_csv.py > progress.csv && echo "[ok] wrote progress.csv"

install-hook:
        @chmod +x tools/precommit.sh && mkdir -p .git/hooks && ln -sf ../../tools/precommit.sh .git/hooks/pre-commit && echo "[ok] pre-commit hook installed"

serve:
        @LATEST=$$(ls -dt $(OUTDIR)/run-* 2>/dev/null | head -n1); \
        if [ -z "$$LATEST" ]; then echo "No runs found. Run 'make run' first."; exit 1; fi; \
        aurorax-serve --run-dir $$LATEST --port $(PORT)

# Task docs sync & drift checks
summary:
        @$(PY) tools/update_summary_md.py

drift:
        @$(PY) tools/check_task_drift.py || true
.PHONY: summary drift

summary:
        @python3 tools/update_summary_md.py

drift:
        @python3 tools/check_task_drift.py || true

# Production commands
.PHONY: prod-check prod-deploy snapshot install-cron

prod-check:
        python -m pytest -q || true
        python tools/ci_gate.py

snapshot:
        ./cron_snapshot.sh

prod-deploy:
        @echo "Deploy hook (placeholder) — wire to your infra if needed"

install-cron:
        ( crontab -l 2>/dev/null | grep -v 'cron_snapshot.sh' ; \
        echo "0 3 * * * cd $$PWD && ./cron_snapshot.sh >> .progress_history/cron.log 2>&1" ) | crontab -
        @echo "Installed daily 3:00 UTC snapshot cron."

# === Aurora-X Spec → Code Automation ===
.PHONY: spec spec-test spec-report spec-all spec-notify spec-test-notify spec-all-notify spec-batch test-all clean-runs show-latest

SPEC ?= specs/rich_spec_v2.md
LATEST_RUN := $(shell ls -dt runs/run-* 2>/dev/null | head -1)

# Core spec compilation
spec:
        @echo "🔧 Compiling spec: $(SPEC)"
        @python -m aurora_x.main --spec $(SPEC)

# Run tests for latest generated code
spec-test:
        @echo "🧪 Running tests for latest run..."
        @if [ -z "$(LATEST_RUN)" ]; then \
                echo "❌ No runs found"; \
                exit 1; \
        fi
        @cd $(LATEST_RUN) && PYTHONPATH=$$PWD python -m unittest discover -s tests -v

# Open HTML report in browser
spec-report:
        @echo "📊 Opening latest run report..."
        @if [ -z "$(LATEST_RUN)" ]; then \
                echo "❌ No runs found"; \
                exit 1; \
        fi
        @python -c "import webbrowser; webbrowser.open('file://$(PWD)/$(LATEST_RUN)/report.html')"

# Run all steps: compile → test → report
spec-all: spec spec-test spec-report

# === Discord Integration ===

# Compile spec and notify Discord
spec-notify:
        @echo "🔧 Compiling spec with Discord notifications: $(SPEC)"
        @python -m aurora_x.main --spec $(SPEC) && \
                python -c "from tools.notify_discord import success; success('✅ Spec compiled successfully: $(SPEC)\nRun: $(shell ls -dt runs/run-* | head -1)')" || \
                python -c "from tools.notify_discord import error; error('❌ Spec compilation failed: $(SPEC)')"

# Test and notify Discord
spec-test-notify:
        @echo "🧪 Running tests with Discord notifications..."
        @if [ -z "$(LATEST_RUN)" ]; then \
                echo "❌ No runs found"; \
                python -c "from tools.notify_discord import error; error('❌ No runs found to test')"; \
                exit 1; \
        fi
        @cd $(LATEST_RUN) && PYTHONPATH=$$PWD python -m unittest discover -s tests -v 2>&1 | tee test.log && \
                python -c "from tools.notify_discord import success; success('✅ All tests passed for $(LATEST_RUN)')" || \
                python -c "from tools.notify_discord import error; error('❌ Tests failed for $(LATEST_RUN)\nCheck test.log for details')"

# Full pipeline with Discord notifications
spec-all-notify: spec-notify spec-test-notify
        @python -c "from tools.notify_discord import info; info('🎉 Aurora-X pipeline complete for $(SPEC)\n✅ Code generated\n✅ Tests passed\n📊 Report: $(LATEST_RUN)/report.html')"

# === Batch Processing ===

# Compile all specs in the specs/ folder
spec-batch:
        @echo "🔧 Compiling all specs..."
        @for spec in specs/*.md; do \
                echo "  Processing: $$spec"; \
                python -m aurora_x.main --spec $$spec; \
        done

# === Utilities ===

# Clean old runs (keep last 10)
clean-runs:
        @echo "🧹 Cleaning old runs (keeping last 10)..."
        @ls -dt runs/run-* | tail -n +11 | xargs rm -rf 2>/dev/null || true

# Show latest run info
show-latest:
        @if [ -z "$(LATEST_RUN)" ]; then \
                echo "❌ No runs found"; \
                exit 1; \
        fi
        @echo "📁 Latest run: $(LATEST_RUN)"
        @echo "📂 Contents:"
        @ls -la $(LATEST_RUN)
        @echo ""
        @echo "🧪 To test: make spec-test"
        @echo "📊 To view report: make spec-report"

# === Aurora-X Ultra v3 — Serve + Spec v3 + Discord ===
.PHONY: serve-v3 open-dashboard open-report spec3 spec3-test spec3-all orchestrator orchestrate-bg orch-status orch-test

SPEC3 ?= specs/check_palindrome.md
DISCORD := tools/discord_cli.py

serve-v3:
        @echo "🚀 Starting FastAPI server on port $${AURORA_PORT:-5001}..."
        @uvicorn aurora_x.serve:app --host 0.0.0.0 --port $${AURORA_PORT:-5001}

# Print the full dashboard URL based on AURORA_PORT and Replit env
open-dashboard:
        @PORT=$${AURORA_PORT:-5001}; \
        HOST=$${REPL_SLUG:+$${REPL_SLUG}.$${REPL_OWNER}.repl.co}; \
        if [ -n "$$HOST" ]; then \
          URL="https://$$HOST/dashboard/spec_runs"; \
        else \
          URL="http://localhost:$$PORT/dashboard/spec_runs"; \
        fi; \
        echo "🌌 Dashboard → $$URL"; \
        URL=$$URL python -c "import webbrowser,os; webbrowser.open(os.environ.get('URL',''))" || true

open-report:
        @latest=$$(ls -dt runs/run-* 2>/dev/null | head -1); \
        if [ -z "$$latest" ]; then echo "No runs found"; exit 1; fi; \
        echo "📖 Opening report: $$latest/report.html"; \
        python -c "import webbrowser,os; webbrowser.open('file://' + os.path.abspath('$$latest/report.html'))"

# === T07 Orchestrator - Continuous spec monitoring ===
orchestrator:
        @echo "🌌 Starting Aurora-X T07 Orchestrator..."
        @echo "📝 Environment config:"
        @echo "  AURORA_ORCH_INTERVAL=$${AURORA_ORCH_INTERVAL:-300} seconds"
        @echo "  AURORA_GIT_AUTO=$${AURORA_GIT_AUTO:-0}"
        @echo "  AURORA_GIT_BRANCH=$${AURORA_GIT_BRANCH:-main}"
        @echo "  AURORA_GIT_URL=$${AURORA_GIT_URL:-Not set}"
        @python aurora_x/orchestrator.py

orchestrate-bg:
        @nohup python aurora_x/orchestrator.py >/tmp/aurora_orch.log 2>&1 &
        @echo "🚀 Daemon started (PID: $$!)"
        @echo "📝 Logs: /tmp/aurora_orch.log"
        @echo "📊 To monitor: tail -f /tmp/aurora_orch.log"
        @echo "⚠️  To stop: pkill -f 'python aurora_x/orchestrator.py'"

orch-test:
        @echo "🧪 Testing orchestrator (5 second interval, no git)..."
        @AURORA_ORCH_INTERVAL=5 AURORA_GIT_AUTO=0 timeout 15 python aurora_x/orchestrator.py || true
        @echo "✅ Orchestrator test completed"

orch-status:
        @echo "🔍 Orchestrator environment status:"
        @echo "  Poll interval: $${AURORA_ORCH_INTERVAL:-300} seconds"
        @echo "  Git auto-commit: $${AURORA_GIT_AUTO:-0}"
        @echo "  Git branch: $${AURORA_GIT_BRANCH:-main}"
        @echo "  Git URL: $${AURORA_GIT_URL:-Not configured}"
        @echo ""
        @echo "📊 Specs being monitored:"
        @ls -la specs/*.md 2>/dev/null | awk '{print "  - " $$9}' || echo "  No specs found"
        @echo ""
        @echo "📝 Recent runs:"
        @tail -3 runs/spec_runs.jsonl 2>/dev/null | while read line; do \
          echo "  $$(echo $$line | python -c "import sys,json; d=json.loads(sys.stdin.read()); print(f'{d[\"timestamp\"]}: {d[\"spec\"]} - {d[\"status\"]}')" 2>/dev/null || echo $$line)"; \
        done || echo "  No recent runs"

spec3:
        @echo "🔧 v3 compile: $(SPEC3)"
        @python tools/spec_compile_v3.py $(SPEC3) || { \
          [ -f $(DISCORD) ] && python $(DISCORD) error "❌ v3 compile failed: $(SPEC3)"; exit 1; }

spec3-test:
        @latest=$$(ls -dt runs/run-* 2>/dev/null | head -1); \
        if [ -z "$$latest" ]; then echo "No runs found"; exit 1; fi; \
        python -m unittest discover -s $$latest/tests -t $$latest || { \
          [ -f $(DISCORD) ] && python $(DISCORD) error "❌ v3 tests failed for $$(basename $$latest)"; exit 1; }

spec3-all:
        @$(MAKE) spec3 SPEC3=$(SPEC3)
        @$(MAKE) spec3-test
        @latest=$$(ls -dt runs/run-* 2>/dev/null | head -1); \
        echo "📊 Report: $$latest/report.html   |   Dashboard: /dashboard/spec_runs"; \
        [ -f $(DISCORD) ] && python $(DISCORD) success "✅ v3 spec passed: $(SPEC3) — $$(basename $$latest)"
