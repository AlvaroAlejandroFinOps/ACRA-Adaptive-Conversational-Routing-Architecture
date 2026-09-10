"""
Unified Context Tier & Caching.
Almacena el estado condensado y proporciona tensores/representaciones limpias inyectables
en la fase de Prefill para erradicar el fenómeno 'Lost in the Middle'.
"""

import hashlib
import time
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field

from .dhc import CompressedContext


class ContextSnapshot(BaseModel):
    snapshot_id: str
    session_id: str
    tenant_id: str = "default"
    version: int = 1
    created_at_epoch: float
    total_turns: int
    compressed_context: CompressedContext
    cache_key: str
    prefill_ready_text: str
    is_revoked: bool = False
    revocation_reason: Optional[str] = None


class UnifiedContextTier:
    """
    Capa Unificada de Contexto y Memoria de Caché.
    Evita que los turnos intermedios queden en el 'valle de atención' en forma de U de los Transformers.
    Incluye aislamiento multi-inquilino (tenant_id), mitigación de colisiones con salt y revocación de snapshots.
    """

    def __init__(self, ttl_seconds: float = 3600.0, salt: str = "acra_kernel_salt_v1"):
        self.ttl_seconds = ttl_seconds
        self.salt = salt
        self._store: Dict[str, ContextSnapshot] = {}
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._revocations: int = 0

    def _generate_cache_key(self, tenant_id: str, session_id: str, clean_prompt: str) -> str:
        payload = f"{tenant_id}::{session_id}::{clean_prompt}::{self.salt}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def persist_snapshot(
        self,
        session_id: str,
        total_turns: int,
        compressed_ctx: CompressedContext,
        tenant_id: str = "default",
        version: int = 1,
    ) -> ContextSnapshot:
        """Persiste un snapshot consolidado y lo indexa para su reutilización inmediata."""
        cache_key = self._generate_cache_key(tenant_id, session_id, compressed_ctx.clean_history_prompt)
        snapshot_id = f"snap_{tenant_id}_{session_id}_{int(time.time()*1000)}"

        # Estructurar el texto listo para la fase Prefill en clúster pesado
        prefill_text = (
            f"[ACRA CONSOLIDATED CONTEXT | TENANT: {tenant_id} | SESSION: {session_id} | TURNS: {total_turns} | CCR: {compressed_ctx.ccr:.2%}]\n"
            f"{compressed_ctx.clean_history_prompt}\n"
            f"[END CONSOLIDATION - EXECUTE UNDER CLEAN BASELINE]"
        )

        snapshot = ContextSnapshot(
            snapshot_id=snapshot_id,
            session_id=session_id,
            tenant_id=tenant_id,
            version=version,
            created_at_epoch=time.time(),
            total_turns=total_turns,
            compressed_context=compressed_ctx,
            cache_key=cache_key,
            prefill_ready_text=prefill_text,
        )

        storage_key = f"{tenant_id}::{session_id}"
        self._store[storage_key] = snapshot
        return snapshot

    def get_latest_snapshot(self, session_id: str, tenant_id: str = "default") -> Optional[ContextSnapshot]:
        """Recupera el último snapshot válido si no ha expirado su TTL ni ha sido revocado."""
        storage_key = f"{tenant_id}::{session_id}"
        if storage_key not in self._store:
            # Fallback a session_id plano para compatibilidad
            if session_id in self._store:
                storage_key = session_id
            else:
                self._cache_misses += 1
                return None

        snap = self._store[storage_key]
        if snap.is_revoked:
            self._cache_misses += 1
            return None

        if (time.time() - snap.created_at_epoch) > self.ttl_seconds:
            del self._store[storage_key]
            self._cache_misses += 1
            return None

        self._cache_hits += 1
        return snap

    def revoke_snapshot(self, session_id: str, tenant_id: str = "default", reason: str = "Security revocation") -> bool:
        """Revoca un snapshot de memoria para prevenir poisoning o contaminación de contexto."""
        storage_key = f"{tenant_id}::{session_id}"
        snap = self._store.get(storage_key) or self._store.get(session_id)
        if snap:
            snap.is_revoked = True
            snap.revocation_reason = reason
            self._revocations += 1
            return True
        return False

    def is_revoked(self, session_id: str, tenant_id: str = "default") -> bool:
        storage_key = f"{tenant_id}::{session_id}"
        snap = self._store.get(storage_key) or self._store.get(session_id)
        return snap.is_revoked if snap else False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Métricas operativas del Unified Context Tier."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (self._cache_hits / total_requests) if total_requests > 0 else 0.0
        return {
            "active_sessions": len(self._store),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "revocations": self._revocations,
            "hit_rate_pct": hit_rate * 100.0,
        }

    def clear(self) -> None:
        """Limpia el almacén de contexto."""
        self._store.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._revocations = 0
