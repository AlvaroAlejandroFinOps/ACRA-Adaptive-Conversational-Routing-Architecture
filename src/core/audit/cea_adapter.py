"""ACRA CEA Context Audit Adapter.

Implements ContextAuditProvider bridging to the local Context Entropy Auditor (CEA) repository.
Provides circuit-breaker fallback to DeterministicFallbackAuditor when external CEA is unavailable.
"""

from __future__ import annotations

import logging
from typing import Any
from src.core.audit.deterministic import DeterministicFallbackAuditor
from src.core.contracts.audit import (
    AuditHookPoint,
    AuditResult,
    ContextAuditProvider,
    EpistemicStatus,
)
from src.core.contracts.context import ContextCapsule

logger = logging.getLogger("acra.audit.cea")


class CEAContextAuditAdapter:
    """Adapter bridging ACRA Context Audit Layer to a local CEA repository implementation."""

    def __init__(
        self,
        cea_client: Any = None,
        fallback_auditor: ContextAuditProvider | None = None,
    ) -> None:
        self._cea_client = cea_client
        self._fallback = fallback_auditor or DeterministicFallbackAuditor()
        self._circuit_open = False
        self._consecutive_failures = 0

    def get_supported_dimensions(self) -> list[str]:
        """Return supported dimensions combining CEA native and deterministic extensions."""
        base_dims = self._fallback.get_supported_dimensions()
        if self._cea_client and hasattr(self._cea_client, "get_dimensions"):
            try:
                cea_dims = self._cea_client.get_dimensions()
                return list(set(base_dims + cea_dims))
            except Exception as e:
                logger.warning("Failed to retrieve dimensions from CEA client: %s", e)
        return base_dims

    def health_check(self) -> bool:
        """Verify CEA reachability, falling back to deterministic readiness."""
        if self._cea_client is not None and not self._circuit_open:
            if hasattr(self._cea_client, "health_check"):
                try:
                    return bool(self._cea_client.health_check())
                except Exception:
                    return False
            return True
        return self._fallback.health_check()

    def audit(
        self,
        context_payload: ContextCapsule | dict[str, Any],
        hook_point: AuditHookPoint = AuditHookPoint.PRE_INFERENCE,
    ) -> AuditResult:
        """Execute audit against CEA with resilient fallback to deterministic auditor."""
        if self._cea_client is not None and not self._circuit_open:
            try:
                # Attempt audit via CEA client
                if hasattr(self._cea_client, "audit_context"):
                    raw_result = self._cea_client.audit_context(context_payload, hook_point.value)
                    self._consecutive_failures = 0
                    if isinstance(raw_result, AuditResult):
                        return raw_result
            except Exception as exc:
                self._consecutive_failures += 1
                if self._consecutive_failures >= 3:
                    self._circuit_open = True
                    logger.error("CEA circuit breaker tripped OPEN after 3 failures: %s", exc)
                else:
                    logger.warning("CEA audit failed, falling back to deterministic: %s", exc)

        # Fallback path: deterministic zero-LLM audit
        result = self._fallback.audit(context_payload, hook_point)
        return result


# Verify Protocol adherence
_cea_check: ContextAuditProvider = CEAContextAuditAdapter()
