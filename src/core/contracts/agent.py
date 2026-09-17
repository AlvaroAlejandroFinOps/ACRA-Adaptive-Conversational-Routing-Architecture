"""ACRA Agent Contracts.

Implements ADR-003: Separation of persistent AgentDefinition from ephemeral AgentInstance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.context import ContextBudget, ContextCapsule
from src.core.contracts.governance import ToolGrant


class AgentInstanceState(str, Enum):
    """Lifecycle states for ephemeral AgentInstance (ADR-004)."""
    CREATED = "CREATED"
    INITIALIZED = "INITIALIZED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


class AgentCapability(BaseModel):
    """Functional capability declared by an AgentDefinition."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Capability name (e.g., 'financial_analysis')")
    level: str = Field(default="STANDARD", description="Proficiency level: BASIC, STANDARD, EXPERT")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Domain-specific attributes")


class AgentPolicy(BaseModel):
    """Governance constraint or operational rule attached to an AgentDefinition."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Human-readable policy name")
    rule_type: str = Field(..., description="Rule category: 'security', 'budget', 'tool', 'domain'")
    expression: str = Field(..., description="Rule logic or constraint expression")
    is_mandatory: bool = Field(default=True, description="Whether rule cannot be bypassed")


class AgentDefinition(BaseModel):
    """Persistent template defining an agent's role, policies, tools, and domain (ADR-003)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_def_id: str = Field(..., description="Unique definition ID (e.g., 'def_finance_auditor')")
    name: str = Field(..., description="Human-readable agent title")
    domain: str = Field(..., description="Authoritative domain boundary")
    description: str = Field(default="", description="Detailed purpose of this agent definition")
    capabilities: list[AgentCapability] = Field(default_factory=list, description="Declared capabilities")
    policies: list[AgentPolicy] = Field(default_factory=list, description="Bound policies and rules")
    tool_grants: list[ToolGrant] = Field(default_factory=list, description="Whitelisted tools (INV-007)")
    input_contract: str = Field(default="json", description="Expected input schema reference")
    output_contract: str = Field(default="json", description="Enforced output schema reference")
    model_profile_id: str = Field(default="domain_planner", description="Target ModelProfile ID")
    escalation_policy_id: str | None = Field(default=None, description="Bound EscalationPolicy ID")
    max_context_tokens: int = Field(default=16000, ge=500, description="Max context ceiling")


class AgentInstance(BaseModel):
    """Ephemeral runtime entity created on-demand for task execution (ADR-003)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    instance_id: str = Field(..., description="Unique instance UUID")
    definition_id: str = Field(..., description="Reference to parent AgentDefinition")
    state: AgentInstanceState = Field(default=AgentInstanceState.CREATED, description="Active lifecycle state")
    context_capsule: ContextCapsule = Field(..., description="Isolated context capsule (INV-003)")
    budget: ContextBudget = Field(..., description="Cascaded resource budget (INV-005)")
    model_affinity_id: str | None = Field(default=None, description="Bound model session affinity ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    expires_at: datetime | None = Field(default=None, description="TTL timestamp when instance is expired")
    parent_instance_id: str | None = Field(default=None, description="Parent agent if delegated")

    def is_expired(self, current_time: datetime | None = None) -> bool:
        """Check if instance has exceeded its TTL."""
        if self.expires_at is None:
            return False
        now = current_time or datetime.now(timezone.utc)
        return now >= self.expires_at
