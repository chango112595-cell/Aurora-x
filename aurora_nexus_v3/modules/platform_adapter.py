"""
Platform Adapter - Adapts Aurora to ANY platform
Supports Windows, Linux, macOS, Android, iOS, embedded systems
"""

import os
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Any


class PlatformType(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"
    FREEBSD = "freebsd"
    EMBEDDED = "embedded"
    UNKNOWN = "unknown"


@dataclass
class PlatformCapabilities:
    has_gui: bool = True
    has_network: bool = True
    has_filesystem: bool = True
    has_processes: bool = True
    has_systemd: bool = False
    has_launchd: bool = False
    has_docker: bool = False
    has_kubernetes: bool = False
    max_threads: int = 100
    supports_async: bool = True


class PlatformAdapter:
    """
    Adapts Aurora to ANY platform
    Auto-detects capabilities and provides unified interface
    """

    def __init__(self, core):
        self.core = core
        self.logger = core.logger.getChild("platform")
        self.platform_type = self._detect_platform()
        self.capabilities = self._detect_capabilities()
        self._adapters: dict[str, Any] = {}

    async def initialize(self):
        self.logger.info(f"Platform detected: {self.platform_type.value}")
        self.logger.info(
            f"Capabilities: GUI={self.capabilities.has_gui}, Docker={self.capabilities.has_docker}"
        )

    async def shutdown(self):
        """Cleanup platform adapter resources."""
        self.logger.info("Platform adapter shutting down")
        self._adapters.clear()
        self.logger.debug("Platform adapters cleared")

    def _detect_platform(self) -> PlatformType:
        system = platform.system().lower()

        if system == "windows":
            return PlatformType.WINDOWS
        elif system == "linux":
            if self._is_android():
                return PlatformType.ANDROID
            return PlatformType.LINUX
        elif system == "darwin":
            if self._is_ios():
                return PlatformType.IOS
            return PlatformType.MACOS
        elif system == "freebsd":
            return PlatformType.FREEBSD
        else:
            return PlatformType.UNKNOWN

    def _is_android(self) -> bool:
        return "ANDROID_ROOT" in os.environ or os.path.exists("/system/build.prop")

    def _is_ios(self) -> bool:
        return platform.machine().startswith("iPhone") or platform.machine().startswith("iPad")

    def _detect_capabilities(self) -> PlatformCapabilities:
        caps = PlatformCapabilities()

        if self.platform_type == PlatformType.LINUX:
            caps.has_systemd = os.path.exists("/run/systemd/system")
            caps.has_docker = self._check_docker()
            caps.has_kubernetes = self._check_kubernetes()

        elif self.platform_type == PlatformType.MACOS:
            caps.has_launchd = True
            caps.has_docker = self._check_docker()

        elif self.platform_type == PlatformType.WINDOWS:
            caps.has_docker = self._check_docker()

        elif self.platform_type == PlatformType.EMBEDDED:
            caps.has_gui = False
            caps.max_threads = 10

        return caps

    def _check_docker(self) -> bool:
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def _check_kubernetes(self) -> bool:
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_home_dir(self) -> str:
        return os.path.expanduser("~")

    def get_temp_dir(self) -> str:
        import tempfile

        return tempfile.gettempdir()

    def get_config_dir(self) -> str:
        if self.platform_type == PlatformType.WINDOWS:
            return os.path.join(os.environ.get("APPDATA", ""), "Aurora")
        elif self.platform_type == PlatformType.MACOS:
            return os.path.expanduser("~/Library/Application Support/Aurora")
        else:
            return os.path.expanduser("~/.config/aurora")

    def get_data_dir(self) -> str:
        if self.platform_type == PlatformType.WINDOWS:
            return os.path.join(os.environ.get("LOCALAPPDATA", ""), "Aurora")
        elif self.platform_type == PlatformType.MACOS:
            return os.path.expanduser("~/Library/Application Support/Aurora/Data")
        else:
            return os.path.expanduser("~/.local/share/aurora")

    async def run_command(self, cmd: list[str], timeout: int = 30) -> dict[str, Any]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_environment_info(self) -> dict[str, Any]:
        return {
            "platform": self.platform_type.value,
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "node_name": platform.node(),
            "capabilities": {
                "gui": self.capabilities.has_gui,
                "network": self.capabilities.has_network,
                "docker": self.capabilities.has_docker,
                "kubernetes": self.capabilities.has_kubernetes,
                "systemd": self.capabilities.has_systemd,
                "launchd": self.capabilities.has_launchd,
            },
        }

    def get_path_separator(self) -> str:
        return os.sep

    def normalize_path(self, path: str) -> str:
        return os.path.normpath(path)
