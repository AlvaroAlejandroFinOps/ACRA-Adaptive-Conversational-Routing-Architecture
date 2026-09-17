"""ACRA Provenance and Economic Telemetry.

Implements R-012, INV-004, and INV-006:
- Comprehensive execution provenance per turn, task, and outcome.
- Strict declaration of EpistemicStatus on every provenance entry (INV-004).
- Explicit discrimination between measured vs estimated tokens and costs (INV-006).
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from src.core.contracts.audit import EpistemicStatus


class ProvenanceRecord(BaseModel):
    """Detailed audit trail record for an action, turn, or task outcome."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    record_id: str = Field(..., description="Unique provenance UUID")
    session_id: str = Field(..., description="Root conversation or workflow session ID")
    agent_id: str = Field(..., description="Executing agent instance ID")
    task_id: str | None = Field(default=None, description="Associated task ID if within a DAG")
    model_profile_id: str = Field(..., description="Capability model profile utilized")
    provider_id: str = Field(..., description="Underlying provider adapter ID")
    tool_calls: list[str] = Field(default_factory=list, description="List of tools invoked in this step")
    tokens_consumed: int = Field(default=0, ge=0, description="Tokens consumed in execution")
    is_measured_tokens: bool = Field(default=True, description="True if measured from provider API, False if estimated (INV-006)")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Cost incurred in USD")
    is_measured_cost: bool = Field(default=True, description="True if directly billed/measured, False if estimated (INV-006)")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Statistical confidence in result")
    epistemic_status: EpistemicStatus = Field(..., description="Mandatory declared epistemic status (INV-004)")
    evidence_refs: list[str] = Field(default_factory=list, description="Cryptographic evidence or artifact URIs")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of record creation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Diagnostic and contextual metadata")


class ProvenanceTracker:
    """Thread-safe telemetry and provenance tracker enforcing epistemic integrity."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._records_by_session: dict[str, list[ProvenanceRecord]] = {}

    def record(
        self,
        session_id: str,
        agent_id: str,
        model_profile_id: str,
        provider_id: str,
        epistemic_status: EpistemicStatus,
        task_id: str | None = None,
        tool_calls: list[str] | None = None,
        tokens_consumed: int = 0,
        is_measured_tokens: bool = True,
        cost_usd: float = 0.0,
        is_measured_cost: bool = True,
        confidence: float = 1.0,
        evidence_refs: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ProvenanceRecord:
        """Record an immutable provenance entry enforcing INV-004 and INV-006."""
        if not epistemic_status:
            raise ValueError("Every provenance entry must declare an epistemic status (INV-004)")

        record = ProvenanceRecord(
            record_id=f"prov_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            agent_id=agent_id,
            task_id=task_id,
            model_profile_id=model_profile_id,
            provider_id=provider_id,
            tool_calls=tool_calls or [],
            tokens_consumed=tokens_consumed,
            is_measured_tokens=is_measured_tokens,
            cost_usd=cost_usd,
            is_measured_cost=is_measured_cost,
            confidence=confidence,
            epistemic_status=epistemic_status,
            evidence_refs=evidence_refs or [],
            metadata=metadata or {},
        )

        with self._lock:
            if session_id not in self._records_by_session:
                self._records_by_session[session_id] = []
            self._records_by_session[session_id].append(record)

        return record

    def get_chain(self, session_id: str) -> list[ProvenanceRecord]:
        """Retrieve complete provenance history for a session."""
        with self._lock:
            return list(self._records_by_session.get(session_id, []))

    def verify_chain_epistemic_integrity(self, session_id: str) -> bool:
        """Verify that all records in session chain declare valid epistemic_status (INV-004)."""
        chain = self.get_chain(session_id)
        if not chain:
            return True
        for rec in chain:
            if not rec.epistemic_status or not isinstance(rec.epistemic_status, EpistemicStatus):
                return False
        return True

    def get_session_summary(self, session_id: str) -> dict[str, Any]:
        """Aggregate telemetry tokens, costs, tool calls, and epistemic distribution."""
        chain = self.get_chain(session_id)
        total_tokens_measured = 0
        total_tokens_estimated = 0
        total_cost_usd = 0.0
        tools_used: set[str] = set()
        status_counts: dict[str, int] = {}

        for r in chain:
            if r.is_measured_tokens:
                total_tokens_measured += r.tokens_consumed
            else:
                total_tokens_estimated += r.tokens_consumed

            total_cost_usd += r.cost_usd
            tools_used.update(r.tool_calls)

            st_val = r.epistemic_status.value
            status_counts[st_val] = status_counts.get(st_val, 0) + 1

        return {
            "session_id": session_id,
            "record_count": len(chain),
            "total_tokens_measured": total_tokens_measured,
            "total_tokens_estimated": total_tokens_estimated,
            "total_tokens": total_tokens_measured + total_tokens_estimated,
            "total_cost_usd": total_cost_usd,
            "tools_invoked": sorted(list(tools_used)),
            "epistemic_distribution": status_counts,
        }

    def clear(self, session_id: str | None = None) -> None:
        """Clear telemetry history."""
        with self._lock:
            if session_id is None:
                self._records_by_session.clear()
            else:
                self._records_by_session.pop(session_id, None)
