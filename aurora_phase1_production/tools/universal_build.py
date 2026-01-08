#!/usr/bin/env python3
"""
Aurora-X Ultra Universal Build Script
Cross-platform build script for Linux, macOS, Windows, WSL
Supports: GPU acceleration, auto-detection, parallel generation
"""

import argparse
import json
import logging
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class UniversalBuilder:
    """Universal build system for Aurora-X Ultra"""

    REQUIRED_PYTHON_VERSION = (3, 8)
    REQUIRED_NODE_VERSION = 16

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.platform_info = self._detect_platform()
        self.checks = {}
        self.build_results = {}

    def _detect_platform(self) -> dict:
        """Detect platform information"""
        system = platform.system()
        release = platform.release().lower()

        return {
            "system": system,
            "release": release,
            "machine": platform.machine(),
            "is_windows": system == "Windows",
            "is_macos": system == "Darwin",
            "is_linux": system == "Linux",
            "is_wsl": "microsoft" in release or "wsl" in release,
            "python_version": sys.version_info[:3],
            "python_path": sys.executable,
        }

    def check_python(self) -> dict:
        """Check Python version and dependencies"""
        version = sys.version_info
        ok = version >= self.REQUIRED_PYTHON_VERSION

        packages = {
            "torch": self._check_package("torch"),
            "numpy": self._check_package("numpy"),
        }

        result = {
            "ok": ok,
            "version": f"{version.major}.{version.minor}.{version.micro}",
            "required": f"{self.REQUIRED_PYTHON_VERSION[0]}.{self.REQUIRED_PYTHON_VERSION[1]}+",
            "path": sys.executable,
            "packages": packages,
        }

        self.checks["python"] = result
        return result

    def _check_package(self, name: str) -> dict:
        """Check if a Python package is installed"""
        try:
            module = __import__(name)
            version = getattr(module, "__version__", "unknown")
            return {"installed": True, "version": version}
        except ImportError:
            return {"installed": False, "version": None}

    def check_node(self) -> dict:
        """Check Node.js version"""
        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version_str = result.stdout.strip().lstrip("v")
                major = int(version_str.split(".")[0])
                ok = major >= self.REQUIRED_NODE_VERSION

                npm_result = subprocess.run(
                    ["npm", "--version"], capture_output=True, text=True, timeout=10
                )
                npm_version = npm_result.stdout.strip() if npm_result.returncode == 0 else None

                result = {
                    "ok": ok,
                    "version": version_str,
                    "required": f"{self.REQUIRED_NODE_VERSION}+",
                    "npm_version": npm_version,
                }
                self.checks["node"] = result
                return result
        except Exception:
            pass

        result = {
            "ok": False,
            "version": None,
            "required": f"{self.REQUIRED_NODE_VERSION}+",
            "error": "Node.js not found",
        }
        self.checks["node"] = result
        return result

    def check_gpu(self) -> dict:
        """Check GPU availability and capabilities"""
        result = {
            "available": False,
            "cuda_available": False,
            "cuda_version": None,
            "gpu_count": 0,
            "gpus": [],
            "recommended_batch_size": 1,
        }

        try:
            import torch

            result["torch_available"] = True
            result["torch_version"] = torch.__version__

            if torch.cuda.is_available():
                result["available"] = True
                result["cuda_available"] = True
                result["cuda_version"] = torch.version.cuda
                result["gpu_count"] = torch.cuda.device_count()

                for i in range(torch.cuda.device_count()):
                    gpu_props = torch.cuda.get_device_properties(i)
                    result["gpus"].append(
                        {
                            "id": i,
                            "name": gpu_props.name,
                            "memory_gb": round(gpu_props.total_memory / 1e9, 2),
                            "compute_capability": f"{gpu_props.major}.{gpu_props.minor}",
                        }
                    )

                total_memory = sum(g["memory_gb"] for g in result["gpus"])
                result["recommended_batch_size"] = max(1, int(total_memory / 2))

            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                result["available"] = True
                result["mps_available"] = True
                result["gpus"].append(
                    {
                        "id": 0,
                        "name": "Apple Silicon (MPS)",
                        "memory_gb": "shared",
                        "compute_capability": "mps",
                    }
                )

        except ImportError:
            result["torch_available"] = False

        self.checks["gpu"] = result
        return result

    def run_all_checks(self) -> dict:
        """Run all system checks"""
        logger.info("Running system checks...")

        python_check = self.check_python()
        node_check = self.check_node()
        gpu_check = self.check_gpu()

        all_ok = python_check["ok"]

        return {
            "platform": self.platform_info,
            "python": python_check,
            "node": node_check,
            "gpu": gpu_check,
            "ready": all_ok,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def install_dependencies(self, gpu: bool = True) -> dict:
        """Install required dependencies"""
        logger.info("Installing dependencies...")
        results = {"python": [], "npm": []}

        python_deps = ["numpy"]
        if gpu:
            python_deps.append("torch")

        for dep in python_deps:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep], capture_output=True, timeout=300
                )
                results["python"].append({"package": dep, "status": "installed"})
            except Exception as e:
                results["python"].append({"package": dep, "status": "failed", "error": str(e)})

        return results

    def build_modules(
        self,
        output_dir: str = None,
        count: int = 550,
        create_zip: bool = True,
        with_registry: bool = True,
    ) -> dict:
        """Build Aurora modules"""
        from generate_aurora_modules import AuroraModuleGenerator

        output_dir = output_dir or "aurora_x"

        logger.info(f"Building {count} Aurora modules...")

        generator = AuroraModuleGenerator(output_dir=output_dir)
        result = generator.generate_all(create_zip=create_zip)

        if with_registry:
            registry_result = generator.generate_registry()
            result["registry"] = registry_result

        self.build_results["modules"] = result
        return result

    def build_phase1(self, output_dir: str = None) -> dict:
        """Build Phase-1 production bundle"""
        logger.info("Building Phase-1 production bundle...")

        output_dir = Path(output_dir) if output_dir else Path("phase1_build")
        output_dir.mkdir(parents=True, exist_ok=True)

        current_dir = Path(__file__).parent.parent

        components = [
            "tools",
            "aurora_nexus_v3",
            "inspector",
            "rule_engine",
            "lifecycle",
            "module_generator",
            "tests",
        ]

        copied = []
        for comp in components:
            src = current_dir / comp
            dst = output_dir / comp
            if src.exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                copied.append(comp)

        readme_src = current_dir / "README.md"
        if readme_src.exists():
            shutil.copy2(readme_src, output_dir / "README.md")

        result = {
            "success": True,
            "output_dir": str(output_dir),
            "components": copied,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self.build_results["phase1"] = result
        return result

    def full_build(self, output_dir: str = None, gpu: bool = True, module_count: int = 550) -> dict:
        """Run full build process"""
        logger.info("=" * 60)
        logger.info("Aurora-X Ultra Universal Build")
        logger.info("=" * 60)

        checks = self.run_all_checks()

        logger.info(f"Platform: {checks['platform']['system']}")
        logger.info(
            f"Python: {checks['python']['version']} - {'OK' if checks['python']['ok'] else 'FAIL'}"
        )
        logger.info(
            f"Node.js: {checks['node'].get('version', 'N/A')} - {'OK' if checks['node']['ok'] else 'Optional'}"
        )
        logger.info(
            f"GPU: {checks['gpu']['gpu_count']} available - {'CUDA' if checks['gpu']['cuda_available'] else 'CPU'}"
        )

        if not checks["ready"]:
            logger.error("System checks failed")
            return {"success": False, "checks": checks, "error": "System requirements not met"}

        output_dir = output_dir or "aurora_build"

        modules_result = self.build_modules(
            output_dir=f"{output_dir}/aurora_x",
            count=module_count,
            create_zip=True,
            with_registry=True,
        )

        logger.info("=" * 60)
        logger.info("Build Complete!")
        logger.info("=" * 60)
        logger.info(f"Modules generated: {modules_result['total_modules']}")
        logger.info(f"Output: {modules_result['output_dir']}")
        if modules_result.get("zip_path"):
            logger.info(f"ZIP: {modules_result['zip_path']}")

        return {
            "success": True,
            "checks": checks,
            "modules": modules_result,
            "output_dir": output_dir,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def print_summary(self):
        """Print build summary"""
        print("\n" + "=" * 60)
        print("BUILD SUMMARY")
        print("=" * 60)

        print(f"\nPlatform: {self.platform_info['system']} ({self.platform_info['machine']})")

        if "python" in self.checks:
            py = self.checks["python"]
            print(f"Python: {py['version']} - {'PASS' if py['ok'] else 'FAIL'}")

        if "gpu" in self.checks:
            gpu = self.checks["gpu"]
            if gpu["available"]:
                print(f"GPU: {gpu['gpu_count']} device(s)")
                for g in gpu.get("gpus", []):
                    print(f"  - {g['name']} ({g['memory_gb']}GB)")
            else:
                print("GPU: Not available (CPU mode)")

        if "modules" in self.build_results:
            mod = self.build_results["modules"]
            print(f"\nModules: {mod['total_modules']} generated")
            print(f"Output: {mod['output_dir']}")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Aurora-X Ultra Universal Build Script")
    parser.add_argument("--output", "-o", type=str, default="aurora_build", help="Output directory")
    parser.add_argument(
        "--modules", type=int, default=550, help="Number of modules to generate (default: 550)"
    )
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU support")
    parser.add_argument("--check-only", action="store_true", help="Run system checks only")
    parser.add_argument("--install-deps", action="store_true", help="Install dependencies")

    args = parser.parse_args()

    builder = UniversalBuilder()

    if args.check_only:
        checks = builder.run_all_checks()
        print(json.dumps(checks, indent=2))
        return

    if args.install_deps:
        result = builder.install_dependencies(gpu=not args.no_gpu)
        print(json.dumps(result, indent=2))
        return

    result = builder.full_build(
        output_dir=args.output, gpu=not args.no_gpu, module_count=args.modules
    )

    builder.print_summary()

    if result["success"]:
        print("\nBuild completed successfully!")
        sys.exit(0)
    else:
        print(f"\nBuild failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
