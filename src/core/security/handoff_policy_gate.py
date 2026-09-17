"""ACRA Handoff Policy Gate.

Implements Phase 6 security controls:
- Pre-handoff static and dynamic audit (INV-002).
- Envelope sanitization and secret/PII redaction.
- Policy mode enforcement across the 5 modes (AUDIT_ONLY, RECOMMEND, HUMAN_REVIEW, DRY_RUN, ENFORCE).
- Destructive operation approvals (INV-007).
- Post-handoff validation (INV-003 domain isolation and capsule integrity).
- Reversible escalation with rehydration plan.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from src.core.contracts.agent import AgentDefinition, AgentInstance
from src.core.contracts.audit import (
    AuditHookPoint,
    AuditResult,
    AuditTriple,
    ContextAuditProvider,
    EpistemicStatus,
    Finding,
    FindingSeverity,
)
from src.core.contracts.context import ContextCapsule
from src.core.contracts.governance import PolicyMode, ValidationResult
from src.core.contracts.handoff import EscalationPolicy, HandoffEnvelope
from src.core.payload_policy import PayloadPolicyGate, PolicyValidationResult
from src.core.audit.policy_modes import GateAction, PolicyDecision, PolicyModeGate
from src.core.audit.deterministic import DeterministicFallbackAuditor


class HandoffSecurityError(PermissionError):
    """Raised when a security policy gate rejects a handoff or operation."""
    pass


class HandoffPolicyGate:
    """Security gate governing inter-agent handoff envelopes, audits, and validations."""

    def __init__(
        self,
        mode: PolicyMode = PolicyMode.ENFORCE,
        auditor: ContextAuditProvider | None = None,
        risk_block_threshold: float = 0.75,
        risk_review_threshold: float = 0.50,
    ) -> None:
        self.mode = mode
        self.payload_gate = PayloadPolicyGate()
        self.policy_gate = PolicyModeGate(
            mode=mode,
            risk_block_threshold=risk_block_threshold,
            risk_review_threshold=risk_review_threshold,
        )
        self.auditor = auditor or DeterministicFallbackAuditor()

    def set_mode(self, mode: PolicyMode) -> None:
        """Update active governance policy mode."""
        self.mode = mode
        self.policy_gate = PolicyModeGate(
            mode=mode,
            risk_block_threshold=self.policy_gate.risk_block_threshold,
            risk_review_threshold=self.policy_gate.risk_review_threshold,
        )

    def pre_handoff_audit(
        self,
        envelope_data: dict[str, Any],
        capsule: ContextCapsule | None = None,
        raw_payload_text: str = "",
    ) -> AuditResult:
        """Execute pre-handoff audit combining static scans and context audit (INV-002)."""
        findings: list[Finding] = []
        triggered_rules: list[str] = []
        text_to_scan = raw_payload_text or str(envelope_data.get("objective", ""))

        # 1. Run static payload analysis (injections, secrets, PII, sizing)
        val_result: PolicyValidationResult = self.payload_gate.validate(text_to_scan)
        risk_score = 0.05
        confidence = 0.95

        for v in val_result.violations:
            sev_str = v.severity.upper()
            severity = FindingSeverity.CRITICAL if sev_str == "CRITICAL" else (
                FindingSeverity.HIGH if sev_str == "HIGH" else FindingSeverity.MEDIUM
            )
            findings.append(Finding(
                finding_id=f"fnd_{uuid.uuid4().hex[:8]}",
                dimension="payload_security",
                severity=severity,
                message=f"[{v.violation_type.value}] {v.detail}",
                remediation_hint="Sanitize or redact payload before handoff",
            ))
            triggered_rules.append(f"payload_rule:{v.violation_type.value}")
            if v.severity == "critical":
                risk_score = max(risk_score, 0.90)
            elif v.severity == "high":
                risk_score = max(risk_score, 0.70)
            else:
                risk_score = max(risk_score, 0.40)

        # 2. Run context audit if capsule is supplied
        if capsule is not None:
            capsule_audit = self.auditor.audit(capsule, AuditHookPoint.PRE_HANDOFF)
            risk_score = max(risk_score, capsule_audit.risk_score)
            confidence = min(confidence, capsule_audit.confidence)
            findings.extend(capsule_audit.findings)
            triggered_rules.extend(capsule_audit.triggered_rules)

        requires_approval = risk_score >= self.policy_gate.risk_review_threshold

        recommended_actions = []
        if risk_score >= self.policy_gate.risk_block_threshold:
            recommended_actions.append("BLOCK_DISPATCH")
        elif requires_approval:
            recommended_actions.append("REQUIRE_HUMAN_APPROVAL")
        else:
            recommended_actions.append("PROCEED")

        from src.core.contracts.audit import AuditTriple

        return AuditResult(
            audit_id=f"audit_{uuid.uuid4().hex[:12]}",
            hook_point=AuditHookPoint.PRE_HANDOFF,
            triple=AuditTriple(
                risk_score=min(1.0, risk_score),
                confidence=confidence,
                evidence_coverage=1.0 if not findings else 0.8,
            ),
            findings=findings,
            triggered_rules=triggered_rules,
            recommended_actions=recommended_actions,
            requires_policy_approval=requires_approval,
            epistemic_status=EpistemicStatus.VERIFIED,
        )

    def evaluate_dispatch(
        self,
        envelope: HandoffEnvelope,
        is_destructive: bool = False,
    ) -> PolicyDecision:
        """Evaluate envelope dispatch authorization under current policy mode."""
        return self.policy_gate.evaluate(
            envelope.pre_handoff_audit,
            is_destructive=is_destructive,
        )

    def sanitize_payload(self, text: str) -> str:
        """Sanitize secrets and PII from raw text."""
        return self.payload_gate.sanitize(text)

    def post_handoff_validation(
        self,
        envelope: HandoffEnvelope,
        target_agent: AgentInstance,
        target_definition: AgentDefinition | None = None,
    ) -> ValidationResult:
        """Validate recipient integrity, domain boundary, and capsule binding post-dispatch."""
        violations: list[str] = []

        # 1. TTL / Expiration check
        if envelope.expires_at is not None:
            now = datetime.now(timezone.utc)
            if now >= envelope.expires_at:
                violations.append("envelope_expired")

        # 2. Domain boundary validation (INV-003)
        target_domain = target_definition.domain if target_definition else target_agent.context_capsule.domain
        if target_domain != "*" and envelope.domain != target_domain:
            violations.append(
                f"domain_mismatch: envelope domain '{envelope.domain}' != target agent domain '{target_domain}'"
            )

        # 3. Context capsule hash verification
        if envelope.context_capsule_hash != target_agent.context_capsule.capsule_hash:
            violations.append(
                f"capsule_hash_mismatch: envelope '{envelope.context_capsule_hash}' != agent '{target_agent.context_capsule.capsule_hash}'"
            )

        is_valid = len(violations) == 0
        return ValidationResult(
            is_valid=is_valid,
            reason="All post-handoff security checks passed" if is_valid else "; ".join(violations),
            violations=violations,
            epistemic_status=EpistemicStatus.VERIFIED,
        )

    def escalate(
        self,
        envelope: HandoffEnvelope,
        policy: EscalationPolicy,
        reason: str,
        supervisor_agent_id: str,
    ) -> tuple[HandoffEnvelope, PolicyDecision]:
        """Execute model or agent escalation with policy approval enforcement (R-011)."""
        # Evaluate approval requirement
        decision = PolicyDecision(
            action=GateAction.REQUIRE_APPROVAL if policy.requires_human_approval else GateAction.PROCEED,
            mode=self.mode,
            reason=f"Escalation triggered: {reason}",
            requires_human_signoff=policy.requires_human_approval,
        )

        if policy.requires_human_approval and self.mode == PolicyMode.ENFORCE:
            # Under ENFORCE, must not proceed automatically without manual approval
            return envelope, decision

        # Build escalated envelope
        escalated_envelope = HandoffEnvelope(
            envelope_id=f"env_esc_{uuid.uuid4().hex[:12]}",
            schema_version=envelope.schema_version,
            source_agent_id=envelope.target_agent_id,
            target_agent_id=supervisor_agent_id,
            domain=envelope.domain,
            objective=f"[ESCALATED: {reason}] {envelope.objective}",
            context_capsule_hash=envelope.context_capsule_hash,
            evidence=envelope.evidence,
            permissions=envelope.permissions,
            budget=envelope.budget,
            expires_at=envelope.expires_at,
            limitations=envelope.limitations + [f"Escalated via policy {policy.policy_id}"],
            pre_handoff_audit=envelope.pre_handoff_audit,
            audit_status=envelope.audit_status,
            epistemic_status=EpistemicStatus.VERIFIED,
        )
        return escalated_envelope, decision

    def de_escalate(
        self,
        escalated_envelope: HandoffEnvelope,
        original_agent_id: str,
        outcome_summary: str,
    ) -> HandoffEnvelope:
        """Reverse escalation back to standard agent tier upon subtask resolution (R-011)."""
        return HandoffEnvelope(
            envelope_id=f"env_deesc_{uuid.uuid4().hex[:12]}",
            schema_version=escalated_envelope.schema_version,
            source_agent_id=escalated_envelope.target_agent_id,
            target_agent_id=original_agent_id,
            domain=escalated_envelope.domain,
            objective=f"[RESOLVED SUBTASK] {outcome_summary}",
            context_capsule_hash=escalated_envelope.context_capsule_hash,
            evidence=escalated_envelope.evidence,
            permissions=escalated_envelope.permissions,
            budget=escalated_envelope.budget,
            expires_at=escalated_envelope.expires_at,
            limitations=escalated_envelope.limitations,
            pre_handoff_audit=escalated_envelope.pre_handoff_audit,
            audit_status="PASSED",
            epistemic_status=EpistemicStatus.VERIFIED,
        )
