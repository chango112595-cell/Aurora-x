#!/usr/bin/env python3
"""
Aurora OS Detector - Universal OS and Hardware Detection
Enhanced with universal OS detection, expanded CPU/GPU detection,
better logging, and fallback routines.
"""

import platform
import sys
import shutil
import logging

try:
    import psutil
except ImportError:
    psutil = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuroraOSDetector:
    # Added enhanced hardware scan
    def scan_hardware_extended(self):
        return {
            "cpu": platform.processor(),
            "architecture": platform.machine(),
            "gpu": self._detect_gpu(),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2) if psutil else 0
        }

    def is_embedded_system(self):
        boards = ["raspberry", "arduino", "jetson", "esp32"]
        rel = platform.release().lower()
        return any(b in rel for b in boards)

    def _detect_gpu(self):
        """Attempt to detect GPU information"""
        try:
            import subprocess
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'VGA' in line or 'GPU' in line or '3D' in line:
                    return line.strip()
        except Exception:
            pass
        return "unknown"

    def detect_os(self):
        """Detect the current operating system"""
        # Enhanced OS mapping
        if "ANDROID" in platform.release().upper():
            return "android"
        if "IOS" in platform.release().upper():
            return "ios"

        system = platform.system().lower()
        if system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        elif system == "windows":
            return "windows"

        if sys.platform.startswith("freebsd"):
            return "freebsd"

        return "unknown"

    def detect_package_manager(self):
        """Detect the available package manager"""
        pm_map = {
            "apt": "debian",
            "dnf": "fedora",
            "yum": "rhel",
            "brew": "macos",
            "choco": "windows",
            "apk": "alpine",
            "pacman": "arch"
        }
        pm_map.update({"apk": "alpine", "pacman": "arch"})

        for pm, distro in pm_map.items():
            if shutil.which(pm):
                return pm, distro
        return None, "unknown"

    def get_system_summary(self):
        """Get a comprehensive system summary"""
        pm, distro = self.detect_package_manager()
        summary = {
            "os": self.detect_os(),
            "distro": distro,
            "package_manager": pm,
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "is_embedded": self.is_embedded_system()
        }
        summary["hardware_extended"] = self.scan_hardware_extended()
        return summary


def main():
    detector = AuroraOSDetector()
    summary = detector.get_system_summary()
    logger.info("Aurora OS Detection Results:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    return summary


if __name__ == "__main__":
    main()
