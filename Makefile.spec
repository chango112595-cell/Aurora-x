# Aurora-X Spec → Code Automation
.PHONY: spec spec-test spec-report spec-all spec-notify spec-test-notify spec-all-notify spec-batch clean-runs show-latest

SPEC ?= specs/rich_spec_v2.md
LATEST_RUN := $(shell ls -dt runs/run-* 2>/dev/null | head -1)

# Core spec compilation
spec:
	@echo "🔧 Compiling spec: $(SPEC)"
	@python -m aurora_x.main --spec $(SPEC)

# Run tests for latest generated code
spec-test:
	@echo "🧪 Running tests for latest run..."
	@if [ -z "$(LATEST_RUN)" ]; then echo "❌ No runs found"; exit 1; fi
	@cd $(LATEST_RUN) && PYTHONPATH=$$PWD python -m unittest discover -s tests -v

# Open HTML report in browser
spec-report:
	@echo "📊 Opening latest run report..."
	@if [ -z "$(LATEST_RUN)" ]; then echo "❌ No runs found"; exit 1; fi
	@python -c "import webbrowser; webbrowser.open('file://$(shell pwd)/$(LATEST_RUN)/report.html')"

# Run all steps: compile → test → report
spec-all: spec spec-test spec-report

# Discord notifications
spec-notify:
	@echo "🔧 Compiling spec with Discord notifications: $(SPEC)"
	@python -m aurora_x.main --spec $(SPEC) && python -c "from tools.notify_discord import success; success('✅ Spec compiled: $(SPEC)')" || python -c "from tools.notify_discord import error; error('❌ Spec failed: $(SPEC)')"

spec-test-notify:
	@echo "🧪 Running tests with Discord notifications..."
	@if [ -z "$(LATEST_RUN)" ]; then echo "❌ No runs found"; exit 1; fi
	@cd $(LATEST_RUN) && PYTHONPATH=$$PWD python -m unittest discover -s tests -v && python -c "from tools.notify_discord import success; success('✅ Tests passed')" || python -c "from tools.notify_discord import error; error('❌ Tests failed')"

spec-all-notify: spec-notify spec-test-notify
	@python -c "from tools.notify_discord import info; info('🎉 Aurora-X complete for $(SPEC)')"

# Batch processing
spec-batch:
	@echo "🔧 Compiling all specs..."
	@for spec in specs/*.md; do echo "  Processing: $$spec"; python -m aurora_x.main --spec $$spec; done

# Utilities
clean-runs:
	@echo "🧹 Cleaning old runs (keeping last 10)..."
	@ls -dt runs/run-* | tail -n +11 | xargs rm -rf 2>/dev/null || true

show-latest:
	@if [ -z "$(LATEST_RUN)" ]; then echo "❌ No runs found"; exit 1; fi
	@echo "📁 Latest run: $(LATEST_RUN)"
	@ls -la $(LATEST_RUN)
	@echo ""
	@echo "🧪 To test: make -f Makefile.spec spec-test"
	@echo "📊 To view report: make -f Makefile.spec spec-report"

help:
	@echo "Aurora-X Spec Compilation:"
	@echo "  make -f Makefile.spec spec [SPEC=path/to/spec.md]"
	@echo "  make -f Makefile.spec spec-test"
	@echo "  make -f Makefile.spec spec-report"
	@echo "  make -f Makefile.spec spec-all"
	@echo ""
	@echo "With Discord notifications:"
	@echo "  make -f Makefile.spec spec-all-notify"
	@echo ""
	@echo "Examples:"
	@echo "  make -f Makefile.spec spec SPEC=specs/reverse_string.md"
	@echo "  make -f Makefile.spec spec-all SPEC=specs/rich_spec_v2.md"
