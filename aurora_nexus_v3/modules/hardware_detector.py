"""
Hardware Detector - Understands device capabilities
Detects CPU, memory, storage, network, GPU, and sensors
"""

import logging
import platform
import socket
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol, Tuple


@dataclass
class CPUInfo:
    cores_physical: int = 1
    cores_logical: int = 1
    architecture: str = "unknown"
    frequency_mhz: float = 0
    model: str = "unknown"


@dataclass
class MemoryInfo:
    total_mb: int = 0
    available_mb: int = 0
    used_mb: int = 0
    percent_used: float = 0


@dataclass 
class StorageInfo:
    total_gb: float = 0
    available_gb: float = 0
    used_gb: float = 0
    mount_point: str = "/"


@dataclass
class NetworkInterface:
    name: str = ""
    address: str = ""
    mac: str = ""
    is_up: bool = False
    speed_mbps: int = 0


@dataclass
class HardwareProfile:
    cpu: CPUInfo = field(default_factory=CPUInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    storage: List[StorageInfo] = field(default_factory=list)
    network: List[NetworkInterface] = field(default_factory=list)
    gpu_available: bool = False
    gpu_details: Dict[str, Any] = field(default_factory=dict)
    battery_powered: bool = False
    battery_percent: Optional[float] = None
    capability_score: int = 0


class HardwareCore(Protocol):
    logger: logging.Logger


def detect_cuda_details(logger: Optional[logging.Logger] = None) -> Dict[str, Any]:
    details: Dict[str, Any] = {
        "available": False,
        "cuda_available": False,
        "device_count": 0,
        "device_name": None,
        "cuda_version": None,
        "driver_version": None,
        "source": None,
        "errors": []
    }

    try:
        import torch
    except ImportError:
        torch = None

    if torch:
        try:
            details["cuda_available"] = torch.cuda.is_available()
            details["cuda_version"] = torch.version.cuda
            details["source"] = "torch"
            if details["cuda_available"]:
                details["device_count"] = torch.cuda.device_count()
                if details["device_count"] > 0:
                    details["device_name"] = torch.cuda.get_device_name(0)
                    details["available"] = True
                else:
                    details["errors"].append("CUDA reported available but no devices detected")
            elif details["cuda_version"] is None:
                details["errors"].append("Torch CUDA runtime not available")
        except Exception as exc:
            details["errors"].append(f"Torch CUDA check failed: {exc}")
            if logger:
                logger.debug("Torch CUDA check failed: %s", exc)

    if not details["available"]:
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout:
                first_line = result.stdout.strip().splitlines()[0]
                name, driver = [part.strip() for part in first_line.split(",", 1)]
                details["device_name"] = details["device_name"] or name
                details["driver_version"] = driver or details["driver_version"]
                details["available"] = True
                details["source"] = details["source"] or "nvidia-smi"
        except Exception as exc:
            details["errors"].append(f"nvidia-smi check failed: {exc}")
            if logger:
                logger.debug("nvidia-smi check failed: %s", exc)

    return details


class HardwareDetector:
    """
    Detects hardware capabilities and scores device
    Determines what features Aurora can enable
    """
    
    CAPABILITY_THRESHOLDS: Dict[str, int] = {
        "full": 80,
        "standard": 50,
        "lite": 25,
        "micro": 0
    }
    
    def __init__(self, core: Any):
        self.core = core
        self.logger: logging.Logger = core.logger.getChild("hardware")
        self.profile: Optional[HardwareProfile] = None
    
    async def initialize(self) -> None:
        self.logger.info("Detecting hardware capabilities...")
        self.profile = await self.detect()
        self.logger.info(f"Hardware detected: {self.profile.cpu.cores_logical} cores, "
                        f"{self.profile.memory.total_mb}MB RAM, "
                        f"Score: {self.profile.capability_score}/100")
    
    async def shutdown(self) -> None:
        """Cleanup hardware detector resources."""
        self.logger.info("Hardware detector shutting down")
        self.profile = None
        self.logger.debug("Hardware profile cleared")
    
    async def detect(self) -> HardwareProfile:
        profile = HardwareProfile()
        profile.cpu = self._detect_cpu()
        profile.memory = self._detect_memory()
        profile.storage = self._detect_storage()
        profile.network = self._detect_network()
        profile.gpu_details = self._detect_gpu_details()
        profile.gpu_available = profile.gpu_details.get("available", False)
        profile.battery_powered, profile.battery_percent = self._detect_battery()
        profile.capability_score = self._calculate_score(profile)
        return profile
    
    def _detect_cpu(self) -> CPUInfo:
        info = CPUInfo()
        info.architecture = platform.machine()
        info.model = platform.processor() or "unknown"
        
        try:
            import multiprocessing
            info.cores_logical = multiprocessing.cpu_count()
            info.cores_physical = info.cores_logical // 2 or 1
        except Exception:
            info.cores_logical = 1
            info.cores_physical = 1
        
        try:
            import psutil
            freq = psutil.cpu_freq()
            if freq:
                info.frequency_mhz = freq.current
        except ImportError:
            self.logger.debug("psutil not available; CPU frequency detection skipped")
        
        return info
    
    def _detect_memory(self) -> MemoryInfo:
        info = MemoryInfo()
        
        try:
            import psutil
            mem = psutil.virtual_memory()
            info.total_mb = int(mem.total / (1024 * 1024))
            info.available_mb = int(mem.available / (1024 * 1024))
            info.used_mb = int(mem.used / (1024 * 1024))
            info.percent_used = mem.percent
        except ImportError:
            info.total_mb = 2048
            info.available_mb = 1024
        
        return info
    
    def _detect_storage(self) -> List[StorageInfo]:
        storage_list: List[StorageInfo] = []
        
        try:
            import psutil
            partitions = psutil.disk_partitions()
            for partition in partitions[:5]:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    storage = StorageInfo(
                        total_gb=usage.total / (1024 ** 3),
                        available_gb=usage.free / (1024 ** 3),
                        used_gb=usage.used / (1024 ** 3),
                        mount_point=partition.mountpoint
                    )
                    storage_list.append(storage)
                except Exception as exc:
                    self.logger.debug(
                        "Failed to read storage usage for %s: %s",
                        partition.mountpoint,
                        exc,
                    )
        except ImportError:
            storage_list.append(StorageInfo(total_gb=100, available_gb=50))
        
        return storage_list
    
    def _detect_network(self) -> List[NetworkInterface]:
        interfaces: List[NetworkInterface] = []
        af_packet = getattr(socket, "AF_PACKET", None)

        try:
            import psutil
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            
            for name, addr_list in addrs.items():
                if name.startswith("lo") or name.startswith("docker"):
                    continue
                
                iface = NetworkInterface(name=name)
                for addr in addr_list:
                    family = addr.family
                    family_name = getattr(family, "name", "")
                    if family in (socket.AF_INET, socket.AF_INET6) or family_name in ("AF_INET", "AF_INET6"):
                        iface.address = addr.address
                    elif af_packet and (family == af_packet or family_name == "AF_PACKET"):
                        iface.mac = addr.address
                
                if name in stats:
                    iface.is_up = stats[name].isup
                    iface.speed_mbps = stats[name].speed
                
                if iface.address:
                    interfaces.append(iface)
        except ImportError:
            interfaces.append(NetworkInterface(name="eth0", address="127.0.0.1", is_up=True))
        
        return interfaces
    
    def _detect_gpu_details(self) -> Dict[str, Any]:
        return detect_cuda_details(self.logger)
    
    def _detect_battery(self) -> Tuple[bool, Optional[float]]:
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return True, battery.percent
        except Exception as exc:
            self.logger.debug("Battery detection failed: %s", exc)
        return False, None
    
    def _calculate_score(self, profile: HardwareProfile) -> int:
        score = 0
        
        cpu_score = min(profile.cpu.cores_logical * 5, 30)
        score += cpu_score
        
        if profile.memory.total_mb >= 8192:
            score += 30
        elif profile.memory.total_mb >= 4096:
            score += 25
        elif profile.memory.total_mb >= 2048:
            score += 20
        elif profile.memory.total_mb >= 1024:
            score += 15
        elif profile.memory.total_mb >= 512:
            score += 10
        else:
            score += 5
        
        total_storage = sum(s.total_gb for s in profile.storage)
        if total_storage >= 500:
            score += 20
        elif total_storage >= 100:
            score += 15
        elif total_storage >= 50:
            score += 10
        else:
            score += 5
        
        if profile.network:
            score += 10
            if any(n.speed_mbps >= 1000 for n in profile.network):
                score += 5
        
        if profile.gpu_available:
            score += 5
        
        return min(score, 100)
    
    def get_device_tier(self) -> str:
        if not self.profile:
            return "unknown"
        
        score = self.profile.capability_score
        for tier, threshold in self.CAPABILITY_THRESHOLDS.items():
            if score >= threshold:
                return tier
        return "micro"
    
    def get_recommended_config(self) -> Dict[str, Any]:
        tier = self.get_device_tier()
        
        configs = {
            "full": {
                "max_threads": 100,
                "max_services": 1000,
                "enable_ml": True,
                "enable_mesh": True,
                "cache_size_mb": 512
            },
            "standard": {
                "max_threads": 50,
                "max_services": 500,
                "enable_ml": True,
                "enable_mesh": True,
                "cache_size_mb": 256
            },
            "lite": {
                "max_threads": 20,
                "max_services": 100,
                "enable_ml": False,
                "enable_mesh": True,
                "cache_size_mb": 64
            },
            "micro": {
                "max_threads": 5,
                "max_services": 20,
                "enable_ml": False,
                "enable_mesh": False,
                "cache_size_mb": 16
            }
        }
        
        return configs.get(tier, configs["lite"])
    
    async def get_info(self) -> Dict[str, Any]:
        if not self.profile:
            self.profile = await self.detect()
        
        profile = self.profile
        return {
            "cpu": {
                "cores_physical": profile.cpu.cores_physical,
                "cores_logical": profile.cpu.cores_logical,
                "architecture": profile.cpu.architecture,
                "model": profile.cpu.model
            },
            "memory": {
                "total_mb": profile.memory.total_mb,
                "available_mb": profile.memory.available_mb,
                "percent_used": profile.memory.percent_used
            },
            "storage": [
                {"mount": s.mount_point, "total_gb": s.total_gb, "available_gb": s.available_gb}
                for s in profile.storage
            ],
            "network": [
                {"name": n.name, "address": n.address, "is_up": n.is_up}
                for n in profile.network
            ],
            "gpu_available": profile.gpu_available,
            "gpu_details": profile.gpu_details,
            "battery": {
                "powered": profile.battery_powered,
                "percent": profile.battery_percent
            },
            "capability_score": profile.capability_score,
            "device_tier": self.get_device_tier()
        }
