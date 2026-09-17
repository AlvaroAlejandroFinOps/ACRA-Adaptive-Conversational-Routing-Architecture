"""ACRA Cache and Continuity Contracts.

Defines CacheContinuityDescriptor, AgentModelAffinity, ModelSessionLease,
ContextReuseEstimate, ModelMigrationDecision, and ContextRehydrationPlan (R-023, INV-010).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import EpistemicStatus


class CacheObservabilityLevel(str, Enum):
    """Level of observability into provider cache metrics."""
    FULL_TELEMETRY = "FULL_TELEMETRY"       # Provider reports cached/uncached tokens exactly
    ESTIMATED_PREFIX = "ESTIMATED_PREFIX"   # Calculated locally based on prefix hash matching
    OPAQUE = "OPAQUE"                       # Provider gives no cache telemetry


class CacheContinuityDescriptor(BaseModel):
    """Descriptor tracking cache continuity across turns and agent invocations (R-023)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_id: str = Field(..., description="Active provider ID")
    model_profile_id: str = Field(..., description="Target model profile")
    concrete_model_id: str = Field(..., description="Concrete model used")
    session_id: str = Field(..., description="ACRA session ID")
    agent_instance_id: str = Field(..., description="Active agent instance ID")
    cache_reference: str | None = Field(default=None, description="Provider-specific cache key or handle")
    cache_scope: str = Field(default="SESSION", description="Scope: SESSION, GLOBAL, TENANT")
    cache_created_at: datetime | None = Field(default=None, description="When cache was initialized")
    cache_expires_at: datetime | None = Field(default=None, description="When cache will expire")
    reported_cached_tokens: int | None = Field(default=None, description="Provider-reported cache read tokens")
    reported_uncached_tokens: int | None = Field(default=None, description="Provider-reported fresh input tokens")
    estimated_reusable_tokens: int = Field(default=0, ge=0, description="Locally estimated reusable prefix tokens")
    stable_prefix_hash: str = Field(..., description="Hash of active stable prefix")
    system_instruction_hash: str = Field(..., description="Hash of active system instruction")
    tool_manifest_hash: str = Field(..., description="Hash of active tool manifest")
    context_capsule_hash: str = Field(..., description="Hash of context capsule")
    provider_reported_cache_hit: bool | None = Field(default=None, description="Provider affirmed cache hit")
    observability_level: CacheObservabilityLevel = Field(
        default=CacheObservabilityLevel.ESTIMATED_PREFIX,
        description="Observability tier for this provider",
    )
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.ESTIMATED, description="Declared status (INV-004)")
    migration_cost_estimate: float = Field(default=0.0, ge=0.0, description="Estimated USD cost to switch model")
    limitations: list[str] = Field(default_factory=list, description="Known cache telemetry limitations")


class AgentModelAffinity(BaseModel):
    """Affinity binding between an agent and a specific provider model to maximize cache reuse."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    affinity_id: str = Field(..., description="Unique affinity record ID")
    agent_def_id: str = Field(..., description="Agent definition ID")
    agent_instance_id: str = Field(..., description="Active agent instance ID")
    bound_provider_id: str = Field(..., description="Bound provider ID")
    bound_model_id: str = Field(..., description="Bound model ID")
    affinity_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Strength of affinity (1.0 = maximum stickiness)")
    consecutive_turns_served: int = Field(default=0, ge=0, description="Turns executed on this model")
    last_interaction_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of last call")
    hysteresis_locked: bool = Field(default=False, description="Whether switching is currently locked by hysteresis policy (INV-010)")


class ModelSessionLease(BaseModel):
    """Lease holding dedicated affinity or provider resource allocation for a session."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    lease_id: str = Field(..., description="Unique lease identifier")
    session_id: str = Field(..., description="Session holding lease")
    provider_id: str = Field(..., description="Leased provider")
    model_id: str = Field(..., description="Leased model")
    acquired_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Acquisition timestamp")
    expires_at: datetime = Field(..., description="Lease expiration timestamp")
    is_active: bool = Field(default=True, description="Whether lease is valid and active")


class CacheCapabilityProfile(BaseModel):
    """Specification of provider-level caching economics and semantics."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_id: str = Field(..., description="Target provider ID")
    supports_prefix_caching: bool = Field(default=False, description="True if provider natively supports prefix caching")
    min_prefix_tokens: int = Field(default=1024, ge=0, description="Minimum tokens required to qualify for cache")
    cache_ttl_seconds: int = Field(default=300, ge=0, description="Default cache TTL")
    cache_read_discount_ratio: float = Field(default=0.5, ge=0.0, le=1.0, description="Cost discount multiplier for cached reads")


class ContextReuseEstimate(BaseModel):
    """Estimate of reusable context tokens and monetary savings."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    estimated_reusable_tokens: int = Field(..., ge=0, description="Tokens expected to hit cache")
    estimated_savings_usd: float = Field(..., ge=0.0, description="Projected dollar savings")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in estimate")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.ESTIMATED, description="Declared status")


class ModelMigrationDecision(BaseModel):
    """Formal decision to maintain or switch model affinity (INV-010)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(..., description="Unique migration evaluation ID")
    current_model_id: str = Field(..., description="Currently bound model")
    candidate_model_id: str = Field(..., description="Evaluated candidate model")
    should_migrate: bool = Field(..., description="True if migration is approved by cost model and hysteresis")
    net_benefit_usd: float = Field(..., description="Estimated net benefit taking migration penalty into account")
    reason: str = Field(..., description="Justification for migration or affinity retention")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared status")


class ContextRehydrationPlan(BaseModel):
    """Execution plan to rehydrate an agent's context when switching models or recovering state."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    plan_id: str = Field(..., description="Unique plan UUID")
    target_model_id: str = Field(..., description="Target model for rehydration")
    steps: list[str] = Field(default_factory=list, description="Ordered reconstruction steps")
    expected_tokens: int = Field(..., ge=0, description="Total expected input tokens for rehydration")
    required_evidence_ids: list[str] = Field(default_factory=list, description="Evidence items required for reconstruction")


class CacheInvalidationEvent(BaseModel):
    """Event triggered when a stable prefix or cached context is invalidated."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str = Field(..., description="Unique event identifier")
    prefix_hash: str = Field(..., description="Hash of invalidated prefix")
    reason: str = Field(..., description="Cause of invalidation")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Invalidation time")
