#!/usr/bin/env python3
"""
Aurora Phase-1 File-Backed Registry & Locking (etcd optional)
Provides distributed-style registry with file-based fallback.
"""
import json
import os
import time
import fcntl
import hashlib
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class RegistryEntry:
    key: str
    value: Any
    version: int
    created: str
    modified: str
    ttl: Optional[int] = None
    expires: Optional[str] = None


class FileLock:
    """File-based distributed lock"""
    
    def __init__(self, lock_path: str, timeout: float = 10.0):
        self.lock_path = Path(lock_path)
        self.timeout = timeout
        self.lock_file = None
        self.acquired = False
    
    def acquire(self) -> bool:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.time()
        
        while time.time() - start < self.timeout:
            try:
                self.lock_file = open(self.lock_path, 'w')
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.lock_file.write(json.dumps({
                    "pid": os.getpid(),
                    "acquired": datetime.now(timezone.utc).isoformat()
                }))
                self.lock_file.flush()
                self.acquired = True
                return True
            except (IOError, OSError):
                if self.lock_file:
                    self.lock_file.close()
                time.sleep(0.1)
        
        return False
    
    def release(self):
        if self.lock_file and self.acquired:
            try:
                fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
                self.lock_file.close()
                if self.lock_path.exists():
                    self.lock_path.unlink()
            except (IOError, OSError):
                pass
            finally:
                self.acquired = False
                self.lock_file = None
    
    def __enter__(self):
        if not self.acquire():
            raise TimeoutError(f"Could not acquire lock: {self.lock_path}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


class EtcdStore:
    """File-backed key-value store with optional etcd backend"""
    
    def __init__(self, data_dir: str = None, use_etcd: bool = False, 
                 etcd_host: str = "localhost", etcd_port: int = 2379):
        self.data_dir = Path(data_dir or ".aurora_store")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.store_file = self.data_dir / "store.json"
        self.locks_dir = self.data_dir / "locks"
        self.locks_dir.mkdir(exist_ok=True)
        
        self.use_etcd = use_etcd
        self.etcd_client = None
        
        if use_etcd:
            try:
                import etcd3
                self.etcd_client = etcd3.client(host=etcd_host, port=etcd_port)
                logger.info("Connected to etcd")
            except ImportError:
                logger.warning("etcd3 not installed, using file backend")
                self.use_etcd = False
            except Exception as e:
                logger.warning(f"Could not connect to etcd: {e}, using file backend")
                self.use_etcd = False
        
        self._local_cache = {}
        self._cache_lock = threading.RLock()
        self._load_store()
    
    def _load_store(self):
        """Load store from file"""
        if self.store_file.exists():
            try:
                with open(self.store_file, 'r') as f:
                    data = json.load(f)
                    self._local_cache = {
                        k: RegistryEntry(**v) if isinstance(v, dict) else v 
                        for k, v in data.items()
                    }
            except (json.JSONDecodeError, IOError):
                self._local_cache = {}
    
    def _save_store(self):
        """Save store to file"""
        with self._cache_lock:
            data = {}
            for k, v in self._local_cache.items():
                if isinstance(v, RegistryEntry):
                    data[k] = asdict(v)
                else:
                    data[k] = v
            
            tmp_file = self.store_file.with_suffix('.tmp')
            with open(tmp_file, 'w') as f:
                json.dump(data, f, indent=2)
            tmp_file.rename(self.store_file)
    
    @contextmanager
    def lock(self, key: str, timeout: float = 10.0):
        """Acquire a distributed lock for a key"""
        lock_path = self.locks_dir / f"{hashlib.md5(key.encode()).hexdigest()}.lock"
        lock = FileLock(str(lock_path), timeout)
        
        try:
            with lock:
                yield
        finally:
            pass
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> RegistryEntry:
        """Store a value with optional TTL (seconds)"""
        now = datetime.now(timezone.utc).isoformat()
        
        with self._cache_lock:
            existing = self._local_cache.get(key)
            version = (existing.version + 1) if existing and isinstance(existing, RegistryEntry) else 1
            
            expires = None
            if ttl:
                expires = datetime.fromtimestamp(
                    time.time() + ttl, tz=timezone.utc
                ).isoformat()
            
            entry = RegistryEntry(
                key=key,
                value=value,
                version=version,
                created=existing.created if existing and isinstance(existing, RegistryEntry) else now,
                modified=now,
                ttl=ttl,
                expires=expires
            )
            
            self._local_cache[key] = entry
            self._save_store()
            
            if self.use_etcd and self.etcd_client:
                try:
                    self.etcd_client.put(key, json.dumps(asdict(entry)))
                except Exception as e:
                    logger.warning(f"etcd put failed: {e}")
            
            return entry
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """Get a value by key"""
        with self._cache_lock:
            entry = self._local_cache.get(key)
            
            if entry is None:
                return default
            
            if isinstance(entry, RegistryEntry):
                if entry.expires:
                    expires_dt = datetime.fromisoformat(entry.expires.replace('Z', '+00:00'))
                    if datetime.now(timezone.utc) > expires_dt:
                        self.delete(key)
                        return default
                return entry.value
            
            return entry
    
    def get_entry(self, key: str) -> Optional[RegistryEntry]:
        """Get full registry entry"""
        with self._cache_lock:
            entry = self._local_cache.get(key)
            if isinstance(entry, RegistryEntry):
                return entry
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        with self._cache_lock:
            if key in self._local_cache:
                del self._local_cache[key]
                self._save_store()
                
                if self.use_etcd and self.etcd_client:
                    try:
                        self.etcd_client.delete(key)
                    except Exception as e:
                        logger.warning(f"etcd delete failed: {e}")
                
                return True
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with optional prefix filter"""
        with self._cache_lock:
            if prefix:
                return [k for k in self._local_cache.keys() if k.startswith(prefix)]
            return list(self._local_cache.keys())
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._local_cache
    
    def compare_and_swap(self, key: str, expected_value: Any, new_value: Any) -> bool:
        """Atomic compare-and-swap operation"""
        with self.lock(key):
            current = self.get(key)
            if current == expected_value:
                self.put(key, new_value)
                return True
            return False
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Atomic increment operation"""
        with self.lock(key):
            current = self.get(key, 0)
            new_value = int(current) + amount
            self.put(key, new_value)
            return new_value
    
    def watch(self, key: str, callback, timeout: float = None):
        """Watch a key for changes (file-based polling)"""
        last_version = None
        start = time.time()
        
        while True:
            if timeout and (time.time() - start) > timeout:
                break
            
            entry = self.get_entry(key)
            if entry:
                if last_version is None or entry.version != last_version:
                    last_version = entry.version
                    callback(key, entry.value, entry.version)
            
            time.sleep(0.5)
    
    def register_module(self, module_id: str, module_data: Dict) -> RegistryEntry:
        """Register a module in the store"""
        key = f"/aurora/modules/{module_id}"
        module_data["registered"] = datetime.now(timezone.utc).isoformat()
        return self.put(key, module_data)
    
    def get_module(self, module_id: str) -> Optional[Dict]:
        """Get a registered module"""
        key = f"/aurora/modules/{module_id}"
        return self.get(key)
    
    def list_modules(self) -> List[str]:
        """List all registered module IDs"""
        keys = self.list_keys("/aurora/modules/")
        return [k.split("/")[-1] for k in keys]
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        now = datetime.now(timezone.utc)
        expired = []
        
        with self._cache_lock:
            for key, entry in self._local_cache.items():
                if isinstance(entry, RegistryEntry) and entry.expires:
                    expires_dt = datetime.fromisoformat(entry.expires.replace('Z', '+00:00'))
                    if now > expires_dt:
                        expired.append(key)
        
        for key in expired:
            self.delete(key)
        
        return len(expired)


def create_store(data_dir: str = None, use_etcd: bool = False) -> EtcdStore:
    return EtcdStore(data_dir=data_dir, use_etcd=use_etcd)


if __name__ == "__main__":
    store = EtcdStore(data_dir=".test_store")
    
    store.put("test/key1", {"name": "test", "value": 123})
    print(f"Stored: {store.get('test/key1')}")
    
    store.put("test/expires", "temporary", ttl=5)
    print(f"With TTL: {store.get('test/expires')}")
    
    store.register_module("0001", {"category": "connector", "status": "active"})
    print(f"Module: {store.get_module('0001')}")
    print(f"All modules: {store.list_modules()}")
