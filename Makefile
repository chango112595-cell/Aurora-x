# Aurora-X Ultra Unified Makefile (T01-T08)
.PHONY: all help install test run clean serve serve-v3 open-dashboard open-report
.PHONY: spec spec-test spec-report spec3 spec3-test spec3-all
.PHONY: orchestrator orchestrate-bg orch-test orch-status
.PHONY: say corpus-dump bias-show adaptive-stats

# === Default Variables ===
SPEC ?= specs/check_palindrome.md
SPEC3 ?= specs/check_palindrome.md
WHAT ?= reverse a string
DISCORD := tools/discord_cli.py
AURORA_PORT ?= 5001

# === Help ===
help:
	@echo "Aurora-X Ultra Commands:"
	@echo ""
	@echo "T08 Natural Language:"
	@echo "  make say WHAT='find the largest number'"
	@echo ""
	@echo "V3 Spec Compilation:"
	@echo "  make spec3-all SPEC3=specs/check_palindrome.md"
	@echo "  make spec3          # compile spec"
	@echo "  make spec3-test     # test latest run"
	@echo ""
	@echo "Server & Dashboard:"
	@echo "  make serve-v3       # start FastAPI (port $(AURORA_PORT))"
	@echo "  make open-dashboard # open dashboard URL"
	@echo "  make open-report    # open latest HTML report"
	@echo ""
	@echo "Orchestrator:"
	@echo "  make orchestrator   # foreground monitoring"
	@echo "  make orchestrate-bg # background daemon"
	@echo "  make orch-status    # check status"
	@echo ""
	@echo "Legacy Commands:"
	@echo "  make run            # run synthesis"
	@echo "  make test           # run unit tests"

# === Installation ===
install:
	pip install -e .

# === Testing ===
test:
	python -m pytest tests/ -v

# === Legacy Run ===
run:
	python -m aurora_x.main --spec specs/rich_spec.md --seed-bias 0.25

# === Clean ===
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf *.egg-info

# === T08: Natural Language → Spec ===
say:
	@echo "🗣  NL → Spec → Code: $(WHAT)"
	@python -m aurora_x.main --nl "$(WHAT)"

# === V3 FastAPI Server ===
serve-v3:
	@echo "🚀 Starting FastAPI server on port $${AURORA_PORT:-5001}..."
	@uvicorn aurora_x.serve:app --host 0.0.0.0 --port $${AURORA_PORT:-5001}

# === Dashboard & Reports ===
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

# === V3 Spec Compilation ===
spec3:
	@echo "🔧 v3 compile: $(SPEC3)"
	@python tools/spec_compile_v3.py $(SPEC3) || { \
	  [ -f $(DISCORD) ] && python $(DISCORD) error "❌ v3 compile failed: $(SPEC3)"; exit 1; }

spec3-test:
	@echo "🧪 Testing latest v3 run..."
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

# === T07 Orchestrator ===
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

# === Corpus & Bias ===
corpus-dump:
	@echo "📚 Querying corpus..."
	@python -m aurora_x.main --dump-corpus "$(SIG)" --top 10

bias-show:
	@echo "🎯 Current seed bias:"
	@python -m aurora_x.main --show-bias --outdir runs

adaptive-stats:
	@echo "📊 Adaptive scheduler stats:"
	@curl -s http://localhost:8080/api/adaptive_stats | python -m json.tool

# === Legacy V2 Spec Commands ===
spec:
	@echo "🔧 Compiling spec: $(SPEC)"
	@python tools/spec_compile.py $(SPEC)

spec-test:
	@echo "🧪 Testing latest run..."
	@latest=$$(ls -dt runs/run-* | head -1); \
	python -m unittest discover -s $$latest/tests -t $$latest

spec-report:
	@echo "📊 Opening latest report..."
	@latest=$$(ls -dt runs/run-* | head -1); \
	open $$latest/report.html 2>/dev/null || xdg-open $$latest/report.html 2>/dev/null || echo "Report: $$latest/report.html"

# === Quick Start Aliases ===
all: help
serve: serve-v3
dashboard: open-dashboard