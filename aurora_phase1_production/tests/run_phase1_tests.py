#!/usr/bin/env python3
"""
Aurora Phase-1 Automated Test Script
Runs the full generate -> inspect -> test -> promote loop and generates audit report.
"""

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from inspector.inspector import CodeInspector
from lifecycle.lifecycle import LifecycleRunner
from module_generator.helpers import CandidateGenerator, PromoteManager
from rule_engine.rule_engine import RuleEngine
from tools.make_550_manifest import generate_manifest

from tools.generate_modules import generate_all_modules


def run_phase1_tests(count: int = 10, output_dir: str = None, audit_file: str = None) -> dict:
    """Run full Phase-1 test suite"""

    start_time = time.time()
    output_dir = Path(output_dir or "test_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "started": datetime.now(UTC).isoformat(),
        "module_count": count,
        "phases": {},
        "summary": {},
    }

    print("=" * 60)
    print("Aurora Phase-1 Test Suite")
    print(f"Modules: {count}")
    print(f"Output: {output_dir}")
    print("=" * 60)

    print("\n[PHASE 1] Generating manifest...")
    manifest_path = output_dir / "test_manifest.json"
    manifest = generate_manifest(count)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    results["phases"]["manifest"] = {
        "total_modules": manifest["total_modules"],
        "categories": manifest["categories"],
        "checksum": manifest["manifest_checksum"],
        "path": str(manifest_path),
    }
    print(f"  Generated manifest with {manifest['total_modules']} modules")
    print(f"  Categories: {', '.join(manifest['categories'])}")

    print("\n[PHASE 2] Generating module files...")
    modules_dir = output_dir / "generated_modules"
    gen_result = generate_all_modules(str(manifest_path), str(modules_dir), force=True)

    results["phases"]["generation"] = {
        "total": gen_result["total"],
        "output_dir": gen_result["output_dir"],
        "registry": gen_result["registry"],
    }
    print(f"  Generated {gen_result['total']} modules to {modules_dir}")

    print("\n[PHASE 3] Inspecting generated modules...")
    inspector = CodeInspector(strict=False)
    inspection_results = []
    safe_count = 0
    unsafe_count = 0

    for module_info in gen_result["results"]:
        for file_path in module_info.get("files", []):
            result = inspector.inspect(file_path)
            inspection_results.append(
                {
                    "path": result.path,
                    "safe": result.safe,
                    "score": result.score,
                    "issue_count": result.issue_count,
                    "max_severity": result.max_severity,
                }
            )
            if result.safe:
                safe_count += 1
            else:
                unsafe_count += 1

    summary = inspector.get_summary(
        [inspector.inspect_code(open(r["path"]).read(), r["path"]) for r in inspection_results]
    )

    results["phases"]["inspection"] = {
        "total_files": len(inspection_results),
        "safe": safe_count,
        "unsafe": unsafe_count,
        "pass_rate": (safe_count / len(inspection_results) * 100) if inspection_results else 0,
        "summary": summary,
    }
    print(f"  Inspected {len(inspection_results)} files")
    print(f"  Safe: {safe_count}, Unsafe: {unsafe_count}")
    print(f"  Pass rate: {results['phases']['inspection']['pass_rate']:.1f}%")

    print("\n[PHASE 4] Running rule engine evaluation...")
    rule_engine = RuleEngine()
    rule_results = []

    for result in inspection_results[:10]:
        context = {
            "severity": result["max_severity"],
            "inspection_passed": result["safe"],
            "security_score": result["score"],
            "failure_count": 0,
            "timeout_count": 0,
            "execution_time": 100,
            "memory_usage": 64,
            "test_passed": True,
        }

        evaluation = rule_engine.evaluate(context)
        rule_results.append(
            {
                "path": result["path"],
                "rules_matched": evaluation.rules_matched,
                "max_severity": evaluation.max_severity,
                "recommended_action": evaluation.recommended_action,
            }
        )

    results["phases"]["rule_evaluation"] = {
        "evaluations": len(rule_results),
        "statistics": rule_engine.get_statistics(),
    }
    print(f"  Evaluated {len(rule_results)} modules")
    print(f"  Statistics: {rule_engine.get_statistics()}")

    print("\n[PHASE 5] Running lifecycle tests...")
    lifecycle_runner = LifecycleRunner(modules_dir=str(modules_dir))
    lifecycle_results = []
    success_count = 0
    fail_count = 0

    for module in manifest["modules"][: min(5, count)]:
        module_id = module["id"]
        category = module["category"]

        try:
            result = lifecycle_runner.run_module(
                module_id=module_id,
                category=category,
                config={"timeout_ms": 5000},
                payload={"action": "test", "data": {}},
                timeout=10.0,
            )

            lifecycle_results.append(
                {
                    "module_id": module_id,
                    "category": category,
                    "success": result.get("success", False),
                    "duration_ms": result.get("total_duration_ms", 0),
                }
            )

            if result.get("success"):
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            lifecycle_results.append(
                {"module_id": module_id, "category": category, "success": False, "error": str(e)}
            )
            fail_count += 1

    results["phases"]["lifecycle"] = {
        "total_tests": len(lifecycle_results),
        "passed": success_count,
        "failed": fail_count,
        "pass_rate": (success_count / len(lifecycle_results) * 100) if lifecycle_results else 0,
        "summary": lifecycle_runner.get_summary(),
        "results": lifecycle_results,
    }
    print(f"  Tested {len(lifecycle_results)} modules")
    print(f"  Passed: {success_count}, Failed: {fail_count}")

    print("\n[PHASE 6] Testing candidate generation and promotion...")
    candidates_dir = output_dir / "candidates"
    production_dir = output_dir / "production"
    snapshots_dir = output_dir / "snapshots"

    generator = CandidateGenerator(str(candidates_dir))
    promote_mgr = PromoteManager(
        candidates_dir=str(candidates_dir),
        production_dir=str(production_dir),
        snapshots_dir=str(snapshots_dir),
    )

    promotion_results = []

    for i in range(min(3, count)):
        module_id = f"test_{i:04d}"
        category = manifest["modules"][i % len(manifest["modules"])]["category"]
        driver = manifest["modules"][i % len(manifest["modules"])]["driver"]

        gen_result = generator.generate(module_id, category, driver)

        if gen_result.success:
            promote_result = promote_mgr.promote(module_id, category)
            promotion_results.append(
                {
                    "module_id": module_id,
                    "category": category,
                    "generated": True,
                    "promoted": promote_result.promoted,
                    "files": promote_result.files_promoted,
                }
            )

            promote_result2 = promote_mgr.promote(module_id, category)
            if promote_result2.snapshots_created:
                promotion_results[-1]["snapshot_created"] = True

    results["phases"]["promotion"] = {
        "total_promotions": len(promotion_results),
        "successful": sum(1 for r in promotion_results if r.get("promoted")),
        "with_snapshots": sum(1 for r in promotion_results if r.get("snapshot_created")),
        "results": promotion_results,
    }
    print(f"  Generated and promoted {len(promotion_results)} test modules")

    total_duration = time.time() - start_time
    results["completed"] = datetime.now(UTC).isoformat()
    results["duration_seconds"] = total_duration

    total_tests = (
        results["phases"]["inspection"]["total_files"]
        + results["phases"]["rule_evaluation"]["evaluations"]
        + results["phases"]["lifecycle"]["total_tests"]
        + results["phases"]["promotion"]["total_promotions"]
    )

    total_passed = (
        results["phases"]["inspection"]["safe"]
        + sum(1 for r in rule_results if r["recommended_action"] in ["notify", "ignore"])
        + results["phases"]["lifecycle"]["passed"]
        + results["phases"]["promotion"]["successful"]
    )

    results["summary"] = {
        "total_tests": total_tests,
        "total_passed": total_passed,
        "overall_pass_rate": (total_passed / total_tests * 100) if total_tests else 0,
        "duration_seconds": total_duration,
        "modules_generated": results["phases"]["generation"]["total"],
        "files_inspected": results["phases"]["inspection"]["total_files"],
        "lifecycle_tests": results["phases"]["lifecycle"]["total_tests"],
        "promotions": results["phases"]["promotion"]["total_promotions"],
    }

    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Duration: {total_duration:.2f} seconds")
    print(f"  Modules generated: {results['summary']['modules_generated']}")
    print(f"  Files inspected: {results['summary']['files_inspected']}")
    print(f"  Lifecycle tests: {results['summary']['lifecycle_tests']}")
    print(f"  Promotions: {results['summary']['promotions']}")
    print(f"  Overall pass rate: {results['summary']['overall_pass_rate']:.1f}%")
    print(f"{'=' * 60}")

    if audit_file:
        audit_path = Path(audit_file)
        with open(audit_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nAudit report saved to: {audit_path}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run Aurora Phase-1 automated tests")
    parser.add_argument(
        "--count", "-c", type=int, default=10, help="Number of modules to test (default: 10)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="test_output",
        help="Output directory for test artifacts",
    )
    parser.add_argument(
        "--audit-report", "-a", type=str, default=None, help="Path to save audit report JSON"
    )

    args = parser.parse_args()

    results = run_phase1_tests(
        count=args.count, output_dir=args.output, audit_file=args.audit_report
    )

    if results["summary"]["overall_pass_rate"] >= 80:
        print("\nTEST SUITE PASSED")
        return 0
    else:
        print("\nTEST SUITE FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
