"""ACRA Audit Contracts.

Defines the Context Audit Layer contracts, AuditResult with the mandatory tripleta
(risk_score, confidence, evidence_coverage), audit hook points, and the ContextAuditProvider protocol.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Protocol, runtime_checkable
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EpistemicStatus(str, Enum):
    """Declared epistemic status for audit, telemetry, and provenance artifacts."""
    VERIFIED = "VERIFIED"                  # Formally checked / deterministic measurement
    MEASURED = "MEASURED"                  # Directly measured from system runtime or metrics
    ESTIMATED = "ESTIMATED"                # Heuristic, probabilistic, or projected value
    PROVIDER_REPORTED = "PROVIDER_REPORTED"# Reported by external provider API without independent verification
    SELF_REPORTED = "SELF_REPORTED"        # Alias for provider-reported telemetry
    INFERRED = "INFERRED"                  # Statistically derived or synthesized from historical signals
    STUB = "STUB"                          # Synthetic test fixture or mock


class AuditHookPoint(str, Enum):
    """Defined hook points for context audit in ACRA lifecycle."""
    INTAKE = "INTAKE"
    PRE_INFERENCE = "PRE_INFERENCE"
    POST_TOOL = "POST_TOOL"
    PRE_HANDOFF = "PRE_HANDOFF"
    POST_HANDOFF = "POST_HANDOFF"
    POST_CONSOLIDATION = "POST_CONSOLIDATION"
    EVICTION = "EVICTION"
    MIGRATION = "MIGRATION"


class FindingSeverity(str, Enum):
    """Severity levels for audit findings."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Finding(BaseModel):
    """An individual finding identified by the audit layer."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    finding_id: str = Field(..., description="Unique finding identifier")
    dimension: str = Field(..., description="Audited dimension name")
    severity: FindingSeverity = Field(..., description="Finding severity level")
    message: str = Field(..., description="Detailed description of the finding")
    evidence_ref: str | None = Field(None, description="Pointer or hash of supporting evidence")
    remediation_hint: str | None = Field(None, description="Actionable recommendation")


class DimensionScore(BaseModel):
    """Score for a specific audited quality/entropy dimension."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    dimension: str = Field(..., description="Dimension name (e.g., contamination, verbosity)")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized score 0.0 to 1.0")
    risk_level: FindingSeverity = Field(..., description="Calculated risk severity for dimension")
    details: dict[str, Any] = Field(default_factory=dict, description="Diagnostic metrics")


class AuditTriple(BaseModel):
    """Mandatory audit assessment tripleta."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    risk_score: float = Field(..., ge=0.0, le=1.0, description="Composite risk assessment (0.0 safe, 1.0 critical)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence in assessment (0.0 none, 1.0 full)")
    evidence_coverage: float = Field(..., ge=0.0, le=1.0, description="Fraction of context substantiated by evidence (0.0 to 1.0)")


class AuditResult(BaseModel):
    """Canonical audit output evaluated by ACRA Context Audit Layer."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    audit_id: str = Field(..., description="Unique audit event identifier")
    hook_point: AuditHookPoint = Field(..., description="Lifecycle stage where audit was triggered")
    triple: AuditTriple = Field(..., description="Primary risk tripleta")
    dimension_scores: dict[str, DimensionScore] = Field(default_factory=dict, description="Scores per audited dimension")
    findings: list[Finding] = Field(default_factory=list, description="Specific findings and defects")
    evidence_refs: list[str] = Field(default_factory=list, description="References to substantiated evidence")
    triggered_rules: list[str] = Field(default_factory=list, description="Rules or security heuristics triggered")
    limitations: list[str] = Field(default_factory=list, description="Known audit limitations or blindspots")
    recommended_actions: list[str] = Field(default_factory=list, description="Suggested orchestrator actions")
    requires_policy_approval: bool = Field(default=False, description="True if human/supervisor sign-off is required")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared status of this audit")

    @property
    def risk_score(self) -> float:
        """Helper property for risk_score from tripleta."""
        return self.triple.risk_score

    @property
    def confidence(self) -> float:
        """Helper property for confidence from tripleta."""
        return self.triple.confidence

    @property
    def evidence_coverage(self) -> float:
        """Helper property for evidence_coverage from tripleta."""
        return self.triple.evidence_coverage

    @field_validator("epistemic_status")
    @classmethod
    def validate_epistemic_status(cls, v: EpistemicStatus) -> EpistemicStatus:
        """Ensure epistemic status is explicitly declared."""
        if not v:
            raise ValueError("Epistemic status must be explicitly declared (INV-004)")
        return v


@runtime_checkable
class ContextAuditProvider(Protocol):
    """Protocol for context audit providers (e.g., CEA adapter, Deterministic fallback)."""

    def audit(self, context_payload: Any, hook_point: AuditHookPoint) -> AuditResult:
        """Perform an audit assessment on the supplied context at the given hook point."""
        ...

    def get_supported_dimensions(self) -> list[str]:
        """Return the list of context dimensions supported by this auditor."""
        ...

    def health_check(self) -> bool:
        """Check if the audit provider is online and operational."""
        ...
