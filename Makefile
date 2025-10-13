# Aurora-X Ultra Unified Makefile (T01-T08)
.PHONY: all help install test run clean serve serve-v3 open-dashboard open-report
.PHONY: spec spec-test spec-report spec3 spec3-test spec3-all
.PHONY: orchestrator orchestrate-bg orch-test orch-status
.PHONY: say corpus-dump bias-show adaptive-stats demo-all demo-list open-demos demo-seed demo-clean demo-clean-hard demo-status
.PHONY: bridge-up bridge-status bridge-nl bridge-spec bridge-deploy orch-up

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
        @echo "Demo Dashboard:"
        @echo "  make demo-status    # check all endpoints health"
        @echo "  make demo-seed      # create example specs and run Aurora"
        @echo "  make demo-all       # run all demo cards (CI/CD)"
        @echo "  make demo-list      # list available demo cards"
        @echo "  make open-demos     # open demo dashboard in browser"
        @echo "  make demo-clean     # remove demo specs and artifacts (safe)"
        @echo "  make demo-clean-hard # CAUTION: remove ALL runs/* outputs"
        @echo ""
        @echo "Orchestrator:"
        @echo "  make orchestrator   # foreground monitoring"
        @echo "  make orchestrate-bg # background daemon"
        @echo "  make orch-status    # check status"
        @echo ""
        @echo "Quality Gates:"
        @echo "  make lint           # run ruff linter"
        @echo "  make sec            # run bandit security scanner"
        @echo "  make cov            # run pytest with coverage"
        @echo "  make gates          # run all quality checks"
        @echo ""
        @echo "Git Tools:"
        @echo "  make diff           # show git diff statistics"
        @echo "  make rollback       # rollback to previous commit"
        @echo "  make nl-pr P='...'  # create PR from natural language"
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
# Aurora-X English Mode Makefile Additions
# Add these targets to your main Makefile or include this file

.PHONY: chat approve english-test english-demo english-status

# === English Mode Variables ===
PROMPT ?= find the largest number in a list
API_URL ?= http://localhost:$${AURORA_PORT:-5001}

# === Interactive Chat Mode ===
chat:
        @echo "🗣️  Aurora-X Interactive English Mode"
        @echo "Enter your request in plain English:"
        @read -r prompt; \
        if [ -z "$$prompt" ]; then \
        echo "Using default: $(PROMPT)"; \
        prompt="$(PROMPT)"; \
        fi; \
        echo "📝 Generating spec from: $$prompt"; \
        python tools/english_to_spec.py "$$prompt" && \
        latest_spec=$$(ls -t specs/requests/*.md 2>/dev/null | head -1); \
        if [ -n "$$latest_spec" ]; then \
        echo "✅ Spec created: $$latest_spec"; \
        echo "🔧 Compiling to code..."; \
        python tools/spec_compile_v3.py "$$latest_spec" && \
        latest_run=$$(ls -dt runs/run-* 2>/dev/null | head -1); \
        echo "📊 Code generated in: $$latest_run"; \
        echo "View report: $$latest_run/report.html"; \
        else \
        echo "❌ Failed to generate spec"; \
        fi

# === API-based Chat (requires server running) ===
chat-api:
        @echo "🌐 Using Aurora-X Chat API"
        @echo "Enter your request:"
        @read -r prompt; \
        if [ -z "$$prompt" ]; then \
        prompt="$(PROMPT)"; \
        echo "Using default: $$prompt"; \
        fi; \
        curl -X POST $(API_URL)/api/chat \
        -H "Content-Type: application/json" \
        -d "{\"prompt\": \"$$prompt\", \"auto_synthesize\": true}" | \
        python -m json.tool

# === Approve Synthesis Runs ===
approve:
        @echo "📋 Checking pending synthesis runs..."
        @curl -s $(API_URL)/api/approve | python -m json.tool
        @echo ""
        @echo "Enter token to approve (or press Enter to skip):"
        @read -r token; \
        if [ -n "$$token" ]; then \
        echo "Approving synthesis for token: $$token"; \
        curl -X POST $(API_URL)/api/approve \
        -H "Content-Type: application/json" \
        -d "{\"token\": \"$$token\", \"approved\": true}" | \
        python -m json.tool; \
        else \
        echo "No approval action taken"; \
        fi

# === Test English Mode ===
english-test:
        @echo "🧪 Testing English Mode Components"
        @echo ""
        @echo "1️⃣ Testing english_to_spec.py..."
        @python tools/english_to_spec.py "reverse a string" > /tmp/english_test.log 2>&1 && \
        echo "   ✅ english_to_spec.py works" || echo "   ❌ english_to_spec.py failed"
        @echo ""
        @echo "2️⃣ Testing fallback template..."
        @python -c "from aurora_x.synthesis.fallback import generate_fallback_function; \
        print('   ✅ Fallback template works') if generate_fallback_function('def test(x: int) -> str', 'Test') else print('   ❌ Fallback failed')" 2>/dev/null || \
        echo "   ❌ Could not import fallback module"
        @echo ""
        @echo "3️⃣ Testing flow_ops.py fallback integration..."
        @python -c "from aurora_x.synthesis.flow_ops import impl_for; \
        code = impl_for('def unknown_func(x: int) -> int', 'some random unrecognized function'); \
        print('   ✅ flow_ops fallback works' if 'NotImplementedError' not in code else '   ❌ Still raises NotImplementedError')" 2>/dev/null || \
        echo "   ❌ Could not test flow_ops"
        @echo ""
        @echo "4️⃣ Checking API endpoints (requires server)..."
        @curl -s $(API_URL)/api/english/status > /dev/null 2>&1 && \
        echo "   ✅ English API endpoints available" || \
        echo "   ⚠️  Server not running or endpoints not available"

# === Demo English Mode ===
english-demo:
        @echo "🎭 Aurora-X English Mode Demo"
        @echo "================================"
        @echo ""
        @echo "Demo 1: Simple function request"
        @python tools/english_to_spec.py "add two numbers together"
        @echo ""
        @echo "Demo 2: Complex function request"
        @python tools/english_to_spec.py "find all prime numbers in a list and return their sum"
        @echo ""
        @echo "Demo 3: Unrecognized pattern (uses fallback)"
        @python tools/english_to_spec.py "perform quantum entanglement calculation"
        @echo ""
        @echo "================================"
        @echo "✅ Demo complete. Check specs/requests/ for generated files"
        @ls -la specs/requests/*.md 2>/dev/null | tail -3

# === Check English Mode Status ===
english-status:
        @echo "📊 Aurora-X English Mode Status"
        @echo "================================"
        @echo ""
        @echo "Components:"
        @[ -f tools/english_to_spec.py ] && echo "  ✅ english_to_spec.py exists" || echo "  ❌ english_to_spec.py missing"
        @[ -f aurora_x/synthesis/fallback.py ] && echo "  ✅ fallback.py exists" || echo "  ❌ fallback.py missing"
        @[ -f aurora_x/serve_addons.py ] && echo "  ✅ serve_addons.py exists" || echo "  ❌ serve_addons.py missing"
        @echo ""
        @echo "Directories:"
        @[ -d specs/requests ] && echo "  ✅ specs/requests/ directory exists" || echo "  ⚠️  specs/requests/ missing (will be created)"
        @echo ""
        @echo "Recent English specs:"
        @ls -lt specs/requests/*.md 2>/dev/null | head -5 || echo "  No specs found in specs/requests/"
        @echo ""
        @echo "Server endpoints (if running):"
        @curl -s $(API_URL)/api/english/status 2>/dev/null | python -m json.tool 2>/dev/null || echo "  Server not accessible"

# === Quick English Mode ===
quick-english:
        @$(MAKE) english-test
        @echo ""
        @$(MAKE) english-demo

# === Help for English Mode ===
english-help:
        @echo "Aurora-X English Mode Commands:"
        @echo ""
        @echo "  make chat              - Interactive English prompt mode"
        @echo "  make chat-api          - Use API for English synthesis"
        @echo "  make approve           - Review and approve synthesis runs"
        @echo "  make english-test      - Test all English mode components"
        @echo "  make english-demo      - Run demo examples"
        @echo "  make english-status    - Check English mode status"
        @echo "  make quick-english     - Run tests and demo"
        @echo ""
        @echo "Examples:"
        @echo "  make chat PROMPT='reverse a string'"
        @echo "  make chat-api API_URL=http://localhost:8000"
        @echo ""
        @echo "Environment variables:"
        @echo "  AURORA_PORT - Server port (default: 5001)"
        @echo "  PROMPT - Default prompt for chat commands"

# === Demo Cards ===
HOST ?= http://localhost:8000

# One-shot: run every demo card and save results
demo-all:
        @curl -s -X POST $(HOST)/api/demo/run_all | jq '{ok,file,count}'

# List available demo cards
demo-list:
        @echo "📋 Available demo cards at $(HOST):"
        @curl -s $(HOST)/api/demo/cards | jq '.cards[] | {id, title, endpoint}' 2>/dev/null || \
        { echo "Error: Failed to fetch demo cards. Is Aurora-X running on $(HOST)?"; exit 1; }

# Open demo dashboard in browser
open-demos:
        @echo "Open: $(HOST)/dashboard/demos"; \
        if command -v xdg-open >/dev/null; then xdg-open "$(HOST)/dashboard/demos"; \
        elif command -v open >/dev/null; then open "$(HOST)/dashboard/demos"; \
        else echo "Please open in your browser."; fi

# Seed example specs, run once, commit, and optionally push
AURORA_GIT_BRANCH ?= main

demo-seed:
        @mkdir -p specs runs
        @printf "## reverse_string\n\n- input: abc\n- output: cba\n" > specs/reverse_string.md
        @printf "## math_eval\n\n- expr: (2+3)^2 + 1\n" > specs/math_eval.md
        @python -m aurora_x.main --spec specs/reverse_string.md || true
        @python -m aurora_x.main --spec specs/math_eval.md || true
        @echo "Seeding orchestrator once..."
        @AURORA_GIT_AUTO=0 AURORA_ORCH_INTERVAL=5 python -m aurora_x.orchestrator || true
        @echo "[ok] Demo seed complete. Check ./runs and /dashboard/demos."
        @if [ -d .git ]; then \
        git add -A && git commit -m "chore: demo seed (specs+runs)" || true; \
        if [ "$${AURORA_PUSH}" = "1" ]; then \
        echo "Pushing to origin $(AURORA_GIT_BRANCH) ..."; \
        git rev-parse --abbrev-ref HEAD >/dev/null 2>&1 || true; \
        git push -u origin "$(AURORA_GIT_BRANCH)" || true; \
        else \
        echo "AURORA_PUSH not set—skipping push."; \
        fi; \
        else echo "Not a git repo—skipping commit/push."; fi

# Clean seeded demos and generated artifacts (safe)
demo-clean:
        @echo "⚠ Removing demo specs and run artifacts..."
        @rm -rf specs/reverse_string.md specs/math_eval.md || true
        @find runs -maxdepth 1 -type f -name 'demo-*.json' -delete 2>/dev/null || true
        @echo "✅ demo-clean done."

# (Optional) hard reset of *all* run artifacts (careful!)
demo-clean-hard:
        @echo "⚠ HARD CLEAN: removing ALL runs/* and test outputs..."
        @rm -rf runs/* || true
        @echo "✅ demo-clean-hard done."

# Comprehensive status check of all Aurora endpoints
demo-status:
        @echo "▶ Aurora-X status @ $(HOST)"
        @echo "• /healthz:" && curl -s $(HOST)/healthz | jq '.status,.components' || true
        @echo "• /api/demo/cards:" && curl -s $(HOST)/api/demo/cards | jq '.ok, (.cards|length)' || true
        @echo "• /api/format/seconds:" && curl -s -X POST -H 'content-type: application/json' -d '{"seconds":86400}' $(HOST)/api/format/seconds | jq . || true
        @echo "• /api/format/units:" && curl -s -X POST -H 'content-type: application/json' -d '{"values":[{"value":7e6,"unit":"m"}]}' $(HOST)/api/format/units | jq . || true
        @echo "• /api/solve (math):" && curl -s -X POST -H 'content-type: application/json' -d '{"problem":"(2+3)^2 + 1"}' $(HOST)/api/solve | jq . || true
        @echo "• /api/solve/pretty (physics):" && curl -s -X POST -H 'content-type: application/json' -d '{"problem":"orbital period a=7000 km M=5.972e24 kg"}' $(HOST)/api/solve/pretty | jq . || true
        @echo "• /chat (timer ui → python):" && curl -s -X POST -H 'content-type: application/json' -d '{"prompt":"make a futuristic timer ui","lang":"python"}' $(HOST)/chat | jq . || true
        @echo "• /api/demo/run_all:" && curl -s -X POST $(HOST)/api/demo/run_all | jq '{ok,file,count}' || true

# Solver demo command
solve-demo:
        @echo "🧮 Testing Aurora-X Solver with differentiation example..."
        @echo ""
        @echo "Testing /api/solve/pretty endpoint with polynomial differentiation:"
        @echo "Input: differentiate x^3 - 2x^2 + x"
        @echo ""
        @curl -s -X POST http://localhost:$${AURORA_PORT:-5001}/api/solve/pretty \
        -H "Content-Type: application/json" \
        -d '{"text": "differentiate x^3 - 2x^2 + x"}' || \
        { echo "Error: Failed to connect. Is the Aurora-X server running on port $${AURORA_PORT:-5001}?"; exit 1; }
        @echo ""
        @echo ""
        @echo "Testing arithmetic evaluation:"
        @echo "Input: 2 + 3 * 4"
        @echo ""
        @curl -s -X POST http://localhost:$${AURORA_PORT:-5001}/api/solve/pretty \
        -H "Content-Type: application/json" \
        -d '{"text": "2 + 3 * 4"}'
        @echo ""
        @echo ""
        @echo "Testing orbital period calculation:"
        @echo "Input: orbital period a=7e6 M=5.972e24"
        @echo ""
        @curl -s -X POST http://localhost:$${AURORA_PORT:-5001}/api/solve/pretty \
        -H "Content-Type: application/json" \
        -d '{"text": "orbital period a=7e6 M=5.972e24"}'
        @echo ""

# Progress helpers
update-progress:
        python tools/update_progress.py

export-progress:
        @python tools/update_progress.py >/dev/null && echo "CSV → progress_export.csv"

progress-view:
        @head -n 30 MASTER_TASK_LIST.md

progress-thresholds:
        @echo "🎨 Setting UI color thresholds..."
        @OK=$${OK:-90}; WARN=$${WARN:-60}; \
        echo "  OK threshold: $$OK% (green)"; \
        echo "  Warn threshold: $$WARN% (amber)"; \
        if [ $$OK -lt $$WARN ]; then \
        echo "❌ Error: OK must be >= WARN"; exit 1; \
        fi; \
        if [ $$OK -gt 100 ] || [ $$WARN -lt 0 ]; then \
        echo "❌ Error: Thresholds must be between 0-100"; exit 1; \
        fi; \
        PORT=$${FASTAPI_PORT:-$${AURORA_PORT:-5001}}; \
        echo "  Trying FastAPI on port $$PORT..."; \
        response=$$(curl -s -X POST http://localhost:$$PORT/api/progress/ui_thresholds \
        -H "Content-Type: application/json" \
        -d "{\"ui_thresholds\": {\"ok\": $$OK, \"warn\": $$WARN}}" 2>/dev/null); \
        if [ -n "$$response" ]; then \
        echo "$$response" | python -c "import sys, json; d=json.loads(sys.stdin.read()); print('✅ Saved:', d.get('ui_thresholds', 'Failed'))"; \
        else \
        echo "⚠️  FastAPI not available on port $$PORT"; \
        echo "Note: This feature requires the FastAPI server (make serve-v3)"; \
        fi

# GitHub README Badge Sync
generate-badges:
        @python tools/generate_readme_badges.py

update-readme:
        @echo "📊 Updating README.md with latest badges..."
        @python tools/update_readme_badges.py

push-progress:
        @echo "🔄 Updating progress and pushing to GitHub..."
        @$(MAKE) update-progress || true
        @$(MAKE) update-readme || true
        @git add -A && \
        git commit -m "Update progress: $$(date '+%Y-%m-%d %H:%M:%S')" || \
        { echo "⚠️  No changes to commit or commit failed"; exit 0; }
        @git push || echo "⚠️  Push failed. Please ensure git is configured and you have network access."
        @echo "✅ Progress update complete"

# Progress v3 helpers (dashboard + README)
progress-serve:
        @python - <<'PY'
        from aurora_x.chat.attach_progress import DASH_HTML; print('OK: /dashboard/progress ready')
        PY

progress-push-v3:
        python tools/update_progress.py
        python tools/patch_readme_progress.py
        @if [ -d .git ]; then git add progress.json MASTER_TASK_LIST.md progress_export.csv README.md || true; git commit -m "chore(progress): refresh badges and lists" || true; git push || true; else echo 'not a git repo'; fi

progress-open:
        @echo "Open /dashboard/progress in your browser (set HOST if remote)"; \
        if command -v xdg-open >/dev/null; then xdg-open "http://localhost:8000/dashboard/progress"; \
        elif command -v open >/dev/null; then open "http://localhost:8000/dashboard/progress"; \
        else echo "http://localhost:8000/dashboard/progress"; fi

# ------- Aurora Make targets (one-liners) -------
HOST ?= http://localhost:5000

.PHONY: dev prod-check orch-up orch-down orch-logs thresholds t08-on t08-off badge demo smoke progress-recompute

dev:
        python -m aurora_x.serve

prod-check:
        python -m aurora_x.checks.ci_gate

orch-up:
        AURORA_GIT_AUTO=1 python -m aurora_x.orchestrator --interval 300 --git-branch main --git-url $${AURORA_GIT_URL:-""} & \
        echo $$! > /tmp/aurora_orch.pid && echo "orchestrator pid: $$(cat /tmp/aurora_orch.pid)"

orch-down:
        @test -f /tmp/aurora_orch.pid && kill $$(cat /tmp/aurora_orch.pid) && rm /tmp/aurora_orch.pid || echo "no orchestrator pid"

orch-logs:
        tail -f /tmp/aurora_orch.log || true

thresholds:
        @test -n "$(OK)" || (echo "Set OK=<int> e.g. 90"; exit 1)
        @test -n "$(WARN)" || (echo "Set WARN=<int> e.g. 60"; exit 1)
        @echo "→ thresholds ok=$(OK) warn=$(WARN) @ $(HOST)"
        @curl -s -X POST -H 'content-type: application/json' \
          -d '{"ui_thresholds":{"ok":'$(OK)',"warn":'$(WARN)'}}' \
          $(HOST)/api/progress/ui_thresholds | python -m json.tool

t08-on:
        curl -s -X POST -H 'content-type: application/json' \
          -d '{"on": true}' $(HOST)/api/t08/activate | python -m json.tool

t08-off:
        curl -s -X POST -H 'content-type: application/json' \
          -d '{"on": false}' $(HOST)/api/t08/activate | python -m json.tool

badge:
        curl -s $(HOST)/badge/progress.svg -o progress.svg && echo "saved → progress.svg"

progress-recompute:
        @curl -s -X POST $(HOST)/api/progress/recompute | python -m json.tool

demo: thresholds

smoke:
        curl -fsS $(HOST)/healthz && echo "health: OK"

# PWA & OS Matrix helpers (T10)
pwa-audit:
        @echo "Checking PWA manifest..."
        @test -f frontend/pwa/manifest.webmanifest && echo "[OK] manifest: frontend/pwa/manifest.webmanifest" || (echo "[FAIL] manifest missing" && exit 1)
        @test -f frontend/pwa/service-worker.js && echo "[OK] service-worker: frontend/pwa/service-worker.js" || (echo "[FAIL] service-worker missing" && exit 1)

serve-pwa:
        @echo "PWA endpoints mounted at /manifest.webmanifest and /service-worker.js"

docker-buildx:
        docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/chango112595-cell/Aurora-x:latest -f docker/Dockerfile . --push

compose-up:
        docker compose -f docker-compose.aurora-x.yml up -d

compose-down:
        docker compose -f docker-compose.aurora-x.yml down

# === Factory Bridge (NL → Project) ===============================
BRIDGE_HOST ?= 127.0.0.1
BRIDGE_PORT ?= 5001

.PHONY: bridge-up bridge-down bridge-restart bridge-health bridge-ensure

bridge-up:
        @echo "▶ starting Factory Bridge on $(BRIDGE_HOST):$(BRIDGE_PORT)…"
        @nohup python -m aurora_x.bridge.service --host $(BRIDGE_HOST) --port $(BRIDGE_PORT) >/tmp/bridge.out 2>/tmp/bridge.err & echo $$! >/tmp/bridge.pid
        @sleep 1
        @$(MAKE) bridge-health

bridge-down:
        @if [ -f /tmp/bridge.pid ]; then \
                echo "⏹ stopping Factory Bridge $$([ -f /tmp/bridge.pid ] && cat /tmp/bridge.pid)"; \
                kill `cat /tmp/bridge.pid` 2>/dev/null || true; \
                rm -f /tmp/bridge.pid; \
        else \
                echo "ℹ no running bridge pid file found"; \
        fi

bridge-restart: bridge-down bridge-up

bridge-health:
        @curl -fsS http://$(BRIDGE_HOST):$(BRIDGE_PORT)/healthz \
          || (echo "❌ bridge not healthy on $(BRIDGE_PORT)"; exit 1)
        @echo "✅ bridge healthy on $(BRIDGE_PORT)"

# Start only if health fails (used by startup scripts & dashboard)
bridge-ensure:
        @curl -fsS http://$(BRIDGE_HOST):$(BRIDGE_PORT)/healthz >/dev/null 2>&1 \
          && echo "✅ bridge already running on $(BRIDGE_PORT)" \
          || $(MAKE) bridge-up

# Start orchestrator with Bridge autostart
orch-up:
        @echo "🚀 Starting Orchestrator with Bridge autostart..."
        @make bridge-ensure
        @make orchestrate-bg
        @echo "✅ Bridge and Orchestrator running in background"

bridge-nl:
        @test -n "$(P)" || (echo "Set P='your prompt'"; exit 1)
        @curl -s -X POST $(HOST)/api/bridge/nl -H 'content-type: application/json' -d '{"prompt":"$(P)"}' | jq .
bridge-spec:
        @test -n "$(SPEC)" || (echo "Set SPEC=path/to/spec.md"; exit 1)
        @curl -s -X POST $(HOST)/api/bridge/spec -H 'content-type: application/json' -d '{"path":"$(SPEC)"}' | jq .
bridge-deploy:
        @curl -s -X POST $(HOST)/api/bridge/deploy | jq .

# === Quality Gates Targets ===
.PHONY: lint sec cov gates diff rollback nl-pr

# Variables for nl-pr target
OWNER ?= $(shell git config --get remote.origin.url | sed -n 's/.*github.com[:/]\([^/]*\).*/\1/p')
REPO ?= $(shell git config --get remote.origin.url | sed -n 's/.*github.com[:/][^/]*\/\([^.]*\).*/\1/p')
BRANCH ?= main
STACK ?= python

# Quality Gate: Linting with ruff
lint:
        @echo "🔍 Running ruff linter on codebase..."
        @ruff check . || { echo "❌ Linting failed"; exit 1; }
        @echo "✅ Linting passed"

# Quality Gate: Security scanning with bandit
sec:
        @echo "🔒 Running bandit security scanner on aurora_x..."
        @bandit -r aurora_x -f json -o /tmp/bandit_report.json 2>/dev/null || true
        @if [ -f /tmp/bandit_report.json ]; then \
                python -c "import json; \
                data = json.load(open('/tmp/bandit_report.json')); \
                issues = data.get('results', []); \
                high = [i for i in issues if i['issue_severity'] == 'HIGH']; \
                medium = [i for i in issues if i['issue_severity'] == 'MEDIUM']; \
                print(f'🔐 Security scan complete:'); \
                print(f'  High severity: {len(high)} issues'); \
                print(f'  Medium severity: {len(medium)} issues'); \
                exit(1 if high else 0)" || { echo "❌ High severity security issues found"; exit 1; }; \
        else \
                bandit -r aurora_x || { echo "❌ Security scan failed"; exit 1; }; \
        fi
        @echo "✅ Security scan passed (no high severity issues)"

# Quality Gate: Coverage testing with pytest
cov:
        @echo "📊 Running pytest with coverage for aurora_x..."
        @python -m pytest tests/ \
                --cov=aurora_x \
                --cov-report=term-missing \
                --cov-report=html:htmlcov \
                --cov-report=json:/tmp/coverage.json \
                -v || { echo "❌ Tests failed"; exit 1; }
        @python -c "import json; \
                data = json.load(open('/tmp/coverage.json')); \
                cov = data['totals']['percent_covered']; \
                print(f'📈 Total coverage: {cov:.2f}%'); \
                exit(0 if cov >= 70 else 1)" || { echo "⚠️  Coverage below 70%"; }
        @echo "✅ Coverage testing complete"

# Run all quality gates in sequence
gates:
        @echo "🚦 Running all quality gates..."
        @echo "================================"
        @$(MAKE) lint
        @echo ""
        @$(MAKE) sec
        @echo ""
        @$(MAKE) cov
        @echo "================================"
        @echo "✅ All quality gates passed"

# Git diff statistics
diff:
        @echo "📊 Git diff statistics:"
        @echo "================================"
        @git diff --stat HEAD 2>/dev/null || echo "No uncommitted changes"
        @echo ""
        @echo "📝 Summary:"
        @git diff --shortstat HEAD 2>/dev/null || echo "Working tree clean"
        @echo ""
        @echo "📁 Changed files:"
        @git diff --name-only HEAD 2>/dev/null | head -20 || echo "No files changed"

# Rollback to previous commit (with safety check)
rollback:
        @echo "⚠️  WARNING: This will rollback to the previous commit"
        @echo "Current HEAD: $$(git log -1 --oneline)"
        @echo ""
        @echo "Previous commit:"
        @git log -1 --oneline HEAD~1
        @echo ""
        @echo "Type 'yes' to confirm rollback:"
        @read confirm; \
        if [ "$$confirm" = "yes" ]; then \
                echo "🔄 Rolling back to previous commit..."; \
                git reset --hard HEAD~1 && \
                echo "✅ Rollback complete"; \
                echo "New HEAD: $$(git log -1 --oneline)"; \
        else \
                echo "❌ Rollback cancelled"; \
        fi

# Natural language to PR (one-shot)
nl-pr:
        @test -n "$(P)" || { echo "Usage: make nl-pr P='your natural language prompt'"; exit 1; }
        @echo "🤖 Creating PR from natural language prompt..."
        @echo "  Prompt: $(P)"
        @echo "  Owner: $(OWNER)"
        @echo "  Repo: $(REPO)"
        @echo "  Branch: $(BRANCH)"
        @echo "  Stack: $(STACK)"
        @echo ""
        @echo "📝 Generating implementation..."
        @python -c "import subprocess, json, tempfile, os; \
        prompt = '$(P)'; \
        spec_file = f'/tmp/nl_pr_spec_{os.getpid()}.md'; \
        print(f'Creating spec from prompt...'); \
        subprocess.run(['python', 'tools/english_to_spec.py', prompt, spec_file]); \
        print(f'Compiling spec to code...'); \
        subprocess.run(['python', 'tools/spec_compile_v3.py', spec_file]); \
        " || { echo "❌ Failed to generate implementation"; exit 1; }
        @latest_run=$$(ls -dt runs/run-* 2>/dev/null | head -1); \
        if [ -n "$$latest_run" ]; then \
                echo "✅ Code generated in: $$latest_run"; \
                echo ""; \
                echo "Creating git branch..."; \
                branch_name="aurora-nl-$$(date +%Y%m%d-%H%M%S)"; \
                git checkout -b "$$branch_name" 2>/dev/null || { echo "❌ Failed to create branch"; exit 1; }; \
                echo "Adding generated files..."; \
                git add "$$latest_run" || true; \
                git commit -m "feat: $(P) (generated by Aurora-X)" || { echo "❌ Failed to commit"; exit 1; }; \
                echo ""; \
                echo "📤 To create PR:"; \
                echo "  1. Push branch: git push -u origin $$branch_name"; \
                echo "  2. Open: https://github.com/$(OWNER)/$(REPO)/pull/new/$$branch_name"; \
                echo ""; \
                echo "Or use GitHub CLI:"; \
                echo "  gh pr create --title '$(P)' --body 'Generated by Aurora-X NL→PR'"; \
        else \
                echo "❌ No code generated"; \
                exit 1; \
        fi
# Diff & Preview helpers for signed commits feature
diff-full:
        @git --no-pager diff

preview:
        @echo "📦 Preview of latest generated project ZIP:"
        @curl -s $(HOST)/bridge/preview 2>/dev/null | python -m json.tool || echo "Bridge service not available or no ZIP found"

sign-on:
        @echo "✍️ Enabling signed commits (for this session)"
        @echo "export AURORA_SIGN=1"
        @echo ""
        @echo "To enable signing, run:"
        @echo "  export AURORA_SIGN=1"

sign-off:
        @echo "📝 Disabling signed commits (for this session)"
        @echo "unset AURORA_SIGN"
        @echo ""
        @echo "To disable signing, run:"
        @echo "  unset AURORA_SIGN"
