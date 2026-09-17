"""ACRA Anthropic Provider Adapter.

Implements ADR-002: Anthropic Claude adapter satisfying ProviderAdapter Protocol,
supporting ephemeral prompt caching semantics and mock simulation.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from src.core.contracts.audit import EpistemicStatus
from src.core.contracts.cache import (
    CacheContinuityDescriptor,
    CacheObservabilityLevel,
)
from src.core.contracts.context import ContextCapsule
from src.core.contracts.model import CapabilityVector, ModelProfile
from src.core.providers.base import ProviderAdapter, ProviderResponse


class AnthropicAdapter:
    """Anthropic Claude Provider Adapter satisfying ProviderAdapter Protocol."""

    DEFAULT_MODEL = "claude-3-5-haiku-latest"

    def __init__(
        self,
        api_key: str | None = None,
        default_model_id: str = DEFAULT_MODEL,
        model_capabilities: dict[str, CapabilityVector] | None = None,
        force_simulation: bool = True,
    ) -> None:
        self.provider_id = "anthropic"
        self.default_model_id = default_model_id
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.force_simulation = force_simulation
        self._session_cache_descriptors: dict[str, CacheContinuityDescriptor] = {}
        self.call_history: list[dict[str, Any]] = []

        self.model_capabilities: dict[str, CapabilityVector] = model_capabilities or {
            "claude-3-7-sonnet-latest": CapabilityVector(
                structured_output=True,
                tool_calling=True,
                long_context=True,
                reasoning=True,
                multimodal=True,
                streaming=True,
                cached_context=True,
                safety_controls=True,
                estimated_cost_per_1k_input=0.003,
                expected_latency_ms=950,
            ),
            "claude-3-5-haiku-latest": CapabilityVector(
                structured_output=True,
                tool_calling=True,
                long_context=True,
                reasoning=False,
                multimodal=False,
                streaming=True,
                cached_context=True,
                safety_controls=True,
                estimated_cost_per_1k_input=0.0008,
                expected_latency_ms=250,
            ),
        }

    def get_provider_id(self) -> str:
        """Return provider identifier."""
        return self.provider_id

    def get_capabilities(self, model_id: str | None = None) -> CapabilityVector:
        """Return capability vector for the specified model or provider default."""
        target_model = model_id or self.default_model_id
        if target_model in self.model_capabilities:
            return self.model_capabilities[target_model]
        return self.model_capabilities.get(
            self.default_model_id,
            CapabilityVector(
                structured_output=True,
                tool_calling=True,
                long_context=True,
                reasoning=False,
                multimodal=False,
                streaming=True,
                cached_context=True,
                safety_controls=True,
                estimated_cost_per_1k_input=0.001,
                expected_latency_ms=300,
            ),
        )

    def health_check(self) -> bool:
        """Anthropic readiness check."""
        return True

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_id: str | None = None,
        cached_tokens: int = 0,
    ) -> float:
        """Calculate cost with Anthropic prompt cache pricing (90% read discount)."""
        caps = self.get_capabilities(model_id)
        effective_input = max(0, input_tokens - cached_tokens)
        input_cost = (effective_input / 1000.0) * caps.estimated_cost_per_1k_input
        # Anthropic cached token read is 10% of base input rate (90% discount)
        cache_cost = (cached_tokens / 1000.0) * (caps.estimated_cost_per_1k_input * 0.10)
        output_cost = (output_tokens / 1000.0) * (caps.estimated_cost_per_1k_input * 5.0)
        return round(input_cost + cache_cost + output_cost, 6)

    def generate(
        self,
        capsule: ContextCapsule,
        profile: ModelProfile,
        concrete_model_id: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Execute inference against Anthropic provider (simulated/mock)."""
        model_id = concrete_model_id or self.default_model_id
        start_time = time.perf_counter()

        capsule_text = f"{capsule.task_context} {capsule.current_turn}"
        prompt_tokens = len(capsule_text.split()) * 2 + 70
        content = json.dumps({
            "status": "success",
            "provider": "anthropic",
            "model": model_id,
            "completion": f"Claude response for '{capsule.task_context[:35]}'",
        })
        completion_tokens = len(content.split()) * 2

        cached_tokens = 0
        cache_hit = False
        if capsule.stable_prefix and capsule.stable_prefix.token_count > 0:
            cached_tokens = capsule.stable_prefix.token_count
            cache_hit = True

        elapsed_ms = max(10, int((time.perf_counter() - start_time) * 1000))
        cost = self.estimate_cost(prompt_tokens, completion_tokens, model_id, cached_tokens)

        # Update cache descriptor
        session_id = getattr(capsule, "session_id", capsule.agent_instance_id)
        stable_hash = capsule.stable_prefix.content_hash if capsule.stable_prefix else "none"
        self._session_cache_descriptors[session_id] = CacheContinuityDescriptor(
            provider_id=self.provider_id,
            model_profile_id=profile.profile_id,
            concrete_model_id=model_id,
            session_id=session_id,
            agent_instance_id=capsule.agent_instance_id,
            cache_reference=f"anthropic_cache_{stable_hash[:8]}",
            cache_scope="SESSION",
            reported_cached_tokens=cached_tokens,
            reported_uncached_tokens=prompt_tokens,
            estimated_reusable_tokens=cached_tokens,
            stable_prefix_hash=stable_hash,
            system_instruction_hash="sys_anthropic",
            tool_manifest_hash="tools_anthropic",
            context_capsule_hash=capsule.capsule_hash,
            provider_reported_cache_hit=cache_hit,
            observability_level=CacheObservabilityLevel.FULL_TELEMETRY,
            epistemic_status=EpistemicStatus.ESTIMATED,
            migration_cost_estimate=0.002,
            limitations=["Mock execution"],
        )

        response = ProviderResponse(
            content=content,
            model_id=model_id,
            provider_id=self.provider_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            cost_usd=cost,
            latency_ms=elapsed_ms,
            raw_metadata={"simulated": True},
            epistemic_status=EpistemicStatus.ESTIMATED,
        )

        self.call_history.append({
            "capsule_id": capsule.capsule_id,
            "session_id": session_id,
            "model_id": model_id,
            "cost_usd": cost,
            "timestamp": time.time(),
        })

        return response

    def get_cache_descriptor(self, session_id: str) -> CacheContinuityDescriptor | None:
        """Retrieve active CacheContinuityDescriptor for session."""
        return self._session_cache_descriptors.get(session_id)


# Verify ProviderAdapter Protocol adherence at import time
_anthropic_check: ProviderAdapter = AnthropicAdapter()
