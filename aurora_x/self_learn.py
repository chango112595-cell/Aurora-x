
#!/usr/bin/env python3
"""
Aurora-X Continuous Self-Learning Daemon
Runs synthesis tasks continuously, learning from each iteration.
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from aurora_x.main import AuroraX
from aurora_x.learn import get_seed_store


class SelfLearningDaemon:
    """Continuous learning daemon for Aurora-X."""
    
    def __init__(
        self,
        spec_dir: Path = Path("specs"),
        outdir: Path = Path("runs"),
        sleep_seconds: int = 15,  # 15 seconds - very aggressive learning (practical minimum)
        max_iters: int = 50,
        beam: int = 20,
    ):
        self.spec_dir = spec_dir
        self.outdir = outdir
        self.sleep_seconds = sleep_seconds
        self.max_iters = max_iters
        self.beam = beam
        self.run_count = 0
        self.seed_store = get_seed_store()
        
    def get_next_spec(self) -> Path | None:
        """Get next spec file to synthesize."""
        # Get all spec files
        specs = list(self.spec_dir.glob("*.md"))
        
        if not specs:
            print("[Self-Learn] No spec files found")
            return None
            
        # Prioritize specs that haven't been run recently
        # For now, just pick randomly
        return random.choice(specs)
        
    def log(self, msg: str):
        """Log with timestamp."""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] [Self-Learn] {msg}")
        
    def run_synthesis(self, spec_path: Path) -> bool:
        """Run synthesis on a spec file."""
        try:
            self.log(f"Starting synthesis: {spec_path.name}")
            
            # Read spec
            spec_text = spec_path.read_text()
            
            # Create Aurora instance with learning enabled
            aurora = AuroraX(
                seed=random.randint(1000, 9999),
                max_iters=self.max_iters,
                beam=self.beam,
                timeout_s=5,
                outdir=self.outdir,
                rng_cfg={"temperature": 0.9, "top_k": 50, "top_p": 0.95},
                disable_seed=False,  # Enable seeding for learning
            )
            
            # Run synthesis
            repo, success = aurora.run(spec_text)
            
            # Log results
            if success:
                self.log(f"✓ Synthesis successful: {repo.root}")
            else:
                self.log(f"✗ Synthesis incomplete: {repo.root}")
                
            # Get updated seed bias
            try:
                weights = json.loads((repo.root / "learn_weights.json").read_text())
                seed_bias = weights.get("seed_bias", 0.0)
                self.log(f"Seed bias: {seed_bias:.4f}")
            except Exception:
                pass
                
            return success
            
        except Exception as e:
            self.log(f"Error during synthesis: {e}")
            return False
            
    def run_forever(self):
        """Run continuous learning loop."""
        self.log("Starting continuous self-learning daemon")
        self.log(f"Specs directory: {self.spec_dir}")
        self.log(f"Output directory: {self.outdir}")
        self.log(f"Sleep interval: {self.sleep_seconds}s")
        
        while True:
            try:
                # Get next spec to synthesize
                spec_path = self.get_next_spec()
                
                if spec_path is None:
                    self.log("No specs available, sleeping...")
                    time.sleep(self.sleep_seconds)
                    continue
                    
                # Run synthesis
                success = self.run_synthesis(spec_path)
                
                # Increment run counter
                self.run_count += 1
                
                # Log summary
                self.log(f"Completed run #{self.run_count} ({'success' if success else 'incomplete'})")
                
                # Show seed store summary periodically
                if self.run_count % 5 == 0:
                    summary = self.seed_store.get_summary()
                    self.log(f"Seed store: {summary['total_seeds']} seeds, avg bias: {summary['avg_bias']:.4f}")
                
                # Sleep before next run
                self.log(f"Sleeping {self.sleep_seconds}s before next run...")
                time.sleep(self.sleep_seconds)
                
            except KeyboardInterrupt:
                self.log("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                self.log(f"Unexpected error in main loop: {e}")
                self.log("Continuing after 60s...")
                time.sleep(60)
                
        self.log(f"Daemon stopped after {self.run_count} runs")


def main():
    """Main entry point for self-learning daemon."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Aurora-X Continuous Self-Learning Daemon")
    parser.add_argument("--spec-dir", type=str, default="specs", help="Directory containing spec files")
    parser.add_argument("--outdir", type=str, default="runs", help="Output directory for synthesis runs")
    parser.add_argument("--sleep", type=int, default=300, help="Seconds to sleep between runs")
    parser.add_argument("--max-iters", type=int, default=50, help="Max synthesis iterations")
    parser.add_argument("--beam", type=int, default=20, help="Beam search width")
    
    args = parser.parse_args()
    
    daemon = SelfLearningDaemon(
        spec_dir=Path(args.spec_dir),
        outdir=Path(args.outdir),
        sleep_seconds=args.sleep,
        max_iters=args.max_iters,
        beam=args.beam,
    )
    
    daemon.run_forever()


if __name__ == "__main__":
    main()
