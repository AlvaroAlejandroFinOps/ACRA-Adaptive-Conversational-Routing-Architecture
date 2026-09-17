"""ACRA Model Selection and Capability Contracts.

Implements ADR-002: Capability-based model resolution replacing brand/model names (INV-001).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import EpistemicStatus


class CapabilityVector(BaseModel):
    """Normalized vector of capabilities supported by a provider model."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    structured_output: bool = Field(default=True, description="Supports strict JSON schema output")
    tool_calling: bool = Field(default=True, description="Supports function/tool calling protocols")
    long_context: bool = Field(default=False, description="Context window >= 128k tokens")
    reasoning: bool = Field(default=False, description="High-depth multi-step reasoning capabilities")
    multimodal: bool = Field(default=False, description="Image/document perception")
    streaming: bool = Field(default=True, description="Supports token streaming")
    cached_context: bool = Field(default=False, description="Supports prompt/prefix caching API")
    safety_controls: bool = Field(default=True, description="Configurable safety/moderation gates")
    estimated_cost_per_1k_input: float = Field(default=0.001, ge=0.0, description="Nominal cost in USD per 1k input tokens")
    expected_latency_ms: int = Field(default=500, ge=0, description="Expected average latency in milliseconds")


class ModelProfile(BaseModel):
    """Declarative capability requirements for an agent's role (ADR-002)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_id: str = Field(..., description="Logical role: 'frontier_planner', 'lightweight_executor', etc.")
    description: str = Field("", description="Purpose and operational context of profile")
    required_capabilities: set[str] = Field(default_factory=set, description="Required capability flags")
    max_context_tokens: int = Field(default=32000, ge=1000, description="Minimum context size needed")
    max_cost_per_1k_input: float = Field(default=0.05, ge=0.0, description="Maximum acceptable cost per 1k input tokens")
    max_latency_ms: int = Field(default=5000, ge=10, description="Maximum acceptable latency budget")
    risk_level_allowed: str = Field(default="MEDIUM", description="Max risk level permitted for this profile")
    preferred_provider: str | None = Field(default=None, description="Preferred provider ID if available")
    fallback_providers: list[str] = Field(default_factory=list, description="Ordered list of fallback provider IDs")


class ProviderProfile(BaseModel):
    """Metadata profile of a connected provider adapter."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    provider_id: str = Field(..., description="Unique provider ID (e.g., 'google', 'stub')")
    name: str = Field(..., description="Human-readable provider name")
    available_capabilities: CapabilityVector = Field(..., description="Capability vector of provider")
    rate_limit_rpm: int = Field(default=60, ge=1, description="Requests per minute limit")
    is_local: bool = Field(default=False, description="Whether execution is local (e.g., Ollama)")


class ModelSelectionDecision(BaseModel):
    """Outcome of capability resolution matching a ModelProfile to an executable model."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    decision_id: str = Field(..., description="Unique selection event ID")
    profile_id: str = Field(..., description="Profile that requested resolution")
    selected_provider_id: str = Field(..., description="Selected provider adapter")
    selected_model_id: str = Field(..., description="Concrete model ID (resolved at runtime)")
    rationale: str = Field(..., description="Justification for selection")
    estimated_input_cost: float = Field(default=0.0, ge=0.0, description="Estimated input cost in USD")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Match confidence")
    fallback_chain: list[str] = Field(default_factory=list, description="Ordered list of alternate models")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared status")
