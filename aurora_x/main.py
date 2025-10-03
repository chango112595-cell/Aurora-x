#!/usr/bin/env python3
"""Aurora-X main module with corpus integration and learning weights."""

from __future__ import annotations
import argparse
import sys
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional
from .corpus.store import record as corpus_record, retrieve as corpus_retrieve, spec_digest
from .corpus.pretty import fmt_rows, filter_rows, to_json
from .learn import weights as learn

# Stub imports for synthesis modules (to be implemented)
class Repo:
    @staticmethod
    def create(outdir): return Repo()
    def __init__(self): self.root = Path(".")
    def path(self, p): return self.root / p
    def set_hash(self, p, c): pass

class Sandbox:
    def __init__(self, root, timeout_s): pass

class Spec:
    def __init__(self): self.functions = []

def parse_spec(text): return Spec()
def write_file(p, c): Path(p).write_text(c)

def main():
    """Main entry point for Aurora-X."""
    ap = argparse.ArgumentParser(description="Aurora-X Autonomous Code Synthesis Engine")
    
    # Mutually exclusive: spec, spec-file, or dump-corpus
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--spec", type=str, help="Inline spec text (Markdown DSL)")
    g.add_argument("--spec-file", type=str, help="Path to spec file")
    g.add_argument("--dump-corpus", type=str, help="Signature to query corpus instead of running synthesis")
    
    # Corpus dump options
    ap.add_argument("--top", type=int, default=10, help="How many corpus entries to print with --dump-corpus")
    ap.add_argument("--json", action="store_true", help="Emit JSON for --dump-corpus")
    ap.add_argument("--grep", type=str, default=None, help="Filter results by substring for --dump-corpus")
    
    # Synthesis options
    ap.add_argument("--seed", type=int, default=1337, help="Random seed")
    ap.add_argument("--outdir", type=str, default="./runs", help="Output directory")
    ap.add_argument("--no-seed", action="store_true", help="Disable seeding from corpus")
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
        seed_bias_override=args.seed_bias
    )
    repo, ok = ax.run(spec_text)
    
    return 0 if ok else 1

class AuroraX:
    def __init__(self, seed: int, max_iters: int, beam: int, timeout_s: int, outdir: Optional[Path],
                 rng_cfg: Dict[str, Any], disable_seed: bool = False, seed_bias_override: float | None = None):
        random.seed(seed)
        self.repo = Repo.create(outdir)
        self.sandbox = Sandbox(self.repo.root, timeout_s=timeout_s)
        self.beam = beam
        self.max_iters = max_iters
        self.rng_cfg = rng_cfg
        self.disable_seed = disable_seed
        self.weights = learn.load(self.repo.root)
        if seed_bias_override is not None:
            self.weights["seed_bias"] = max(0.0, min(0.5, float(seed_bias_override)))
    
    def run(self, spec_text: str):
        """Main orchestration loop."""
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
        
        return self.repo, True
    
    def build_module(self, spec, best_map):
        """Build final module source."""
        return "\n\n".join(best_map.values())
    
    def synthesize_best(self, f, callees_meta, base_prefix):
        """Stub for synthesis - returns mock candidate."""
        return type('obj', (object,), {'src': f'def {f.name}(): pass'})()
    
    def save_run_config(self, cfg: Dict[str, Any]) -> None:
        write_file(self.repo.path("run_config.json"), json.dumps(cfg, indent=2))

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