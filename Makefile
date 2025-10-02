.PHONY: run test lint fmt clean open-report

run:
	python -m aurora_x.main --spec-file ./specs/rich_spec.md --outdir runs

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff format .

clean:
	rm -rf runs/* __pycache__ .pytest_cache

open-report:
	@echo "Opening latest report..."
	@ls -t runs/run-*/report.html 2>/dev/null | head -1 | xargs -I {} open {} || echo "No reports found"