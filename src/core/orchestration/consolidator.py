"""ACRA Result Consolidator.

Synthesizes multiple AgentOutcomes into a ConsolidatedOutcome without cross-domain
context mixing (INV-003, INV-004).
"""

from __future__ import annotations

import uuid
from typing import Any
from src.core.contracts.audit import AuditHookPoint, ContextAuditProvider, EpistemicStatus
from src.core.contracts.outcome import AgentOutcome, ConsolidatedOutcome


class Consolidator:
    """Merges discrete task outcomes into a unified objective deliverable."""

    def __init__(self, audit_provider: ContextAuditProvider | None = None) -> None:
        self.audit_provider = audit_provider

    def consolidate(
        self,
        objective_id: str,
        outcomes: list[AgentOutcome],
    ) -> ConsolidatedOutcome:
        """Consolidate individual agent outcomes without merging internal contexts (INV-003)."""
        total_tokens = sum(o.tokens_consumed for o in outcomes)
        total_cost = sum(o.cost_usd for o in outcomes)
        total_latency = sum(o.latency_ms for o in outcomes)

        all_success = all(o.status == "SUCCESS" for o in outcomes) if outcomes else False
        status = "COMPLETED" if all_success else "FAILED"

        # Synthesize answers from structured payloads or fallback strings
        summary_parts = []
        for idx, o in enumerate(outcomes, start=1):
            res = o.payload.get("result", str(o.payload))
            summary_parts.append(f"Step {idx} ({o.task_id}): {res}")

        final_answer = "\n".join(summary_parts) if summary_parts else "Objective resolved with 0 task executions."

        # Post-consolidation audit
        consolidation_audit = None
        if self.audit_provider:
            consolidation_audit = self.audit_provider.audit(
                {"current_turn": final_answer, "domain": "consolidated"},
                hook_point=AuditHookPoint.POST_CONSOLIDATION,
            )

        return ConsolidatedOutcome(
            consolidation_id=f"cons_{uuid.uuid4().hex[:8]}",
            objective_id=objective_id,
            status=status,
            individual_outcomes=outcomes,
            final_answer=final_answer,
            total_tokens=total_tokens,
            total_cost_usd=round(total_cost, 6),
            total_latency_ms=total_latency,
            consolidation_audit=consolidation_audit,
            epistemic_status=EpistemicStatus.VERIFIED,
        )
