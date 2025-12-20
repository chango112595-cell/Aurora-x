"""
Aurora Pack 11: Device Mesh

Production-ready device discovery and mesh networking system.
Manages multi-device coordination, communication, and synchronization.

Author: Aurora AI System
Version: 2.0.0
"""

import os
import json
import socket
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib

PACK_ID = "pack11"
PACK_NAME = "Device Mesh"
PACK_VERSION = "2.0.0"


class DeviceStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    CONNECTING = "connecting"
    BUSY = "busy"
    ERROR = "error"


class MessageType(Enum):
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    DATA = "data"
    COMMAND = "command"
    RESPONSE = "response"
    SYNC = "sync"


@dataclass
class DeviceInfo:
    device_id: str
    name: str
    address: str
    port: int
    status: DeviceStatus = DeviceStatus.OFFLINE
    capabilities: List[str] = field(default_factory=list)
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeshMessage:
    message_id: str
    message_type: MessageType
    source_id: str
    target_id: str
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl: int = 3


class DeviceRegistry:
    def __init__(self, registry_path: str = "/tmp/aurora_mesh/registry"):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.devices: Dict[str, DeviceInfo] = {}
        self._lock = threading.Lock()
        self._load_registry()
    
    def _load_registry(self):
        registry_file = self.registry_path / "devices.json"
        if registry_file.exists():
            data = json.loads(registry_file.read_text())
            for device_id, info in data.items():
                info["status"] = DeviceStatus(info.get("status", "offline"))
                self.devices[device_id] = DeviceInfo(**info)
    
    def _save_registry(self):
        registry_file = self.registry_path / "devices.json"
        data = {}
        for device_id, device in self.devices.items():
            data[device_id] = {
                "device_id": device.device_id,
                "name": device.name,
                "address": device.address,
                "port": device.port,
                "status": device.status.value,
                "capabilities": device.capabilities,
                "last_seen": device.last_seen,
                "metadata": device.metadata
            }
        registry_file.write_text(json.dumps(data, indent=2))
    
    def register(self, device: DeviceInfo) -> bool:
        with self._lock:
            self.devices[device.device_id] = device
            self._save_registry()
        return True
    
    def unregister(self, device_id: str) -> bool:
        with self._lock:
            if device_id in self.devices:
                del self.devices[device_id]
                self._save_registry()
                return True
        return False
    
    def update_status(self, device_id: str, status: DeviceStatus):
        with self._lock:
            if device_id in self.devices:
                self.devices[device_id].status = status
                self.devices[device_id].last_seen = datetime.now().isoformat()
                self._save_registry()
    
    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        return self.devices.get(device_id)
    
    def get_online_devices(self) -> List[DeviceInfo]:
        return [d for d in self.devices.values() if d.status == DeviceStatus.ONLINE]
    
    def get_all_devices(self) -> List[DeviceInfo]:
        return list(self.devices.values())
    
    def find_by_capability(self, capability: str) -> List[DeviceInfo]:
        return [d for d in self.devices.values() 
                if capability in d.capabilities and d.status == DeviceStatus.ONLINE]


class MessageRouter:
    def __init__(self, local_device_id: str):
        self.local_device_id = local_device_id
        self.message_handlers: Dict[MessageType, List[Callable]] = {
            msg_type: [] for msg_type in MessageType
        }
        self.message_history: List[MeshMessage] = []
        self.seen_messages: Set[str] = set()
        self._lock = threading.Lock()
        self._message_counter = 0
    
    def register_handler(self, message_type: MessageType, handler: Callable):
        self.message_handlers[message_type].append(handler)
    
    def create_message(self, message_type: MessageType, target_id: str,
                       payload: Dict[str, Any]) -> MeshMessage:
        with self._lock:
            self._message_counter += 1
            message_id = hashlib.md5(
                f"{self.local_device_id}{self._message_counter}{time.time()}".encode()
            ).hexdigest()[:16]
        
        return MeshMessage(
            message_id=message_id,
            message_type=message_type,
            source_id=self.local_device_id,
            target_id=target_id,
            payload=payload
        )
    
    def route_message(self, message: MeshMessage) -> bool:
        with self._lock:
            if message.message_id in self.seen_messages:
                return False
            self.seen_messages.add(message.message_id)
            self.message_history.append(message)
            if len(self.seen_messages) > 10000:
                oldest = list(self.seen_messages)[:5000]
                self.seen_messages = set(list(self.seen_messages)[5000:])
        
        if message.target_id == self.local_device_id or message.target_id == "*":
            self._handle_message(message)
            return True
        
        if message.ttl > 0:
            message.ttl -= 1
            return True
        
        return False
    
    def _handle_message(self, message: MeshMessage):
        handlers = self.message_handlers.get(message.message_type, [])
        for handler in handlers:
            try:
                handler(message)
            except Exception:
                pass
    
    def get_message_stats(self) -> Dict[str, int]:
        with self._lock:
            return {
                "total_routed": len(self.message_history),
                "unique_seen": len(self.seen_messages)
            }


class MeshNode:
    def __init__(self, device_id: str, name: str, port: int = 9000):
        self.device_id = device_id
        self.name = name
        self.port = port
        self.address = self._get_local_address()
        
        self.registry = DeviceRegistry()
        self.router = MessageRouter(device_id)
        
        self.capabilities: List[str] = ["compute", "storage", "relay"]
        self.running = False
        self._server_thread: Optional[threading.Thread] = None
        
        self._register_default_handlers()
    
    def _get_local_address(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            addr = s.getsockname()[0]
            s.close()
            return addr
        except Exception:
            return "127.0.0.1"
    
    def _register_default_handlers(self):
        self.router.register_handler(MessageType.HEARTBEAT, self._handle_heartbeat)
        self.router.register_handler(MessageType.DISCOVERY, self._handle_discovery)
        self.router.register_handler(MessageType.COMMAND, self._handle_command)
    
    def _handle_heartbeat(self, message: MeshMessage):
        source_id = message.source_id
        self.registry.update_status(source_id, DeviceStatus.ONLINE)
    
    def _handle_discovery(self, message: MeshMessage):
        device_data = message.payload.get("device_info", {})
        if device_data:
            device_data["status"] = DeviceStatus(device_data.get("status", "online"))
            device = DeviceInfo(**device_data)
            self.registry.register(device)
    
    def _handle_command(self, message: MeshMessage):
        command = message.payload.get("command")
        response_payload = {"status": "received", "command": command}
        response = self.router.create_message(
            MessageType.RESPONSE,
            message.source_id,
            response_payload
        )
        self.router.route_message(response)
    
    def start(self):
        self.running = True
        
        local_device = DeviceInfo(
            device_id=self.device_id,
            name=self.name,
            address=self.address,
            port=self.port,
            status=DeviceStatus.ONLINE,
            capabilities=self.capabilities
        )
        self.registry.register(local_device)
    
    def stop(self):
        self.running = False
        self.registry.update_status(self.device_id, DeviceStatus.OFFLINE)
    
    def discover_devices(self) -> List[DeviceInfo]:
        return self.registry.get_online_devices()
    
    def send_message(self, target_id: str, message_type: MessageType,
                     payload: Dict[str, Any]) -> bool:
        message = self.router.create_message(message_type, target_id, payload)
        return self.router.route_message(message)
    
    def broadcast(self, message_type: MessageType, payload: Dict[str, Any]) -> int:
        devices = self.registry.get_online_devices()
        sent = 0
        for device in devices:
            if device.device_id != self.device_id:
                if self.send_message(device.device_id, message_type, payload):
                    sent += 1
        return sent
    
    def send_heartbeat(self):
        return self.broadcast(MessageType.HEARTBEAT, {"timestamp": datetime.now().isoformat()})
    
    def get_mesh_status(self) -> Dict[str, Any]:
        devices = self.registry.get_all_devices()
        online = [d for d in devices if d.status == DeviceStatus.ONLINE]
        
        return {
            "local_device": {
                "id": self.device_id,
                "name": self.name,
                "address": self.address,
                "port": self.port
            },
            "mesh_stats": {
                "total_devices": len(devices),
                "online_devices": len(online),
                "capabilities": self.capabilities
            },
            "message_stats": self.router.get_message_stats(),
            "running": self.running
        }


class DeviceMesh:
    _instance: Optional['DeviceMesh'] = None
    
    def __init__(self, device_name: str = "aurora-node", port: int = 9000):
        device_id = hashlib.md5(
            f"{device_name}{socket.gethostname()}".encode()
        ).hexdigest()[:12]
        
        self.node = MeshNode(device_id, device_name, port)
    
    @classmethod
    def get_instance(cls, device_name: str = "aurora-node") -> 'DeviceMesh':
        if cls._instance is None:
            cls._instance = cls(device_name)
        return cls._instance
    
    def start(self):
        self.node.start()
    
    def stop(self):
        self.node.stop()
    
    def discover(self) -> List[Dict[str, Any]]:
        devices = self.node.discover_devices()
        return [
            {
                "id": d.device_id,
                "name": d.name,
                "address": d.address,
                "status": d.status.value,
                "capabilities": d.capabilities
            }
            for d in devices
        ]
    
    def send_command(self, target_id: str, command: str, 
                     params: Dict[str, Any] = None) -> bool:
        return self.node.send_message(
            target_id,
            MessageType.COMMAND,
            {"command": command, "params": params or {}}
        )
    
    def get_status(self) -> Dict[str, Any]:
        return self.node.get_mesh_status()


def get_pack_info():
    return {
        "id": PACK_ID,
        "name": PACK_NAME,
        "version": PACK_VERSION,
        "status": "production",
        "components": [
            "DeviceRegistry",
            "MessageRouter",
            "MeshNode",
            "DeviceMesh"
        ],
        "features": [
            "Device discovery and registration",
            "Message routing with TTL",
            "Heartbeat monitoring",
            "Capability-based device lookup",
            "Broadcast messaging",
            "Persistent device registry"
        ]
    }
