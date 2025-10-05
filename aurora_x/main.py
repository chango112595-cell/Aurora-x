#!/usr/bin/env python3
"""Aurora-X main module with corpus integration and learning weights."""

from __future__ import annotations
import argparse
import sys
import json
import random
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from .corpus.store import record as corpus_record, retrieve as corpus_retrieve, spec_digest
from .corpus.pretty import fmt_rows, filter_rows, to_json
from .learn import weights as learn

def iso_now() -> str:
    """Get current ISO timestamp."""
    return datetime.now().isoformat()

def fmt_duration(seconds: float) -> str:
    """Format seconds into human-readable 'Xh Ym Zs' format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    
    return " ".join(parts)

def diff_graphs(old: Dict[str, list], new: Dict[str, list]) -> Dict[str, Any]:
    """Compute differences between two call graphs.
    
    Args:
        old: Old graph as adjacency list (node -> list of connected nodes)
        new: New graph as adjacency list (node -> list of connected nodes)
    
    Returns:
        Dictionary with:
        - "added": sorted list of added edge tuples
        - "removed": sorted list of removed edge tuples
        - "old_edges": count of edges in old graph
        - "new_edges": count of edges in new graph
    """
    # Extract edges from both graphs as sets of tuples
    old_edges = set()
    for u, neighbors in old.items():
        for v in neighbors:
            old_edges.add((u, v))
    
    new_edges = set()
    for u, neighbors in new.items():
        for v in neighbors:
            new_edges.add((u, v))
    
    # Compute added and removed edges
    added = new_edges - old_edges
    removed = old_edges - new_edges
    
    # Return result dictionary
    return {
        "added": sorted(list(added)),
        "removed": sorted(list(removed)),
        "old_edges": len(old_edges),
        "new_edges": len(new_edges)
    }

def load_scores_map(run_root: Path) -> Dict[str, Dict[str, Any]]:
    """Load function scores from logs/scores.jsonl.
    
    Args:
        run_root: Root directory of the run
    
    Returns:
        Dict mapping function names to their latest scores:
        {'passed': int, 'total': int, 'iter': int}
    """
    scores_file = run_root / "logs" / "scores.jsonl"
    if not scores_file.exists():
        return {}
    
    scores_map = {}
    try:
        with open(scores_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                func_name = entry.get("function")
                if not func_name:
                    continue
                
                # Track latest score per function (highest iteration)
                curr_iter = entry.get("iter", 0)
                if func_name not in scores_map or curr_iter > scores_map[func_name].get("iter", 0):
                    scores_map[func_name] = {
                        "passed": entry.get("passed", 0),
                        "total": entry.get("total", 0),
                        "iter": curr_iter
                    }
    except Exception:
        # Return empty dict on any error
        return {}
    
    return scores_map

def diff_scores(old: Dict[str, Dict[str, Any]], new: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Compute per-function score differences.
    
    Args:
        old: Old score map from load_scores_map
        new: New score map from load_scores_map
    
    Returns:
        Dict with:
        - "summary": {"regressions": count, "improvements": count, "count": total_functions}
        - "rows": list of dicts with "function", "old" [passed, total], "new" [passed, total], "delta_passed"
    """
    all_funcs = set(old.keys()) | set(new.keys())
    
    rows = []
    regressions = 0
    improvements = 0
    
    for func in sorted(all_funcs):
        old_score = old.get(func, {"passed": 0, "total": 0})
        new_score = new.get(func, {"passed": 0, "total": 0})
        
        old_passed = old_score.get("passed", 0)
        old_total = old_score.get("total", 0)
        new_passed = new_score.get("passed", 0)
        new_total = new_score.get("total", 0)
        
        delta_passed = new_passed - old_passed
        
        if delta_passed < 0:
            regressions += 1
        elif delta_passed > 0:
            improvements += 1
        
        rows.append({
            "function": func,
            "old": [old_passed, old_total],
            "new": [new_passed, new_total],
            "delta_passed": delta_passed
        })
    
    return {
        "summary": {
            "regressions": regressions,
            "improvements": improvements,
            "count": len(all_funcs)
        },
        "rows": rows
    }

# Stub imports for synthesis modules (to be implemented)
class Repo:
    @staticmethod
    def create(outdir): 
        r = Repo()
        if outdir:
            # Create timestamped run directory under outdir
            import time
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            r.root = outdir / f"run-{timestamp}"
            r.root.mkdir(parents=True, exist_ok=True)
        else:
            r.root = Path("/tmp/aurora-tmp")
            r.root.mkdir(parents=True, exist_ok=True)
        return r
    def __init__(self): 
        self.root = Path(".")
    def path(self, p): 
        return self.root / p
    def set_hash(self, p, c): 
        pass
    def list_files(self):
        return [str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file()]

class Sandbox:
    def __init__(self, root, timeout_s): pass

class Spec:
    def __init__(self): self.functions = []

def parse_spec(text): return Spec()
def write_file(p, c): 
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(c)

def main():
    """Main entry point for Aurora-X."""
    ap = argparse.ArgumentParser(description="AURORA-X Ultra (Offline)")
    
    # Mutually exclusive: spec, spec-file, dump-corpus, or show-bias
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--spec", type=str, help="Inline spec text (Markdown DSL)")
    g.add_argument("--spec-file", type=str, help="Path to spec file")
    g.add_argument("--dump-corpus", type=str, help="Signature to query corpus instead of running synthesis")
    g.add_argument("--show-bias", action="store_true", help="Print current seed_bias and exit")
    
    # Corpus dump options
    ap.add_argument("--top", type=int, default=10, help="How many corpus entries to print with --dump-corpus")
    ap.add_argument("--json", action="store_true", help="Emit JSON for --dump-corpus")
    ap.add_argument("--grep", type=str, default=None, help="Filter results by substring for --dump-corpus")
    
    # Synthesis options
    ap.add_argument("--seed", type=int, default=1337, help="Random seed")
    ap.add_argument("--outdir", type=str, default="./runs", help="Output directory")
    ap.add_argument("--no-seed", action="store_true", help="Disable seeding from corpus")
    ap.add_argument("--baseline", type=str, default=None, help="Path to baseline run dir for report diffs (default: runs/latest)")
    ap.add_argument("--seed-bias", type=float, default=None, help="Override learned seed bias [0.0..0.5]")
    ap.add_argument("--max-iters", type=int, default=100, help="Maximum synthesis iterations")
    ap.add_argument("--beam", type=int, default=20, help="Beam search width")
    ap.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")
    
    # RNG config
    ap.add_argument("--temp", type=float, default=0.9, help="Temperature")
    ap.add_argument("--top-k", type=int, default=50, help="Top-K sampling")
    ap.add_argument("--top-p", type=float, default=0.95, help="Top-P (nucleus) sampling")
    
    args = ap.parse_args()
    
    outdir = Path(args.outdir).resolve() if args.outdir else None
    rng_cfg = {
        "temperature": args.temp,
        "top_k": args.top_k,
        "top_p": args.top_p
    }
    
    # ----- Show bias mode (no synthesis) -----
    if args.show_bias:
        run_root = outdir / "latest"
        weights_file = run_root / "learn_weights.json"
        if weights_file.exists():
            try:
                weights = json.loads(weights_file.read_text())
                sb = float(weights.get("seed_bias", 0.0))
                print(f"[AURORA-X] Current seed_bias: {sb:.2f}")
            except Exception as e:
                print(f"[AURORA-X] Error reading seed_bias: {e}")
        else:
            print("[AURORA-X] No weights found yet. Run a synthesis first.")
        return 0
    
    # ----- Corpus dump mode (no synthesis) -----
    if args.dump_corpus:
        run_root = outdir / "run-dump"
        run_root.mkdir(parents=True, exist_ok=True)
        rows = corpus_retrieve(run_root, args.dump_corpus, k=max(1, args.top))
        rows = filter_rows(rows, args.grep)
        print(to_json(rows) if args.json else fmt_rows(rows))
        return 0
    
    # ----- Synthesis mode -----
    spec_text = args.spec if args.spec else Path(args.spec_file).read_text()
    
    ax = AuroraX(
        seed=args.seed, 
        max_iters=args.max_iters, 
        beam=args.beam, 
        timeout_s=args.timeout,
        outdir=outdir, 
        rng_cfg=rng_cfg, 
        disable_seed=args.no_seed, 
        seed_bias_override=args.seed_bias,
        baseline=Path(args.baseline).resolve() if args.baseline else None
    )
    repo, ok = ax.run(spec_text)
    
    # Show seed_bias snapshot at the end of the run for quick glance
    try:
        weights = learn.load(repo.root)
        sb = float(weights.get("seed_bias", 0.0))
    except Exception:
        sb = 0.0
    
    print(f"[AURORA-X] Repo: {repo.root}")
    print(f"[AURORA-X] Status: {'PASS' if ok else 'INCOMPLETE'}")
    print(f"[AURORA-X] seed_bias: {sb:.2f}")
    print("[AURORA-X] Files:")
    for f in repo.list_files():
        print(" -", f)
    print(f"\nOpen HTML report: file://{repo.path('report.html')}")
    
    return 0 if ok else 1

class AuroraX:
    def __init__(self, seed: int, max_iters: int, beam: int, timeout_s: int, outdir: Optional[Path],
                 rng_cfg: Dict[str, Any], disable_seed: bool = False, seed_bias_override: float | None = None,
                 baseline: Optional[Path] = None):
        random.seed(seed)
        self._start_time = time.time()
        self.repo = Repo.create(outdir)
        self.sandbox = Sandbox(self.repo.root, timeout_s=timeout_s)
        self.beam = beam
        self.max_iters = max_iters
        self.rng_cfg = rng_cfg
        self.disable_seed = disable_seed
        self.baseline = baseline
        self.weights = learn.load(self.repo.root)
        if seed_bias_override is not None:
            self.weights["seed_bias"] = max(0.0, min(0.5, float(seed_bias_override)))
    
    def run(self, spec_text: str):
        """Main orchestration loop."""
        start_ts = iso_now()  # Capture start timestamp in ISO format
        spec = parse_spec(spec_text)
        best_map: Dict[str,str] = {}
        
        for idx, f in enumerate(spec.functions):
            # Gather seed snippets from corpus
            seed_snippets: List[str] = []
            if not self.disable_seed:
                sig = f"{f.name}({', '.join(a+': '+t for a,t in f.args)}) -> {f.returns}"
                for row in corpus_retrieve(self.repo.root, sig, k=min(12, self.beam//4)):
                    seed_snippets.append(row["snippet"])
            
            # Synthesize (stub - would call actual synthesis)
            cand = type('obj', (object,), {'src': 'def stub(): pass'})()
            
            # Record to corpus
            corpus_entry = {
                "func_name": f.name,
                "func_signature": sig,
                "passed": 1,
                "total": 1,
                "score": 1.0,
                "snippet": cand.src,
                **spec_digest(spec_text)
            }
            corpus_record(self.repo.root, corpus_entry)
            
            best_map[f.name] = cand.src
            
            # Learning nudge
            won_with_seed = _seed_won(cand.src, seed_snippets)
            self.weights["seed_bias"] = learn.update_seed_bias(
                float(self.weights.get("seed_bias", 0.0)), 
                won_with_seed
            )
            learn.save(self.repo.root, self.weights)
        
        # Build and save module
        module_src = self.build_module(spec, best_map)
        write_file(self.repo.path("src/app.py"), module_src)
        self.repo.set_hash("src/app.py", module_src)
        
        # Save run config
        cfg = {
            "seed": random.getstate()[1][0],
            "max_iters": self.max_iters,
            "beam": self.beam,
            **self.rng_cfg,
            "weights": self.weights
        }
        self.save_run_config(cfg)
        
        # Capture end time and save run metadata
        self._end_time = time.time()
        duration_seconds = round(self._end_time - self._start_time, 3)
        run_metadata = {
            "start_ts": start_ts,
            "end_ts": iso_now(),
            "duration_seconds": duration_seconds
        }
        write_file(self.repo.path("run_meta.json"), json.dumps(run_metadata, indent=2))
        
        # Generate HTML report (before symlink update so it can detect previous latest run)
        write_html_report(self.repo, spec, baseline=self.baseline)
        
        # Update 'latest' symlink to this run (after HTML report generation)
        try:
            latest_link = self.repo.root.parent / "latest"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(self.repo.root.resolve())
            print(f"[AURORA-X] Updated symlink: {latest_link} → {self.repo.root.name}")
        except Exception as e:
            print(f"[AURORA-X] (nonfatal) failed to update 'latest' symlink: {e}")
        
        return self.repo, True
    
    def build_module(self, spec, best_map):
        """Build final module source."""
        return "\n\n".join(best_map.values())
    
    def synthesize_best(self, f, callees_meta, base_prefix):
        """Stub for synthesis - returns mock candidate."""
        return type('obj', (object,), {'src': f'def {f.name}(): pass'})()
    
    def save_run_config(self, cfg: Dict[str, Any]) -> None:
        write_file(self.repo.path("run_config.json"), json.dumps(cfg, indent=2))

def write_html_report(repo: Repo, spec: Spec, baseline: Optional[Path] = None) -> None:
    """Generate HTML report with latest run status."""
    # Read report markdown if exists
    report_path = repo.path("AURORA_REPORT.md")
    if report_path.exists():
        md = report_path.read_text()
    else:
        md = "# Aurora-X Synthesis Report\n\nRun completed."
        write_file(report_path, md)
    
    cfg = json.loads(repo.path("run_config.json").read_text())
    
    # Load run metadata for timestamp and duration
    run_meta_path = repo.path("run_meta.json")
    start_ts = None
    duration_seconds = None
    if run_meta_path.exists():
        try:
            run_meta = json.loads(run_meta_path.read_text())
            start_ts = run_meta.get("start_ts")
            duration_seconds = run_meta.get("duration_seconds")
        except Exception:
            pass
    
    # Call graph (stub for now - would load from call_graph.json in real implementation)
    graph = {"nodes": [f.name for f in spec.functions], "edges": {}}
    
    # Save call graph for future comparisons
    call_graph_path = repo.path("call_graph.json")
    write_file(call_graph_path, json.dumps(graph, indent=2))
    
    # weights + bias snapshot
    weights_path = repo.path("learn_weights.json")
    try:
        weights = json.loads(weights_path.read_text()) if weights_path.exists() else {}
    except Exception:
        weights = {}
    seed_bias = float(weights.get("seed_bias", 0.0))
    
    # latest symlink status
    latest_link = repo.root.parent / "latest"
    try:
        is_latest = latest_link.exists() and latest_link.resolve() == repo.root.resolve()
    except Exception:
        is_latest = False
    
    # If NOT latest run, generate graph comparison
    graph_diff_generated = False
    if not is_latest and latest_link.exists():
        try:
            latest_graph_path = latest_link / "call_graph.json"
            if latest_graph_path.exists():
                latest_graph = json.loads(latest_graph_path.read_text())
                # Compute diff using diff_graphs function
                diff = diff_graphs(
                    latest_graph.get("edges", {}),
                    graph.get("edges", {})
                )
                
                # Save graph_diff.json
                graph_diff_path = repo.path("graph_diff.json")
                write_file(graph_diff_path, json.dumps(diff, indent=2))
                
                # Generate graph_diff.html
                diff_html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Graph Comparison</title>
<style>
  body{{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:24px}}
  .added{{color:#16a34a;font-weight:600}}
  .removed{{color:#dc2626;font-weight:600}}
  pre{{background:#f6f8fa;padding:12px;overflow:auto;border-radius:6px}}
  h2{{color:#1e293b}}
  .stats{{background:#f0f9ff;padding:12px;border-radius:6px;margin:16px 0}}
</style>
</head><body>
<h1>Graph Comparison with Latest Run</h1>
<div class="stats">
  <b>Statistics:</b><br>
  Previous edges: {diff['old_edges']}<br>
  Current edges: {diff['new_edges']}<br>
  Added: {len(diff['added'])}<br>
  Removed: {len(diff['removed'])}
</div>

<h2 class="added">Added Edges ({len(diff['added'])})</h2>
<pre>{json.dumps(diff['added'], indent=2) if diff['added'] else 'None'}</pre>

<h2 class="removed">Removed Edges ({len(diff['removed'])})</h2>
<pre>{json.dumps(diff['removed'], indent=2) if diff['removed'] else 'None'}</pre>

<h2>Full Diff Data</h2>
<pre>{json.dumps(diff, indent=2)}</pre>

<p><a href="report.html">← Back to Report</a></p>
</body></html>"""
                write_file(repo.path("graph_diff.html"), diff_html)
                graph_diff_generated = True
        except Exception as e:
            print(f"[AURORA-X] Could not generate graph diff: {e}")
    
    # Scores regression comparison
    scores_diff_generated = False
    scores_html = ""
    if latest_link.exists():
        try:
            # Load scores from both runs
            latest_scores = load_scores_map(latest_link)
            current_scores = load_scores_map(repo.root)
            
            # Only generate diff if we have scores from at least one run
            if latest_scores or current_scores:
                # Compute diff
                scores_diff = diff_scores(latest_scores, current_scores)
                
                # Save scores_diff.json
                scores_diff_path = repo.path("scores_diff.json")
                write_file(scores_diff_path, json.dumps(scores_diff, indent=2))
                
                # Generate HTML table for scores regression
                summary = scores_diff["summary"]
                rows = scores_diff["rows"]
                
                # Build regression table rows
                table_rows = []
                for row in rows:
                    func = row["function"]
                    old_p, old_t = row["old"]
                    new_p, new_t = row["new"]
                    delta = row["delta_passed"]
                    
                    # Color coding for delta
                    if delta < 0:
                        delta_color = "#dc2626"  # red for regression
                        delta_text = f"{delta:+d}"
                    elif delta > 0:
                        delta_color = "#16a34a"  # green for improvement
                        delta_text = f"{delta:+d}"
                    else:
                        delta_color = "#6b7280"  # gray for no change
                        delta_text = "0"
                    
                    table_rows.append(
                        f'<tr>'
                        f'<td>{func}</td>'
                        f'<td>{old_p}/{old_t}</td>'
                        f'<td>{new_p}/{new_t}</td>'
                        f'<td style="color:{delta_color};font-weight:600">{delta_text}</td>'
                        f'</tr>'
                    )
                
                # Generate scores_diff.html standalone page
                scores_diff_html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Scores Regression</title>
<style>
  body{{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:24px}}
  .summary{{background:#f0f9ff;padding:16px;border-radius:8px;margin:20px 0}}
  .summary-bar{{display:flex;gap:20px;margin-top:12px}}
  .stat{{padding:8px 12px;border-radius:6px;font-weight:600}}
  .regression{{background:#fee2e2;color:#991b1b}}
  .improvement{{background:#dcfce7;color:#14532d}}
  .neutral{{background:#f3f4f6;color:#374151}}
  table{{width:100%;border-collapse:collapse;margin:20px 0}}
  th{{background:#f8fafc;text-align:left;padding:12px;border-bottom:2px solid #e5e7eb}}
  td{{padding:10px 12px;border-bottom:1px solid #e5e7eb}}
  tr:hover{{background:#f8fafc}}
  h2{{color:#1e293b}}
  a{{color:#0969da;text-decoration:none}}
  a:hover{{text-decoration:underline}}
</style>
</head><body>
<h1>Scores Regression Analysis</h1>

<div class="summary">
  <h3 style="margin:0 0 12px 0">Summary</h3>
  <div class="summary-bar">
    <span class="stat regression">Regressions: {summary['regressions']}</span>
    <span class="stat improvement">Improvements: {summary['improvements']}</span>
    <span class="stat neutral">Total Functions: {summary['count']}</span>
  </div>
</div>

<h2>Function Scores Comparison</h2>
<table>
  <thead>
    <tr>
      <th>Function</th>
      <th>Old (pass/total)</th>
      <th>New (pass/total)</th>
      <th>Δ passed</th>
    </tr>
  </thead>
  <tbody>
    {''.join(table_rows)}
  </tbody>
</table>

<h2>Raw Data</h2>
<pre>{json.dumps(scores_diff, indent=2)}</pre>

<p><a href="report.html">← Back to Report</a></p>
</body></html>"""
                write_file(repo.path("scores_diff.html"), scores_diff_html)
                scores_diff_generated = True
                
                # Build HTML section for main report
                scores_html = f"""
<h3>Scores Regression</h3>
<div style="background:#f0f9ff;padding:16px;border-radius:8px;margin:12px 0">
  <div style="display:flex;gap:20px">
    <span style="padding:8px 12px;border-radius:6px;background:#fee2e2;color:#991b1b;font-weight:600">
      Regressions: {summary['regressions']}
    </span>
    <span style="padding:8px 12px;border-radius:6px;background:#dcfce7;color:#14532d;font-weight:600">
      Improvements: {summary['improvements']}
    </span>
    <span style="padding:8px 12px;border-radius:6px;background:#f3f4f6;color:#374151;font-weight:600">
      Total: {summary['count']}
    </span>
  </div>
</div>
<table style="width:100%;border-collapse:collapse;margin:12px 0">
  <thead>
    <tr style="background:#f8fafc">
      <th style="text-align:left;padding:12px;border-bottom:2px solid #e5e7eb">Function</th>
      <th style="text-align:left;padding:12px;border-bottom:2px solid #e5e7eb">Old (pass/total)</th>
      <th style="text-align:left;padding:12px;border-bottom:2px solid #e5e7eb">New (pass/total)</th>
      <th style="text-align:left;padding:12px;border-bottom:2px solid #e5e7eb">Δ passed</th>
    </tr>
  </thead>
  <tbody>
    {''.join([f'<tr style="border-bottom:1px solid #e5e7eb">' + row.replace('<td', '<td style="padding:10px 12px"') + '</tr>' for row in [r.replace('<tr>', '').replace('</tr>', '') for r in table_rows]])}
  </tbody>
</table>
"""
        except Exception as e:
            print(f"[AURORA-X] Could not generate scores diff: {e}")
    
    latest_badge = (
        '<span style="display:inline-block;padding:4px 8px;border-radius:6px;background:#16a34a;color:#fff;font-weight:600;">LATEST RUN ✓</span>'
        if is_latest else
        f'<span style="display:inline-block;padding:4px 8px;border-radius:6px;background:#f59e0b;color:#111;font-weight:600;">NOT LATEST</span> '
        f'<a href="../latest/report.html" style="margin-left:8px;">Open Latest Report →</a>'
    )
    
    # Build timestamp/duration banner
    meta_parts = []
    if start_ts:
        meta_parts.append(f"<b>Started:</b> {start_ts}")
    if duration_seconds is not None:
        meta_parts.append(f"<b>Duration:</b> {fmt_duration(duration_seconds)}")
    meta_html = " | ".join(meta_parts) if meta_parts else ""
    
    # quick links if present
    corpus_jsonl = repo.root / "corpus.jsonl"
    corpus_db = repo.root / "corpus.db"
    links = []
    if corpus_jsonl.exists(): 
        links.append(f'<a href="corpus.jsonl">corpus.jsonl</a>')
    if corpus_db.exists(): 
        links.append(f'<a href="corpus.db">corpus.db</a>')
    if weights_path.exists():
        links.append(f'<a href="learn_weights.json">learn_weights.json</a>')
    if graph_diff_generated:
        links.append(f'<a href="graph_diff.html">Compare with latest (diff)</a>')
    if scores_diff_generated:
        links.append(f'<a href="scores_diff.html">Scores regression</a>')
    links_html = " | ".join(links) if links else "No corpus files yet"
    
    body = f"""<!doctype html><html><head><meta charset="utf-8"><title>AURORA-X Report</title>
<style>
  body{{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:24px}}
  pre,code{{background:#f6f8fa;padding:12px;overflow:auto;border-radius:6px}}
  .hdr{{display:flex;align-items:center;gap:12px;margin-bottom:8px}}
  .sub{{color:#555;margin:0 0 4px 0}}
  .meta{{color:#666;margin:0 0 16px 0;font-size:14px}}
  h3{{color:#1e293b;margin-top:24px}}
  a{{color:#0969da;text-decoration:none}}
  a:hover{{text-decoration:underline}}
</style>
</head><body>
<div class="hdr">
  <h1 style="margin:0;">AURORA-X Ultra</h1>
  {latest_badge}
</div>
<p class="sub"><b>Run:</b> {repo.root}</p>
{f'<p class="meta">{meta_html}</p>' if meta_html else ''}

<h3>Learning</h3>
<pre>{json.dumps({"seed_bias": round(seed_bias, 4), "weights_file": str(weights_path.name if weights_path.exists() else "none")}, indent=2)}</pre>

<h3>Quick Links</h3>
<p>{links_html}</p>

<h3>Config</h3>
<pre>{json.dumps(cfg, indent=2)}</pre>

<h3>Call Graph</h3>
<pre>{json.dumps(graph, indent=2)}</pre>

{scores_html}

<h3>Report</h3>
<pre>{md}</pre>

</body></html>"""
    write_file(repo.path("report.html"), body)

def _seed_won(final_src: str, seeds: List[str]) -> bool:
    """Check if winning code matches any seed (whitespace-insensitive)."""
    def norm(s: str) -> str: 
        return "".join(s.split())
    n_final = norm(final_src)
    for s in seeds:
        try:
            if norm(s) == n_final:
                return True
        except Exception:
            continue
    return False

if __name__ == "__main__":
    sys.exit(main())