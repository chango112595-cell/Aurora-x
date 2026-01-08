"""
Production-grade plugin capability model.

Capabilities are strings like: 'network', 'gpu', 'fs-write', 'shell', 'ipc', 'camera'.
Policy file lives at data/plugins/permissions.json and is enforced locally (no external calls).
Default stance: deny-by-default unless explicitly allowed.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "data" / "plugins" / "permissions.json"
POLICY.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class PermissionPolicy:
    allow: list[str] = field(default_factory=list)
    block: list[str] = field(default_factory=list)
    default_allow: bool = False

    @classmethod
    def load(cls) -> "PermissionPolicy":
        if not POLICY.exists():
            policy = cls()
            POLICY.write_text(json.dumps(policy.__dict__, indent=2))
            return policy
        try:
            raw = json.loads(POLICY.read_text())
            return cls(
                allow=raw.get("allow", []),
                block=raw.get("block", []),
                default_allow=bool(raw.get("default_allow", False)),
            )
        except Exception as exc:
            raise RuntimeError(f"Invalid permissions policy: {exc}")

    def persist(self) -> None:
        POLICY.write_text(json.dumps(self.__dict__, indent=2))

    def evaluate(self, requested: list[str]) -> dict[str, list[str]]:
        allowed, blocked = [], []
        for perm in requested:
            if perm in self.block:
                blocked.append(perm)
            elif perm in self.allow or self.default_allow:
                allowed.append(perm)
            else:
                blocked.append(perm)
        return {"allowed": allowed, "blocked": blocked}


def request_permissions(plugin_id: str, perms: list[str]) -> dict[str, list[str]]:
    """
    Evaluate a plugin permission request against the local policy.
    Deny-by-default unless explicitly allowed.
    """
    policy = PermissionPolicy.load()
    decision = policy.evaluate(perms)
    audit = {
        "plugin": plugin_id,
        "requested": perms,
        "decision": decision,
    }
    audit_path = POLICY.parent / "permissions_audit.log"
    with audit_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(audit) + "\n")
    return decision


def update_policy(
    allow: list[str] = None, block: list[str] = None, default_allow: bool = False
) -> PermissionPolicy:
    """
    Update and persist the permissions policy.
    """
    policy = PermissionPolicy.load()
    policy.allow = sorted(set(allow or policy.allow))
    policy.block = sorted(set(block or policy.block))
    policy.default_allow = default_allow
    policy.persist()
    return policy
