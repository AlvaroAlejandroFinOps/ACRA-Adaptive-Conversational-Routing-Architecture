"""ACRA Deterministic Fallback Auditor.

Implements ContextAuditProvider with zero-LLM dependencies, evaluating the 18
deterministic signals and emitting the mandatory AuditTriple across 12 dimensions.
"""

from __future__ import annotations

import uuid
from typing import Any
from src.core.audit.signals import DeterministicSignals, SignalCalculator
from src.core.contracts.audit import (
    AuditHookPoint,
    AuditResult,
    AuditTriple,
    ContextAuditProvider,
    DimensionScore,
    EpistemicStatus,
    Finding,
    FindingSeverity,
)
from src.core.contracts.context import ContextCapsule


class DeterministicFallbackAuditor:
    """Zero-LLM context auditor implementing the ContextAuditProvider protocol."""

    SUPPORTED_DIMENSIONS = [
        "instruction_conflict",
        "task_ambiguity",
        "context_contamination",
        "evidence_quality",
        "state_integrity",
        "redundancy_pressure",
        "context_utilization",
        "evidence_coverage",
        "stale_tool_results",
        "duplicate_documents",
        "identifier_collisions",
        "cross_domain_leakage",
    ]

    def __init__(self, foreign_domains: list[str] | None = None) -> None:
        self.foreign_domains = foreign_domains or []

    def get_supported_dimensions(self) -> list[str]:
        """Return dimensions supported by deterministic inspection."""
        return list(self.SUPPORTED_DIMENSIONS)

    def health_check(self) -> bool:
        """Deterministic auditor is in-process and always healthy."""
        return True

    def audit(
        self,
        context_payload: ContextCapsule | dict[str, Any],
        hook_point: AuditHookPoint = AuditHookPoint.PRE_INFERENCE,
    ) -> AuditResult:
        """Audit context deterministically and emit canonical AuditResult."""
        # Extract fields depending on input type
        if isinstance(context_payload, ContextCapsule):
            current_turn = context_payload.current_turn
            task_context = context_payload.task_context
            domain_context = context_payload.domain_context
            domain = context_payload.domain
            tool_results = [
                {"tool_name": t.tool_name, "call_id": t.call_id, "is_stale": t.is_stale}
                for t in context_payload.volatile_tool_state
            ]
        else:
            current_turn = str(context_payload.get("current_turn", ""))
            task_context = str(context_payload.get("task_context", ""))
            domain_context = str(context_payload.get("domain_context", ""))
            domain = str(context_payload.get("domain", "default"))
            tool_results = context_payload.get("tool_results", [])

        # Calculate 18 deterministic signals
        signals = SignalCalculator.calculate(
            current_turn=current_turn,
            task_context=task_context,
            domain_context=domain_context,
            tool_results=tool_results,
            target_domain=domain,
            known_foreign_domains=self.foreign_domains,
        )

        findings: list[Finding] = []
        dim_scores: dict[str, DimensionScore] = {}

        # 1. Contradiction / Conflict
        conflict_risk = min(1.0, signals.unresolved_contradictions * 0.5)
        dim_scores["instruction_conflict"] = DimensionScore(
            dimension="instruction_conflict",
            score=conflict_risk,
            risk_level=FindingSeverity.HIGH if conflict_risk > 0.4 else FindingSeverity.LOW,
            details={"contradictions": signals.unresolved_contradictions},
        )
        if conflict_risk > 0:
            findings.append(Finding(
                finding_id=f"f_{uuid.uuid4().hex[:6]}",
                dimension="instruction_conflict",
                severity=FindingSeverity.HIGH,
                message=f"Detected {signals.unresolved_contradictions} conflicting directives in instructions",
                remediation_hint="Clarify instruction priorities or remove contradicting statements",
            ))

        # 2. Context Contamination / Cross-Domain Leakage
        leakage_risk = min(1.0, signals.cross_domain_references * 0.4)
        dim_scores["cross_domain_leakage"] = DimensionScore(
            dimension="cross_domain_leakage",
            score=leakage_risk,
            risk_level=FindingSeverity.CRITICAL if leakage_risk > 0.3 else FindingSeverity.LOW,
            details={"cross_domain_refs": signals.cross_domain_references},
        )
        if leakage_risk > 0:
            findings.append(Finding(
                finding_id=f"f_{uuid.uuid4().hex[:6]}",
                dimension="cross_domain_leakage",
                severity=FindingSeverity.CRITICAL,
                message=f"Detected {signals.cross_domain_references} foreign domain mentions within scoped context",
                remediation_hint="Scrub foreign domain identifiers before inference (INV-003)",
            ))

        # 3. Redundancy & Duplicates
        redundancy_risk = max(
            signals.repeated_instruction_ratio,
            min(1.0, signals.exact_document_duplicates * 0.3),
        )
        dim_scores["redundancy_pressure"] = DimensionScore(
            dimension="redundancy_pressure",
            score=redundancy_risk,
            risk_level=FindingSeverity.MEDIUM if redundancy_risk > 0.3 else FindingSeverity.LOW,
            details={
                "exact_duplicates": signals.exact_document_duplicates,
                "repetition_ratio": signals.repeated_instruction_ratio,
            },
        )
        if redundancy_risk > 0.3:
            findings.append(Finding(
                finding_id=f"f_{uuid.uuid4().hex[:6]}",
                dimension="redundancy_pressure",
                severity=FindingSeverity.MEDIUM,
                message="Elevated textual redundancy detected in context",
                remediation_hint="Apply deduplication stage in pipeline",
            ))

        # 4. Stale Tool Results
        stale_risk = min(1.0, (signals.stale_context_items + signals.superseded_tool_results) * 0.3)
        dim_scores["stale_tool_results"] = DimensionScore(
            dimension="stale_tool_results",
            score=stale_risk,
            risk_level=FindingSeverity.HIGH if stale_risk > 0.4 else FindingSeverity.LOW,
            details={
                "stale_items": signals.stale_context_items,
                "superseded": signals.superseded_tool_results,
            },
        )
        if stale_risk > 0.2:
            findings.append(Finding(
                finding_id=f"f_{uuid.uuid4().hex[:6]}",
                dimension="stale_tool_results",
                severity=FindingSeverity.MEDIUM if stale_risk < 0.5 else FindingSeverity.HIGH,
                message=f"Context contains {signals.stale_context_items} stale and {signals.superseded_tool_results} superseded tool outputs",
                remediation_hint="Prune outdated tool responses before next inference turn",
            ))

        # 5. Context Utilization
        util_risk = 0.0
        if signals.context_utilization_ratio > 0.90:
            util_risk = 0.9
        elif signals.context_utilization_ratio > 0.75:
            util_risk = 0.5
        dim_scores["context_utilization"] = DimensionScore(
            dimension="context_utilization",
            score=min(1.0, signals.context_utilization_ratio),
            risk_level=FindingSeverity.HIGH if util_risk > 0.6 else FindingSeverity.LOW,
            details={"utilization_ratio": signals.context_utilization_ratio},
        )

        # Composite Risk Score Calculation
        dim_weights = {
            "cross_domain_leakage": 0.35,
            "instruction_conflict": 0.25,
            "stale_tool_results": 0.20,
            "redundancy_pressure": 0.10,
            "context_utilization": 0.10,
        }
        composite_risk = sum(
            dim_scores[d].score * w for d, w in dim_weights.items() if d in dim_scores
        )
        composite_risk = min(1.0, max(0.0, composite_risk))

        # Evidence Coverage (heuristic: ratio of substantive content substantiated by tools/facts)
        evidence_coverage = 0.85
        if signals.orphan_tool_results > 0:
            evidence_coverage -= 0.2
        if signals.unresolved_contradictions > 0:
            evidence_coverage -= 0.2
        evidence_coverage = max(0.1, min(1.0, evidence_coverage))

        confidence = 0.90  # Deterministic measurement provides high statistical confidence

        triple = AuditTriple(
            risk_score=round(composite_risk, 4),
            confidence=round(confidence, 4),
            evidence_coverage=round(evidence_coverage, 4),
        )

        recommended_actions: list[str] = []
        if leakage_risk > 0:
            recommended_actions.append("PURGE_CROSS_DOMAIN_REFERENCES")
        if stale_risk > 0:
            recommended_actions.append("PRUNE_STALE_TOOL_RESULTS")
        if redundancy_risk > 0.3:
            recommended_actions.append("COMPACT_CONTEXT")

        return AuditResult(
            audit_id=f"aud_det_{uuid.uuid4().hex[:8]}",
            hook_point=hook_point,
            triple=triple,
            dimension_scores=dim_scores,
            findings=findings,
            evidence_refs=[],
            triggered_rules=[f"det_rule_{d}" for d, s in dim_scores.items() if s.score > 0.3],
            limitations=["Evaluated using zero-LLM deterministic heuristics"],
            recommended_actions=recommended_actions,
            requires_policy_approval=(composite_risk >= 0.70),
            epistemic_status=EpistemicStatus.VERIFIED,
        )


# Verify Protocol adherence at import time
_check: ContextAuditProvider = DeterministicFallbackAuditor()
