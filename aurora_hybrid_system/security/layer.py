import hashlib
import hmac
import time


class CapabilityToken:
    def __init__(self, entity_id, capabilities, expires_at, secret=None):
        import os

        self.entity_id = entity_id
        self.capabilities = capabilities
        self.expires_at = expires_at
        # SECURITY: Secret MUST come from environment variable
        self.secret = secret or os.environ.get("AURORA_TOKEN_SECRET")
        if not self.secret:
            raise ValueError(
                "AURORA_TOKEN_SECRET environment variable must be set for security tokens"
            )
        self.signature = self._sign()

    def _sign(self):
        data = f"{self.entity_id}:{','.join(sorted(self.capabilities))}:{self.expires_at}"
        return hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).hexdigest()

    def is_valid(self):
        if time.time() > self.expires_at:
            return False
        return self._sign() == self.signature

    def has_capability(self, cap):
        return cap in self.capabilities and self.is_valid()

    def to_dict(self):
        return {
            "entity_id": self.entity_id,
            "capabilities": list(self.capabilities),
            "expires_at": self.expires_at,
            "signature": self.signature,
        }


class SecurityLayer:
    TIER_CAPABILITIES = {
        "sandbox": {"read", "compute"},
        "worker": {"read", "compute", "write_temp"},
        "autonomy": {"read", "compute", "write_temp", "write_module", "repair"},
        "admin": {
            "read",
            "compute",
            "write_temp",
            "write_module",
            "repair",
            "promote",
            "delete",
            "configure",
        },
    }
    APPROVAL_REQUIRED = {"delete", "promote", "configure"}

    def __init__(self, secret=None):
        import os

        # SECURITY: Secret MUST come from environment variable
        self.secret = secret or os.environ.get("AURORA_TOKEN_SECRET")
        if not self.secret:
            raise ValueError(
                "AURORA_TOKEN_SECRET environment variable must be set for SecurityLayer"
            )
        self.tokens = {}
        self.pending_approvals = {}
        self.approval_log = []

    def issue_token(self, entity_id, tier, ttl_seconds=3600):
        if tier not in self.TIER_CAPABILITIES:
            return None
        caps = self.TIER_CAPABILITIES[tier]
        expires = time.time() + ttl_seconds
        token = CapabilityToken(entity_id, caps, expires, self.secret)
        self.tokens[entity_id] = token
        return token

    def validate_token(self, entity_id):
        token = self.tokens.get(entity_id)
        return token is not None and token.is_valid()

    def check_capability(self, entity_id, capability):
        token = self.tokens.get(entity_id)
        if not token:
            return False
        return token.has_capability(capability)

    def requires_approval(self, capability):
        return capability in self.APPROVAL_REQUIRED

    def request_approval(self, entity_id, action, context=None):
        approval_id = f"APR-{int(time.time() * 1000)}"
        self.pending_approvals[approval_id] = {
            "entity_id": entity_id,
            "action": action,
            "context": context or {},
            "requested_at": time.time(),
            "status": "pending",
        }
        return approval_id

    def approve(self, approval_id, approver):
        if approval_id not in self.pending_approvals:
            return False
        self.pending_approvals[approval_id]["status"] = "approved"
        self.pending_approvals[approval_id]["approved_by"] = approver
        self.pending_approvals[approval_id]["approved_at"] = time.time()
        self.approval_log.append(self.pending_approvals[approval_id])
        return True

    def deny(self, approval_id, reason=""):
        if approval_id not in self.pending_approvals:
            return False
        self.pending_approvals[approval_id]["status"] = "denied"
        self.pending_approvals[approval_id]["reason"] = reason
        return True

    def revoke_token(self, entity_id):
        self.tokens.pop(entity_id, None)
