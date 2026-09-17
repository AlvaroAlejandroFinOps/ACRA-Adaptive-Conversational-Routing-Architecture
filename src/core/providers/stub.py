"""ACRA Deterministic Stub Provider.

Provides zero-dependency, reproducible execution for unit testing, CI/CD,
and offline verification complying with ProviderAdapter Protocol.
"""

from __future__ import annotations

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


class DeterministicStubProvider:
    """Zero-LLM deterministic provider adapter satisfying ProviderAdapter Protocol."""

    def __init__(
        self,
        provider_id: str = "stub",
        capabilities: CapabilityVector | None = None,
        default_model_id: str = "stub-deterministic-v1",
        model_capabilities: dict[str, CapabilityVector] | None = None,
    ) -> None:
        self.provider_id = provider_id
        self.default_model_id = default_model_id
        self.capabilities = capabilities or CapabilityVector(
            structured_output=True,
            tool_calling=True,
            long_context=True,
            reasoning=True,
            multimodal=False,
            streaming=True,
            cached_context=True,
            safety_controls=True,
            estimated_cost_per_1k_input=0.001,
            expected_latency_ms=10,
        )
        self.model_capabilities = model_capabilities or {
            default_model_id: self.capabilities
        }
        self.call_history: list[dict[str, Any]] = []
        self._canned_responses: dict[str, str] = {}
        self._session_cache_descriptors: dict[str, CacheContinuityDescriptor] = {}

    def get_provider_id(self) -> str:
        """Return provider identifier."""
        return self.provider_id

    def get_capabilities(self, model_id: str | None = None) -> CapabilityVector:
        """Return capabilities for the given model or provider default."""
        if model_id and model_id in self.model_capabilities:
            return self.model_capabilities[model_id]
        return self.capabilities

    def set_canned_response(self, prompt_substring: str, response: str) -> None:
        """Configure a deterministic response when prompt contains substring."""
        self._canned_responses[prompt_substring] = response

    def generate(
        self,
        capsule: ContextCapsule,
        profile: ModelProfile,
        concrete_model_id: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Execute deterministic inference."""
        model_id = concrete_model_id or self.default_model_id
        capsule_text = f"{capsule.task_context} {capsule.current_turn}"

        content = '{"status": "ok", "result": "Deterministic response generated"}'
        for substr, canned in self._canned_responses.items():
            if substr in capsule_text:
                content = canned
                break

        prompt_tokens = len(capsule_text.split()) * 2 + 50
        completion_tokens = len(content.split()) * 2
        cached_tokens = 0
        if self.capabilities.cached_context and capsule.stable_prefix:
            cached_tokens = capsule.stable_prefix.token_count

        cost = self.estimate_cost(prompt_tokens, completion_tokens, model_id, cached_tokens)

        response = ProviderResponse(
            content=content,
            model_id=model_id,
            provider_id=self.provider_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            cost_usd=cost,
            latency_ms=15,
            raw_metadata={"turn_hash": capsule.capsule_hash, "profile": profile.profile_id},
            epistemic_status=EpistemicStatus.STUB,
        )

        self.call_history.append({
            "capsule_id": capsule.capsule_id,
            "profile_id": profile.profile_id,
            "model_id": model_id,
            "timestamp": time.time(),
        })

        return response

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_id: str | None = None,
        cached_tokens: int = 0,
    ) -> float:
        """Calculate synthetic cost based on token counts."""
        caps = self.get_capabilities(model_id)
        effective_input = max(0, input_tokens - cached_tokens)
        input_cost = (effective_input / 1000.0) * caps.estimated_cost_per_1k_input
        # 50% discount on cached reads if supported
        cache_cost = (cached_tokens / 1000.0) * (caps.estimated_cost_per_1k_input * 0.5)
        output_cost = (output_tokens / 1000.0) * (caps.estimated_cost_per_1k_input * 4.0)
        return round(input_cost + cache_cost + output_cost, 6)

    def set_cache_descriptor(self, session_id: str, descriptor: CacheContinuityDescriptor) -> None:
        """Register a cache descriptor for testing."""
        self._session_cache_descriptors[session_id] = descriptor

    def get_cache_descriptor(self, session_id: str) -> CacheContinuityDescriptor | None:
        """Retrieve simulated cache descriptor for session."""
        return self._session_cache_descriptors.get(session_id)

    def health_check(self) -> bool:
        """Stub is always healthy."""
        return True


# Verify ProviderAdapter Protocol adherence at import time
_stub_check: ProviderAdapter = DeterministicStubProvider()
