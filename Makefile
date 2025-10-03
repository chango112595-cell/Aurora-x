.PHONY: run test clean install open-report

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