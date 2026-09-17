"""ACRA Model Resolver and Capability Registry.

Implements ADR-002: Capability-based model resolution replacing brand/model names (INV-001).
Resolves ModelProfile declarative requirements against active ProviderAdapters.
"""

from __future__ import annotations

import os
import uuid
from typing import Any
import yaml
from pydantic import ValidationError

from src.core.contracts.audit import EpistemicStatus
from src.core.contracts.context import ContextBudget
from src.core.contracts.model import (
    CapabilityVector,
    ModelProfile,
    ModelSelectionDecision,
    ProviderProfile,
)
from src.core.providers.base import ProviderAdapter


class ResolutionError(Exception):
    """Raised when model resolution fails to satisfy profile constraints."""
    pass


class ModelCapabilityRegistry:
    """Registry managing model capability profiles and runtime resolution."""

    def __init__(self) -> None:
        self._profiles: dict[str, ModelProfile] = {}
        self._providers: dict[str, ProviderAdapter] = {}
        self._provider_models: dict[str, dict[str, CapabilityVector]] = {}

    def register_profile(self, profile: ModelProfile) -> None:
        """Register a ModelProfile."""
        self._profiles[profile.profile_id] = profile

    def get_profile(self, profile_id: str) -> ModelProfile | None:
        """Retrieve a registered ModelProfile."""
        return self._profiles.get(profile_id)

    def register_provider(
        self,
        provider: ProviderAdapter,
        models: dict[str, CapabilityVector] | None = None,
    ) -> None:
        """Register a ProviderAdapter with its supported models and capability vectors."""
        p_id = provider.get_provider_id()
        self._providers[p_id] = provider
        if models:
            self._provider_models[p_id] = models
        else:
            # Default model using provider default capabilities
            self._provider_models[p_id] = {f"{p_id}-default": provider.get_capabilities()}

    def load_profiles_from_yaml(self, yaml_path: str) -> None:
        """Load ModelProfiles from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Profile configuration not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        profiles_data = data.get("profiles", {})
        for p_id, p_config in profiles_data.items():
            if "profile_id" not in p_config:
                p_config["profile_id"] = p_id
            # Ensure required_capabilities is a set
            if "required_capabilities" in p_config and isinstance(p_config["required_capabilities"], list):
                p_config["required_capabilities"] = set(p_config["required_capabilities"])
            profile = ModelProfile(**p_config)
            self.register_profile(profile)

    def load_provider_config_from_yaml(self, yaml_path: str, provider: ProviderAdapter) -> None:
        """Load model capability mappings for a provider from YAML."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Provider configuration not found: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        models_data = data.get("models", {})
        model_caps: dict[str, CapabilityVector] = {}
        for m_id, m_config in models_data.items():
            model_caps[m_id] = CapabilityVector(**m_config)

        self.register_provider(provider, model_caps)

    def resolve(
        self,
        profile_id: str,
        context_budget: ContextBudget | None = None,
    ) -> ModelSelectionDecision:
        """Resolve a ModelProfile against registered providers and models (ADR-002)."""
        profile = self._profiles.get(profile_id)
        if not profile:
            raise ResolutionError(f"ModelProfile '{profile_id}' is not registered.")

        # Determine evaluation order of providers: preferred first, fallbacks, then others
        ordered_provider_ids: list[str] = []
        if profile.preferred_provider and profile.preferred_provider in self._providers:
            ordered_provider_ids.append(profile.preferred_provider)

        for fb in profile.fallback_providers:
            if fb in self._providers and fb not in ordered_provider_ids:
                ordered_provider_ids.append(fb)

        for p_id in self._providers:
            if p_id not in ordered_provider_ids:
                ordered_provider_ids.append(p_id)

        evaluated_candidates: list[tuple[str, str, CapabilityVector]] = []
        rejected_reasons: list[str] = []

        for p_id in ordered_provider_ids:
            provider = self._providers[p_id]
            if not provider.health_check():
                rejected_reasons.append(f"Provider '{p_id}' health_check failed")
                continue

            models_dict = self._provider_models.get(p_id, {})
            for m_id, cap in models_dict.items():
                # Check capability satisfaction
                missing_caps = self._check_missing_capabilities(profile.required_capabilities, cap)
                if missing_caps:
                    rejected_reasons.append(f"{p_id}/{m_id} missing required capabilities: {missing_caps}")
                    continue

                # Check cost constraints
                if cap.estimated_cost_per_1k_input > profile.max_cost_per_1k_input:
                    rejected_reasons.append(
                        f"{p_id}/{m_id} cost {cap.estimated_cost_per_1k_input} exceeds max {profile.max_cost_per_1k_input}"
                    )
                    continue

                # Check latency constraints
                if cap.expected_latency_ms > profile.max_latency_ms:
                    rejected_reasons.append(
                        f"{p_id}/{m_id} latency {cap.expected_latency_ms}ms exceeds max {profile.max_latency_ms}ms"
                    )
                    continue

                evaluated_candidates.append((p_id, m_id, cap))

        if not evaluated_candidates:
            raise ResolutionError(
                f"No provider/model satisfies profile '{profile_id}'. Reasons: {'; '.join(rejected_reasons)}"
            )

        # First matching candidate according to provider preference order is selected
        selected_provider_id, selected_model_id, selected_cap = evaluated_candidates[0]

        fallback_chain = [
            f"{p}/{m}" for p, m, _ in evaluated_candidates[1:]
        ]

        return ModelSelectionDecision(
            decision_id=f"dec_{uuid.uuid4().hex[:8]}",
            profile_id=profile_id,
            selected_provider_id=selected_provider_id,
            selected_model_id=selected_model_id,
            rationale=f"Satisfies all capabilities for '{profile_id}' via provider '{selected_provider_id}'",
            estimated_input_cost=selected_cap.estimated_cost_per_1k_input,
            confidence=1.0,
            fallback_chain=fallback_chain,
            epistemic_status=EpistemicStatus.VERIFIED,
        )

    @staticmethod
    def _check_missing_capabilities(required: set[str], vector: CapabilityVector) -> list[str]:
        """Verify which required capabilities are missing from vector."""
        missing = []
        vec_dict = vector.model_dump()
        for req in required:
            if req in vec_dict and not vec_dict[req]:
                missing.append(req)
            elif req not in vec_dict:
                missing.append(req)
        return missing
