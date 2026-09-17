"""ACRA Handoff Contracts.

Defines HandoffEnvelope, EscalationPolicy, and HandoffState.
Enforces INV-002: Every handoff envelope must pass pre-handoff audit before dispatch.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import AuditResult, EpistemicStatus
from src.core.contracts.context import ContextBudget
from src.core.contracts.governance import ExecutionEvidence, ToolGrant


class HandoffState(str, Enum):
    """Lifecycle states for an inter-agent handoff event (ADR-004)."""
    PREPARING = "PREPARING"
    AUDITING = "AUDITING"
    DISPATCHED = "DISPATCHED"
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"


class EscalationPolicy(BaseModel):
    """Policy governing model or agent escalation when task complexity exceeds thresholds."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str = Field(..., description="Unique escalation policy ID")
    trigger_conditions: list[str] = Field(default_factory=list, description="Triggers (e.g., 'max_turns_reached', 'high_risk')")
    target_profile_id: str = Field(..., description="Target ModelProfile to escalate to")
    requires_human_approval: bool = Field(default=False, description="Whether escalation halts for human approval (INV-007)")
    allow_reversal: bool = Field(default=True, description="Whether execution can de-escalate after subtask completion")


class HandoffEnvelope(BaseModel):
    """Typed, versioned, audited communication envelope between agents.

    Enforces INV-002: Pre-handoff audit is mandatory before dispatch.
    """
    model_config = ConfigDict(frozen=True, extra="forbid")

    envelope_id: str = Field(..., description="Unique envelope UUID")
    schema_version: str = Field(default="1.0.0", description="Envelope schema version")
    source_agent_id: str = Field(..., description="Originating agent instance ID")
    target_agent_id: str = Field(..., description="Receiving agent instance ID")
    domain: str = Field(..., description="Target domain boundary")
    objective: str = Field(..., description="Delegated objective or task summary")
    context_capsule_hash: str = Field(..., description="Integrity hash of the associated ContextCapsule")
    evidence: list[ExecutionEvidence] = Field(default_factory=list, description="Cryptographic evidence items")
    permissions: list[ToolGrant] = Field(default_factory=list, description="Delegated tool grants")
    budget: ContextBudget = Field(..., description="Allocated sub-budget (INV-005)")
    expires_at: datetime | None = Field(default=None, description="Handoff validity expiration")
    limitations: list[str] = Field(default_factory=list, description="Known operational limitations or constraints")
    pre_handoff_audit: AuditResult = Field(..., description="Mandatory audit result (INV-002)")
    audit_status: str = Field(default="PASSED", description="Audit status: PASSED, CONDITIONALLY_PASSED, REJECTED")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared status")

    def is_dispatchable(self) -> bool:
        """Check if envelope satisfies INV-002 for dispatch."""
        if self.audit_status != "PASSED" and self.audit_status != "CONDITIONALLY_PASSED":
            return False
        if self.pre_handoff_audit.risk_score > 0.8:
            return False
        return True
