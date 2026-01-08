"""
Aurora Nexus V3 Configuration
Adaptive configuration system for all platforms
"""

import os
import platform
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from aurora_nexus_v3.utils.atomic_io import atomic_json_write, load_snapshot


@dataclass
class ResourceLimits:
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    max_threads: int = 100
    max_services: int = 1000
    max_ports: int = 500


@dataclass
class NetworkConfig:
    api_host: str = "0.0.0.0"
    api_port: int = 5002  # Changed from 5000 to avoid conflict with main app
    websocket_port: int = 5003
    discovery_port: int = 5353
    mesh_port: int = 6000
    enable_mdns: bool = True
    enable_upnp: bool = True


@dataclass
class SecurityConfig:
    enable_tls: bool = True
    require_auth: bool = True
    api_key: str | None = None
    jwt_secret: str | None = None
    allowed_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class NexusConfig:
    node_id: str = ""
    node_name: str = "aurora-nexus"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    data_dir: str = ".aurora_nexus"
    resources: ResourceLimits = field(default_factory=ResourceLimits)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    platform_info: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.node_id:
            import uuid

            self.node_id = str(uuid.uuid4())[:8]

        self.platform_info = {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        }

        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "NexusConfig":
        config = cls()
        config.environment = os.getenv("AURORA_ENV", "development")
        config.debug = os.getenv("AURORA_DEBUG", "1") == "1"
        config.log_level = os.getenv("AURORA_LOG_LEVEL", "INFO")
        config.network.api_port = int(os.getenv("AURORA_NEXUS_PORT", "5002"))
        config.security.api_key = os.getenv("AURORA_API_KEY")
        return config

    @classmethod
    def from_file(cls, path: str) -> "NexusConfig":
        data = load_snapshot(path, {})
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

    def save(self, path: str | None = None):
        if path is None:
            path = os.path.join(self.data_dir, "config.json")

        data = {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
        }

        atomic_json_write(path, data)

    def get_device_tier(self) -> str:
        total_memory = self._get_total_memory_mb()

        if total_memory >= 4096:
            return "full"
        elif total_memory >= 1024:
            return "standard"
        elif total_memory >= 256:
            return "lite"
        else:
            return "micro"

    def _get_total_memory_mb(self) -> int:
        try:
            import psutil

            return int(psutil.virtual_memory().total / (1024 * 1024))
        except ImportError:
            return 2048
