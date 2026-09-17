"""ACRA Scoped Context Registry.

Implements ScopedContextRegistry with domain and tenant boundaries (INV-003).
Guarantees cryptographic and logical tenant/domain isolation.
"""

from __future__ import annotations

import hmac
import hashlib
from datetime import datetime, timezone
from typing import Any
from src.core.contracts.context import ContextCapsule


class ScopeAccessError(PermissionError):
    """Raised when an attempt is made to access context outside granted domain or tenant scope."""
    pass


class ScopedContextRegistry:
    """Registry maintaining scoped, isolated ContextCapsules."""

    def __init__(self, salt: str = "acra_scoped_salt_v2", default_ttl_sec: int = 3600) -> None:
        self.salt = salt
        self.default_ttl_sec = default_ttl_sec
        self._store: dict[str, dict[str, Any]] = {}

    def _compute_key(self, tenant_id: str, domain: str, capsule_id: str) -> str:
        """Derive isolated storage key using HMAC."""
        base = f"{tenant_id}:{domain}:{capsule_id}"
        return hmac.new(self.salt.encode("utf-8"), base.encode("utf-8"), hashlib.sha256).hexdigest()

    def register_capsule(
        self,
        tenant_id: str,
        capsule: ContextCapsule,
        ttl_seconds: int | None = None,
    ) -> str:
        """Register and store an isolated ContextCapsule."""
        key = self._compute_key(tenant_id, capsule.domain, capsule.capsule_id)
        now = datetime.now(timezone.utc)
        ttl = ttl_seconds or self.default_ttl_sec

        self._store[key] = {
            "capsule": capsule,
            "tenant_id": tenant_id,
            "domain": capsule.domain,
            "capsule_id": capsule.capsule_id,
            "created_at": now,
            "expires_at": capsule.expires_at or datetime.fromtimestamp(now.timestamp() + ttl, timezone.utc),
            "is_revoked": False,
        }
        return key

    def get_capsule(
        self,
        tenant_id: str,
        requesting_domain: str,
        capsule_id: str,
    ) -> ContextCapsule | None:
        """Retrieve a capsule ensuring tenant and domain scope boundaries (INV-003)."""
        key = self._compute_key(tenant_id, requesting_domain, capsule_id)
        entry = self._store.get(key)
        if not entry:
            return None

        # Scope enforcement (INV-003)
        if entry["tenant_id"] != tenant_id or entry["domain"] != requesting_domain:
            raise ScopeAccessError(f"Cross-domain access violation: {requesting_domain} cannot access {entry['domain']}")

        if entry["is_revoked"]:
            return None

        now = datetime.now(timezone.utc)
        if now >= entry["expires_at"]:
            del self._store[key]
            return None

        capsule: ContextCapsule = entry["capsule"]
        return capsule

    def revoke_capsule(self, tenant_id: str, domain: str, capsule_id: str) -> bool:
        """Revoke a capsule immediately."""
        key = self._compute_key(tenant_id, domain, capsule_id)
        if key in self._store:
            self._store[key]["is_revoked"] = True
            return True
        return False

    def list_active_capsules_for_domain(self, tenant_id: str, domain: str) -> list[str]:
        """List active capsule IDs for a given tenant and domain."""
        now = datetime.now(timezone.utc)
        results = []
        for entry in self._store.values():
            if (
                entry["tenant_id"] == tenant_id
                and entry["domain"] == domain
                and not entry["is_revoked"]
                and now < entry["expires_at"]
            ):
                results.append(entry["capsule_id"])
        return results
