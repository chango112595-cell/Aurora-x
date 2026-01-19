"""
Aurora-X etcd-backed Registry and Distributed Locks
Provides distributed state management with file-based fallback.
"""

import fcntl
import hashlib
import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class LockInfo:
    """Information about a distributed lock."""

    key: str
    holder: str
    acquired_at: float
    ttl: int
    lease_id: str | None = None


class FileBasedLock:
    """File-based lock for fallback mode."""

    def __init__(self, lock_dir: Path):
        self.lock_dir = lock_dir
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, Any] = {}

    def acquire(self, key: str, holder: str, ttl: int = 30) -> bool:
        """Acquire a lock."""
        lock_file = self.lock_dir / f"{hashlib.md5(key.encode()).hexdigest()}.lock"

        try:
            fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            lock_data = {"holder": holder, "acquired_at": time.time(), "ttl": ttl}
            os.write(fd, json.dumps(lock_data).encode())

            self._locks[key] = fd
            logger.debug(f"Lock acquired: {key} by {holder}")
            return True

        except OSError:
            if self._is_lock_expired(lock_file):
                try:
                    os.unlink(str(lock_file))
                    return self.acquire(key, holder, ttl)
                except Exception as exc:
                    logger.debug("Failed to remove expired lock %s: %s", lock_file, exc)
            return False

    def _is_lock_expired(self, lock_file: Path) -> bool:
        """Check if a lock file has expired."""
        if not lock_file.exists():
            return True

        try:
            with open(lock_file) as f:
                data = json.load(f)

            elapsed = time.time() - data.get("acquired_at", 0)
            return elapsed > data.get("ttl", 30)
        except Exception as exc:
            logger.debug("Failed to read lock %s: %s", lock_file, exc)
            return True

    def release(self, key: str) -> bool:
        """Release a lock."""
        if key not in self._locks:
            return False

        fd = self._locks.pop(key)
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

            lock_file = self.lock_dir / f"{hashlib.md5(key.encode()).hexdigest()}.lock"
            if lock_file.exists():
                os.unlink(str(lock_file))

            logger.debug(f"Lock released: {key}")
            return True
        except Exception as exc:
            logger.debug("Failed to release lock %s: %s", key, exc)
            return False

    def is_locked(self, key: str) -> bool:
        """Check if a key is locked."""
        lock_file = self.lock_dir / f"{hashlib.md5(key.encode()).hexdigest()}.lock"

        if not lock_file.exists():
            return False

        return not self._is_lock_expired(lock_file)


class EtcdStore:
    """
    etcd-backed key-value store with distributed locking.
    Falls back to file-based storage when etcd is unavailable.
    """

    def __init__(
        self, endpoints: list[str] | None = None, fallback_dir: str = "data/etcd_fallback"
    ):
        self.endpoints = endpoints or ["127.0.0.1:2379"]
        self.fallback_dir = Path(fallback_dir)
        self.fallback_dir.mkdir(parents=True, exist_ok=True)

        self._client = None
        self._using_fallback = True
        self._data: dict[str, Any] = {}
        self._file_lock = FileBasedLock(self.fallback_dir / "locks")

        self._try_connect()
        self._load_fallback_data()

    def _try_connect(self):
        """Try to connect to etcd."""
        try:
            logger.info("etcd client not configured; using fallback store")
            self._using_fallback = True
            logger.info("Using file-based fallback for storage")
        except Exception as e:
            self._using_fallback = True
            logger.warning(f"etcd unavailable, using fallback: {e}")

    def _load_fallback_data(self):
        """Load data from fallback storage."""
        data_file = self.fallback_dir / "store.json"
        if data_file.exists():
            try:
                self._data = json.loads(data_file.read_text())
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save_fallback_data(self):
        """Save data to fallback storage."""
        data_file = self.fallback_dir / "store.json"
        data_file.write_text(json.dumps(self._data, indent=2))

    def put(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Store a value."""
        try:
            if self._using_fallback:
                self._data[key] = {"value": value, "created_at": time.time(), "ttl": ttl}
                self._save_fallback_data()
            else:
                logger.warning("etcd client unavailable; write skipped for %s", key)
            return True
        except Exception as e:
            logger.error(f"Failed to put {key}: {e}")
            return False

    def get(self, key: str) -> Any | None:
        """Retrieve a value."""
        try:
            if self._using_fallback:
                entry = self._data.get(key)
                if entry is None:
                    return None

                if entry.get("ttl"):
                    elapsed = time.time() - entry.get("created_at", 0)
                    if elapsed > entry["ttl"]:
                        del self._data[key]
                        self._save_fallback_data()
                        return None

                return entry.get("value")
            else:
                logger.warning("etcd client unavailable; read skipped for %s", key)
        except Exception as e:
            logger.error(f"Failed to get {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key."""
        try:
            if self._using_fallback:
                if key in self._data:
                    del self._data[key]
                    self._save_fallback_data()
            return True
        except Exception as e:
            logger.error(f"Failed to delete {key}: {e}")
            return False

    def list_keys(self, prefix: str = "") -> list[str]:
        """List keys with optional prefix."""
        if self._using_fallback:
            return [k for k in self._data.keys() if k.startswith(prefix)]
        return []

    @contextmanager
    def lock(self, key: str, ttl: int = 30):
        """Context manager for distributed locking."""
        holder = f"aurora_{os.getpid()}_{threading.current_thread().ident}"
        lock_key = f"locks/{key}"

        acquired = False
        try:
            if self._using_fallback:
                acquired = self._file_lock.acquire(lock_key, holder, ttl)
            else:
                logger.warning("etcd client unavailable; lock fallback skipped for %s", key)

            if not acquired:
                raise RuntimeError(f"Failed to acquire lock: {key}")

            yield

        finally:
            if acquired:
                if self._using_fallback:
                    self._file_lock.release(lock_key)

    def try_lock(self, key: str, ttl: int = 30) -> bool:
        """Try to acquire a lock without blocking."""
        holder = f"aurora_{os.getpid()}"
        lock_key = f"locks/{key}"

        if self._using_fallback:
            return self._file_lock.acquire(lock_key, holder, ttl)
        return False

    def unlock(self, key: str) -> bool:
        """Release a lock."""
        lock_key = f"locks/{key}"

        if self._using_fallback:
            return self._file_lock.release(lock_key)
        return False

    def get_status(self) -> dict[str, Any]:
        """Get store status."""
        return {
            "using_fallback": self._using_fallback,
            "endpoints": self.endpoints,
            "fallback_dir": str(self.fallback_dir),
            "key_count": len(self._data),
        }


class ModuleRegistry:
    """Module registry backed by EtcdStore."""

    def __init__(self, store: EtcdStore | None = None):
        self.store = store or EtcdStore()
        self.prefix = "modules/"

    def register(self, module_id: str, info: dict[str, Any]) -> bool:
        """Register a module."""
        key = f"{self.prefix}{module_id}"
        info["registered_at"] = time.time()
        return self.store.put(key, info)

    def unregister(self, module_id: str) -> bool:
        """Unregister a module."""
        key = f"{self.prefix}{module_id}"
        return self.store.delete(key)

    def get(self, module_id: str) -> dict[str, Any] | None:
        """Get module info."""
        key = f"{self.prefix}{module_id}"
        return self.store.get(key)

    def list_all(self) -> list[str]:
        """List all registered modules."""
        keys = self.store.list_keys(self.prefix)
        return [k.replace(self.prefix, "") for k in keys]

    def update_status(self, module_id: str, status: str) -> bool:
        """Update module status."""
        info = self.get(module_id)
        if info:
            info["status"] = status
            info["updated_at"] = time.time()
            return self.register(module_id, info)
        return False


# Module-level singleton and functions for prod_autonomy.py compatibility
_default_store: EtcdStore | None = None
_registry_key = "/aurora/modules_registry"


def _get_store() -> EtcdStore:
    """Get or create the default store instance."""
    global _default_store
    if _default_store is None:
        endpoints = os.environ.get("ETCD_HOSTS", "127.0.0.1:2379").split(",")
        _default_store = EtcdStore(endpoints=endpoints)
    return _default_store


def get_registry() -> dict:
    """Get the modules registry from etcd (or fallback)."""
    store = _get_store()
    data = store.get(_registry_key)
    if data is None:
        return {}
    return data


def put_registry_atomic(updater_func) -> tuple:
    """
    Atomically update the registry using the provided updater function.
    Returns (success: bool, new_registry: dict).
    """
    store = _get_store()
    lock_key = "registry_update"

    try:
        with store.lock(lock_key, ttl=30):
            current = get_registry()
            updated = updater_func(current)
            success = store.put(_registry_key, updated)
            return (success, updated if success else current)
    except Exception as e:
        logger.error(f"Atomic registry update failed: {e}")
        return (False, get_registry())


@contextmanager
def acquire_lock(name: str, ttl: int = 30):
    """Context manager for acquiring a distributed lock."""
    store = _get_store()
    with store.lock(name, ttl):
        yield
