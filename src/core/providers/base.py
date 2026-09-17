"""ACRA Provider Adapter Base Interfaces and Protocols.

Implements ADR-002: ProviderAdapter Protocol defining capability negotiation,
execution, cache descriptor inspection, and cost estimation.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from pydantic import BaseModel, ConfigDict, Field
from src.core.contracts.audit import EpistemicStatus
from src.core.contracts.cache import CacheContinuityDescriptor
from src.core.contracts.context import ContextCapsule
from src.core.contracts.model import CapabilityVector, ModelProfile


class ProviderResponse(BaseModel):
    """Standardized response envelope returned by any ProviderAdapter."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    content: str = Field(..., description="Generated text or structured output payload")
    model_id: str = Field(..., description="Concrete model identifier that executed generation")
    provider_id: str = Field(..., description="Provider identifier")
    prompt_tokens: int = Field(default=0, ge=0, description="Input tokens evaluated")
    completion_tokens: int = Field(default=0, ge=0, description="Output tokens produced")
    cached_tokens: int = Field(default=0, ge=0, description="Tokens read from prefix/prompt cache")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Calculated or estimated cost in USD")
    latency_ms: int = Field(default=0, ge=0, description="Execution duration in milliseconds")
    raw_metadata: dict[str, Any] = Field(default_factory=dict, description="Provider-specific telemetry")
    epistemic_status: EpistemicStatus = Field(default=EpistemicStatus.VERIFIED, description="Declared epistemic status")


@runtime_checkable
class ProviderAdapter(Protocol):
    """Protocol for LLM provider adapters (Google, Anthropic, OpenAI, Local, Stub)."""

    def get_provider_id(self) -> str:
        """Return the unique provider identifier (e.g., 'google', 'stub')."""
        ...

    def get_capabilities(self, model_id: str | None = None) -> CapabilityVector:
        """Return the capability vector for the specified model or provider default."""
        ...

    def generate(
        self,
        capsule: ContextCapsule,
        profile: ModelProfile,
        concrete_model_id: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Execute inference against the provider using context from ContextCapsule."""
        ...

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_id: str | None = None,
        cached_tokens: int = 0,
    ) -> float:
        """Estimate execution cost in USD."""
        ...

    def get_cache_descriptor(self, session_id: str) -> CacheContinuityDescriptor | None:
        """Return the current cache continuity descriptor for a session, if observable."""
        ...

    def health_check(self) -> bool:
        """Check provider connectivity and readiness."""
        ...
