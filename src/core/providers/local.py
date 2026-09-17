"""ACRA Local Model Provider Adapter.

Implements ADR-002: Local / Ollama adapter satisfying ProviderAdapter Protocol,
providing zero-cost offline execution with local KV-cache estimations.
"""

from __future__ import annotations

import json
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


class LocalAdapter:
    """Local Provider Adapter (Ollama / Local Inference) satisfying ProviderAdapter Protocol."""

    DEFAULT_MODEL = "llama-3.3-70b"

    def __init__(
        self,
        endpoint: str = "http://localhost:11434",
        default_model_id: str = DEFAULT_MODEL,
        model_capabilities: dict[str, CapabilityVector] | None = None,
    ) -> None:
        self.provider_id = "local"
        self.endpoint = endpoint
        self.default_model_id = default_model_id
        self._session_cache_descriptors: dict[str, CacheContinuityDescriptor] = {}
        self.call_history: list[dict[str, Any]] = []

        self.model_capabilities: dict[str, CapabilityVector] = model_capabilities or {
            "llama-3.3-70b": CapabilityVector(
                structured_output=True,
                tool_calling=True,
                long_context=True,
                reasoning=True,
                multimodal=False,
                streaming=True,
                cached_context=True,
                safety_controls=True,
                estimated_cost_per_1k_input=0.0,
                expected_latency_ms=1200,
            ),
            "mistral-nemo-12b": CapabilityVector(
                structured_output=True,
                tool_calling=True,
                long_context=True,
                reasoning=False,
                multimodal=False,
                streaming=True,
                cached_context=True,
                safety_controls=True,
                estimated_cost_per_1k_input=0.0,
                expected_latency_ms=450,
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
                estimated_cost_per_1k_input=0.0,
                expected_latency_ms=600,
            ),
        )

    def health_check(self) -> bool:
        """Local adapter health check."""
        return True

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model_id: str | None = None,
        cached_tokens: int = 0,
    ) -> float:
        """Local models have zero financial token cost."""
        return 0.0

    def generate(
        self,
        capsule: ContextCapsule,
        profile: ModelProfile,
        concrete_model_id: str | None = None,
        **kwargs: Any,
    ) -> ProviderResponse:
        """Execute inference against local engine (simulated)."""
        model_id = concrete_model_id or self.default_model_id
        start_time = time.perf_counter()

        capsule_text = f"{capsule.task_context} {capsule.current_turn}"
        prompt_tokens = len(capsule_text.split()) * 2 + 40
        content = json.dumps({
            "status": "success",
            "provider": "local",
            "model": model_id,
            "result": f"Local model completion for '{capsule.task_context[:30]}'",
        })
        completion_tokens = len(content.split()) * 2

        cached_tokens = 0
        cache_hit = False
        if capsule.stable_prefix and capsule.stable_prefix.token_count > 0:
            cached_tokens = capsule.stable_prefix.token_count
            cache_hit = True

        elapsed_ms = max(5, int((time.perf_counter() - start_time) * 1000))

        # Update cache descriptor
        session_id = getattr(capsule, "session_id", capsule.agent_instance_id)
        stable_hash = capsule.stable_prefix.content_hash if capsule.stable_prefix else "none"
        self._session_cache_descriptors[session_id] = CacheContinuityDescriptor(
            provider_id=self.provider_id,
            model_profile_id=profile.profile_id,
            concrete_model_id=model_id,
            session_id=session_id,
            agent_instance_id=capsule.agent_instance_id,
            cache_reference=f"local_kv_{stable_hash[:8]}",
            cache_scope="SESSION",
            reported_cached_tokens=cached_tokens,
            reported_uncached_tokens=prompt_tokens,
            estimated_reusable_tokens=cached_tokens,
            stable_prefix_hash=stable_hash,
            system_instruction_hash="sys_local",
            tool_manifest_hash="tools_local",
            context_capsule_hash=capsule.capsule_hash,
            provider_reported_cache_hit=cache_hit,
            observability_level=CacheObservabilityLevel.OPAQUE,
            epistemic_status=EpistemicStatus.ESTIMATED,
            migration_cost_estimate=0.0,
            limitations=["Local KV cache estimation only"],
        )

        response = ProviderResponse(
            content=content,
            model_id=model_id,
            provider_id=self.provider_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            cost_usd=0.0,
            latency_ms=elapsed_ms,
            raw_metadata={"local_endpoint": self.endpoint},
            epistemic_status=EpistemicStatus.ESTIMATED,
        )

        self.call_history.append({
            "capsule_id": capsule.capsule_id,
            "session_id": session_id,
            "model_id": model_id,
            "cost_usd": 0.0,
            "timestamp": time.time(),
        })

        return response

    def get_cache_descriptor(self, session_id: str) -> CacheContinuityDescriptor | None:
        """Retrieve active CacheContinuityDescriptor for session."""
        return self._session_cache_descriptors.get(session_id)


# Verify ProviderAdapter Protocol adherence at import time
_local_check: ProviderAdapter = LocalAdapter()
