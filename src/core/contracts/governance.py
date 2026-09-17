"""ACRA Governance and Security Contracts.

Defines ToolGrant whitelists, PolicyMode enforcement gates, ValidationResult,
and ExecutionEvidence contracts.
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import EpistemicStatus


class PolicyMode(str, Enum):
    """Operational mode for security, governance, and audit gates."""
    AUDIT_ONLY = "AUDIT_ONLY"       # Log audit result without altering execution flow
    RECOMMEND = "RECOMMEND"         # Log recommendations; orchestrator may adapt strategy
    HUMAN_REVIEW = "HUMAN_REVIEW"   # Halt execution and request supervisor / human sign-off
    DRY_RUN = "DRY_RUN"             # Simulate execution without applying external side-effects
    ENFORCE = "ENFORCE"             # Hard block on policy or threshold violations


class ToolGrant(BaseModel):
    """Explicit grant authorizing an agent to invoke a specific tool."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    tool_name: str = Field(..., description="Canonical tool identifier")
    description: str = Field("", description="Human-readable purpose of the tool")
    is_destructive: bool = Field(default=False, description="Whether tool performs state mutation or destructive actions")
    max_invocations_per_task: int = Field(default=10, ge=1, description="Maximum calls allowed within a task lifecycle")
    allowed_parameters: list[str] = Field(default_factory=list, description="Whitelisted parameter names; empty allows all")
    requires_approval: bool = Field(default=False, description="Whether invocation requires runtime human/policy confirmation")


class ValidationResult(BaseModel):
    """Outcome of a security, schema, or contract validation check."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    is_valid: bool = Field(..., description="Whether validation passed")
    reason: str = Field(default="", description="Detailed reason if validation failed or warning raised")
    violations: list[str] = Field(default_factory=list, description="Specific rule or contract violation keys")
    sanitized_data: dict[str, Any] | None = Field(default=None, description="Sanitized payload if mutation occurred")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared epistemic status")


class ExecutionEvidence(BaseModel):
    """Cryptographically referenced evidence supporting an agent's claims or actions."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence_id: str = Field(..., description="Unique identifier for evidence item")
    tool_name: str | None = Field(None, description="Tool that generated this evidence, if tool-based")
    input_hash: str | None = Field(None, description="Hash of the input data")
    output_hash: str = Field(..., description="SHA-256 or similar content digest of the evidence")
    summary: str = Field(..., description="Concise synopsis of evidence content")
    provenance_uri: str | None = Field(None, description="URI or path where raw artifact is archived")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared epistemic status")
