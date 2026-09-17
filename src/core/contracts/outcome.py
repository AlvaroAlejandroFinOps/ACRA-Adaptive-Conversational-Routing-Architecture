"""ACRA Outcome Contracts.

Defines AgentOutcome and ConsolidatedOutcome for result consolidation without context mixing.
Enforces INV-004 (epistemic_status on provenance) and INV-006 (estimate vs measured tokens).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import AuditResult, EpistemicStatus
from src.core.contracts.governance import ExecutionEvidence, ValidationResult


class AgentOutcome(BaseModel):
    """The result produced by an AgentInstance completing a task."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    outcome_id: str = Field(..., description="Unique outcome UUID")
    agent_instance_id: str = Field(..., description="Agent instance that completed the task")
    task_id: str = Field(..., description="Task ID executed")
    status: str = Field(..., description="Execution status: SUCCESS, PARTIAL_SUCCESS, FAILED")
    payload: dict[str, Any] = Field(default_factory=dict, description="Structured output payload")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score in output validity")
    evidence: list[ExecutionEvidence] = Field(default_factory=list, description="Substantiating evidence")
    tokens_consumed: int = Field(default=0, ge=0, description="Tokens consumed during task")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Cost incurred in USD")
    latency_ms: int = Field(default=0, ge=0, description="Execution duration in milliseconds")
    validation_result: ValidationResult | None = Field(default=None, description="Schema/policy validation result")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared status (INV-004)")


class ConsolidatedOutcome(BaseModel):
    """Consolidated result of multiple agent tasks resolving an overall objective."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    consolidation_id: str = Field(..., description="Unique consolidation UUID")
    objective_id: str = Field(..., description="Objective ID resolved")
    status: str = Field(..., description="Overall objective status: COMPLETED, FAILED, ESCALATED")
    individual_outcomes: list[AgentOutcome] = Field(default_factory=list, description="Constituent agent outcomes")
    final_answer: str = Field(..., description="Synthesized response or deliverable")
    total_tokens: int = Field(default=0, ge=0, description="Aggregated tokens consumed")
    total_cost_usd: float = Field(default=0.0, ge=0.0, description="Aggregated cost in USD")
    total_latency_ms: int = Field(default=0, ge=0, description="Total elapsed wall-clock latency")
    consolidation_audit: AuditResult | None = Field(default=None, description="Post-consolidation audit result")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared status (INV-004)")
