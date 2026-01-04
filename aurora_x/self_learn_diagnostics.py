#!/usr/bin/env python3
"""
Aurora Self-Learning Diagnostics Module
Provides honest feedback on learning quality and effectiveness
"""

from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Optional


class SelfLearningDiagnostics:
    """Diagnoses quality and effectiveness of self-learning runs"""
    
    def __init__(self):
        self.diagnostics_file = Path(".aurora_diagnostics.json")
        self.failed_specs: List[str] = []
        self.quality_scores: List[Dict] = []
        self._load_existing_state()
        
    def _load_existing_state(self):
        """Load existing diagnostics from disk on init"""
        if self.diagnostics_file.exists():
            try:
                data = json.loads(self.diagnostics_file.read_text())
                self.quality_scores = data.get("recent_scores", [])
                progress = data.get("progress", {})
                self.failed_specs = progress.get("failed_specs", [])
            except Exception:
                pass
        
    def diagnose_synthesis_run(
        self, 
        spec_name: str, 
        success: bool, 
        output_repo: Optional[Path] = None,
        error_msg: Optional[str] = None
    ) -> Dict:
        """
        Diagnose a single synthesis run with honest 0-100 scoring
        
        Args:
            spec_name: Name of the spec that was synthesized
            success: Whether synthesis succeeded
            output_repo: Path to generated code repo
            error_msg: Error message if failed
            
        Returns:
            Diagnostic report dict
        """
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "spec_name": spec_name,
            "success": success,
            "quality_score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        if not success:
            diagnosis["quality_score"] = 0.0
            diagnosis["issues"].append(f"Synthesis failed: {error_msg or 'Unknown error'}")
            diagnosis["recommendations"].append("Investigate failure pattern")
            if spec_name not in self.failed_specs:
                self.failed_specs.append(spec_name)
        elif output_repo and output_repo.exists():
            quality_score = self._check_code_quality(output_repo)
            diagnosis["quality_score"] = quality_score
            
            if quality_score == 0:
                diagnosis["issues"].append("No code files generated")
                diagnosis["recommendations"].append("Review synthesis pipeline")
            elif quality_score < 30:
                diagnosis["issues"].append("Generated code has quality issues")
                diagnosis["recommendations"].append("Review generated code patterns")
            elif quality_score < 70:
                diagnosis["issues"].append("Generated code could be improved")
                diagnosis["recommendations"].append("Analyze common improvement areas")
            else:
                diagnosis["recommendations"].append("Continue current synthesis approach")
        else:
            diagnosis["quality_score"] = 0.0
            diagnosis["issues"].append("Output repo does not exist")
            diagnosis["recommendations"].append("Check synthesis output path")
        
        self.quality_scores.append({
            "spec": spec_name,
            "score": diagnosis["quality_score"],
            "timestamp": diagnosis["timestamp"],
            "success": success
        })
        
        if len(self.quality_scores) > 100:
            self.quality_scores = self.quality_scores[-100:]
        
        self._save_to_disk(diagnosis)
        
        return diagnosis
    
    def _check_code_quality(self, repo_path: Path) -> float:
        """Check generated code quality with honest 0-100 scoring"""
        if not repo_path.exists():
            return 0.0
            
        try:
            py_files = list(repo_path.rglob("*.py"))
            js_files = list(repo_path.rglob("*.js")) + list(repo_path.rglob("*.ts"))
            all_code_files = py_files + js_files
            
            if not all_code_files:
                return 0.0
            
            score = 0.0
            
            total_lines = 0
            for code_file in all_code_files[:10]:
                try:
                    content = code_file.read_text()
                    total_lines += len(content.split('\n'))
                except Exception:
                    pass
            
            if total_lines > 10:
                score += 20
            elif total_lines > 0:
                score += 10
            
            docstring_count = 0
            for py_file in py_files[:5]:
                try:
                    content = py_file.read_text()
                    if '"""' in content or "'''" in content:
                        docstring_count += 1
                except Exception:
                    pass
            
            if py_files:
                coverage_ratio = docstring_count / min(len(py_files), 5)
                if coverage_ratio >= 0.8:
                    score += 20
                elif coverage_ratio >= 0.5:
                    score += 10
                elif coverage_ratio > 0:
                    score += 5
            
            has_type_hints = False
            for py_file in py_files[:3]:
                try:
                    content = py_file.read_text()
                    if " -> " in content or ": str" in content or ": int" in content or ": Dict" in content:
                        has_type_hints = True
                        break
                except Exception:
                    pass
            
            if has_type_hints:
                score += 15
            
            test_files = list(repo_path.rglob("test_*.py")) + list(repo_path.rglob("*_test.py"))
            if test_files:
                score += 20
            elif list(repo_path.rglob("tests/")):
                score += 10
            
            readme_files = list(repo_path.glob("README*")) + list(repo_path.glob("readme*"))
            if readme_files:
                score += 10
            
            req_files = list(repo_path.glob("requirements.txt")) + list(repo_path.glob("package.json"))
            if req_files:
                score += 10
            
            return min(score, 95.0)
            
        except Exception:
            return 0.0
    
    def _save_to_disk(self, latest_diagnosis: Dict):
        """Save current state to disk after each diagnosis"""
        try:
            diagnostics = {
                "generated_at": datetime.now().isoformat(),
                "latest_diagnosis": latest_diagnosis,
                "progress": self.get_learning_progress(),
                "recent_scores": self.quality_scores[-20:]
            }
            self.diagnostics_file.write_text(json.dumps(diagnostics, indent=2))
        except Exception:
            pass
    
    def get_learning_progress(self) -> Dict:
        """Get overall self-learning progress with honest metrics"""
        total_runs = len(self.quality_scores)
        if total_runs == 0:
            return {
                "total_runs": 0,
                "success_rate": 0.0,
                "avg_quality": 0.0,
                "failed_specs": self.failed_specs,
                "high_quality_runs": 0
            }
        
        successful_runs = sum(1 for s in self.quality_scores if s.get("success", False) and s["score"] > 0)
        avg_quality = sum(s["score"] for s in self.quality_scores) / total_runs
        
        return {
            "total_runs": total_runs,
            "success_rate": round((successful_runs / total_runs) * 100, 1),
            "avg_quality": round(avg_quality, 1),
            "failed_specs": self.failed_specs,
            "high_quality_runs": sum(1 for s in self.quality_scores if s["score"] >= 70),
            "zero_score_runs": sum(1 for s in self.quality_scores if s["score"] == 0)
        }
    
    def save_diagnostics(self) -> Dict:
        """Save full diagnostics to disk for tracking"""
        diagnostics = {
            "generated_at": datetime.now().isoformat(),
            "progress": self.get_learning_progress(),
            "recent_scores": self.quality_scores[-20:],
            "failure_history": self.failed_specs[-50:]
        }
        
        try:
            self.diagnostics_file.write_text(json.dumps(diagnostics, indent=2))
        except Exception:
            pass
            
        return diagnostics
    
    def load_diagnostics(self) -> Optional[Dict]:
        """Load existing diagnostics from disk"""
        if self.diagnostics_file.exists():
            try:
                return json.loads(self.diagnostics_file.read_text())
            except Exception:
                return None
        return None
    
    def get_failure_patterns(self) -> Dict:
        """Analyze failure patterns for learning"""
        failures = [s for s in self.quality_scores if s["score"] == 0]
        
        return {
            "total_failures": len(failures),
            "failed_spec_names": list(set(s["spec"] for s in failures)),
            "recent_failures": failures[-10:] if failures else []
        }
