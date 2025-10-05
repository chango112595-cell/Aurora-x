.PHONY: run test clean install open-report compare-latest

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