"""ACRA Policy Mode Evaluators.

Implements the 5 Policy Modes specified in EVO ACRA.md §5:
AUDIT_ONLY, RECOMMEND, HUMAN_REVIEW, DRY_RUN, ENFORCE.
"""

from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import AuditResult
from src.core.contracts.governance import PolicyMode


class GateAction(str, Enum):
    """Enforced decision emitted by the PolicyModeGate."""
    PROCEED = "PROCEED"                 # Execution authorized
    WARN = "WARN"                       # Logged warning; execution authorized
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL" # Suspended awaiting human/supervisor confirmation
    SIMULATE_ONLY = "SIMULATE_ONLY"     # Dry run simulation; no side effects
    BLOCK = "BLOCK"                     # Execution forbidden


class PolicyDecision(BaseModel):
    """Result of policy gate evaluation."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: GateAction = Field(..., description="Action to enforce")
    mode: PolicyMode = Field(..., description="Active policy mode evaluated")
    reason: str = Field(..., description="Justification for decision")
    requires_human_signoff: bool = Field(default=False, description="True if manual approval required")
    sanitized: bool = Field(default=False, description="Whether payload was scrubbed or mitigated")


class PolicyModeGate:
    """Evaluates audit findings and operational actions against the active PolicyMode."""

    def __init__(
        self,
        mode: PolicyMode = PolicyMode.ENFORCE,
        risk_block_threshold: float = 0.75,
        risk_review_threshold: float = 0.50,
    ) -> None:
        self.mode = mode
        self.risk_block_threshold = risk_block_threshold
        self.risk_review_threshold = risk_review_threshold

    def evaluate(
        self,
        audit: AuditResult,
        is_destructive: bool = False,
    ) -> PolicyDecision:
        """Evaluate an audit result and action risk under the configured PolicyMode."""
        risk = audit.risk_score

        # Destructive actions always demand explicit approval unless in AUDIT_ONLY mode (INV-007)
        if is_destructive:
            if self.mode == PolicyMode.AUDIT_ONLY:
                return PolicyDecision(
                    action=GateAction.WARN,
                    mode=self.mode,
                    reason="Destructive action logged under AUDIT_ONLY mode",
                )
            return PolicyDecision(
                action=GateAction.REQUIRE_APPROVAL,
                mode=self.mode,
                reason="Destructive operations require explicit authorization (INV-007)",
                requires_human_signoff=True,
            )

        if self.mode == PolicyMode.AUDIT_ONLY:
            return PolicyDecision(
                action=GateAction.PROCEED if risk < self.risk_block_threshold else GateAction.WARN,
                mode=self.mode,
                reason=f"AUDIT_ONLY: Risk score is {risk:.2f}",
            )

        if self.mode == PolicyMode.DRY_RUN:
            return PolicyDecision(
                action=GateAction.SIMULATE_ONLY,
                mode=self.mode,
                reason="DRY_RUN mode active: simulating without applying side effects",
            )

        if self.mode == PolicyMode.HUMAN_REVIEW:
            if risk >= self.risk_review_threshold or audit.requires_policy_approval:
                return PolicyDecision(
                    action=GateAction.REQUIRE_APPROVAL,
                    mode=self.mode,
                    reason=f"HUMAN_REVIEW mode: risk {risk:.2f} exceeds threshold {self.risk_review_threshold}",
                    requires_human_signoff=True,
                )
            return PolicyDecision(
                action=GateAction.PROCEED,
                mode=self.mode,
                reason="Risk acceptable under HUMAN_REVIEW mode",
            )

        if self.mode == PolicyMode.RECOMMEND:
            action = GateAction.PROCEED if risk < self.risk_block_threshold else GateAction.WARN
            return PolicyDecision(
                action=action,
                mode=self.mode,
                reason=f"RECOMMEND mode: risk={risk:.2f}. Recommended: {', '.join(audit.recommended_actions) or 'continue'}",
            )

        # Mode == PolicyMode.ENFORCE
        if risk >= self.risk_block_threshold:
            return PolicyDecision(
                action=GateAction.BLOCK,
                mode=self.mode,
                reason=f"ENFORCE mode: risk {risk:.2f} exceeds critical ceiling {self.risk_block_threshold}",
            )

        if risk >= self.risk_review_threshold or audit.requires_policy_approval:
            return PolicyDecision(
                action=GateAction.REQUIRE_APPROVAL,
                mode=self.mode,
                reason=f"ENFORCE mode: elevated risk {risk:.2f} requires policy sign-off",
                requires_human_signoff=True,
            )

        return PolicyDecision(
            action=GateAction.PROCEED,
            mode=self.mode,
            reason=f"ENFORCE mode: context audit verified clean (risk={risk:.2f})",
        )
