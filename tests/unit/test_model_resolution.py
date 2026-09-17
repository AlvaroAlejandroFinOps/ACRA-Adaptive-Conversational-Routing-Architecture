"""Unit tests for ACRA Model Resolution and Capability Registry (Phase 2).

Verifies capability-based resolution, fallback chains, and enforces INV-001
(no concrete model names in core domain code).
"""

import os
import re
import pytest

from src.core.contracts.context import ContextCapsule, StablePrefixDescriptor
from src.core.contracts.model import (
    CapabilityVector,
    ModelProfile,
    ModelSelectionDecision,
)
from src.core.providers.base import ProviderAdapter, ProviderResponse
from src.core.providers.stub import DeterministicStubProvider
from src.core.routing.model_resolver import (
    ModelCapabilityRegistry,
    ResolutionError,
)


@pytest.fixture
def configured_registry() -> ModelCapabilityRegistry:
    """Fixture initializing registry with profiles and stub provider."""
    registry = ModelCapabilityRegistry()
    profiles_path = os.path.join("config", "profiles", "model_profiles.yaml")
    stub_path = os.path.join("config", "providers", "stub.yaml")

    registry.load_profiles_from_yaml(profiles_path)
    stub_provider = DeterministicStubProvider(provider_id="stub")
    registry.load_provider_config_from_yaml(stub_path, stub_provider)
    return registry


class TestModelResolution:
    """Tests for capability matching and ModelProfile resolution (ADR-002)."""

    def test_all_seven_profiles_resolve(self, configured_registry: ModelCapabilityRegistry) -> None:
        """Verify all 7 defined profiles resolve successfully."""
        profiles = [
            "frontier_planner",
            "complex_reasoner",
            "domain_planner",
            "lightweight_executor",
            "classifier",
            "validator",
            "fallback_local",
        ]
        for p_id in profiles:
            decision = configured_registry.resolve(p_id)
            assert isinstance(decision, ModelSelectionDecision)
            assert decision.profile_id == p_id
            assert decision.selected_provider_id == "stub"
            assert decision.selected_model_id in [
                "stub-frontier-v1",
                "stub-reasoner-v1",
                "stub-fast-v1",
            ]
            assert decision.estimated_input_cost > 0.0

    def test_fallback_provider_chain(self) -> None:
        """Verify resolution falls back when preferred provider is unhealthy."""
        registry = ModelCapabilityRegistry()
        profile = ModelProfile(
            profile_id="test_fallback",
            required_capabilities={"structured_output"},
            preferred_provider="primary_cloud",
            fallback_providers=["secondary_cloud"],
        )
        registry.register_profile(profile)

        # Primary provider is unhealthy
        class UnhealthyProvider(DeterministicStubProvider):
            def health_check(self) -> bool:
                return False

        primary = UnhealthyProvider(provider_id="primary_cloud")
        secondary = DeterministicStubProvider(provider_id="secondary_cloud")

        registry.register_provider(primary)
        registry.register_provider(secondary)

        decision = registry.resolve("test_fallback")
        assert decision.selected_provider_id == "secondary_cloud"

    def test_unsatisfiable_capabilities_raises_resolution_error(self) -> None:
        """Verify ResolutionError raised when capability is missing."""
        registry = ModelCapabilityRegistry()
        profile = ModelProfile(
            profile_id="impossible_profile",
            required_capabilities={"multimodal"},  # Stub has multimodal=False
        )
        registry.register_profile(profile)
        registry.register_provider(DeterministicStubProvider(provider_id="stub"))

        with pytest.raises(ResolutionError, match="missing required capabilities"):
            registry.resolve("impossible_profile")


class TestProviderAdapterProtocol:
    """Tests for ProviderAdapter protocol and DeterministicStubProvider."""

    def test_stub_provider_inference(self) -> None:
        """Verify DeterministicStubProvider satisfies inference flow."""
        provider = DeterministicStubProvider(provider_id="stub")
        assert isinstance(provider, ProviderAdapter)

        prefix = StablePrefixDescriptor(
            prefix_id="pfx_1",
            content_hash="h1",
            token_count=100,
            system_instruction_hash="s1",
            tool_manifest_hash="t1",
        )
        capsule = ContextCapsule(
            capsule_id="cap_test",
            agent_instance_id="inst_1",
            domain="finance",
            stable_prefix=prefix,
            task_context="Analyze EBITDA margins",
            current_turn="User: What is the trend?",
        )
        profile = ModelProfile(profile_id="domain_planner")

        provider.set_canned_response("EBITDA", '{"margin": "24.5%"}')
        response = provider.generate(capsule, profile)

        assert isinstance(response, ProviderResponse)
        assert response.provider_id == "stub"
        assert '{"margin": "24.5%"}' in response.content
        assert response.prompt_tokens > 0
        assert response.cost_usd > 0.0
        assert len(provider.call_history) == 1


class TestInvariantNoModelNamesInCore:
    """Enforces INV-001: No concrete model names in core domain code."""

    BANNED_MODEL_PATTERNS = [
        r"gpt-4",
        r"gpt-3\.5",
        r"claude-3",
        r"claude-2",
        r"gemini-1\.5",
        r"gemini-2\.0",
        r"gemini-2\.5",
        r"llama-3",
        r"mistral-7b",
    ]

    ALLOWED_PATHS = [
        os.path.join("src", "core", "models"),       # Legacy adapters (being phased out)
        os.path.join("src", "core", "providers"),    # Provider adapters and stubs
        os.path.join("config"),                      # Configuration manifests
        os.path.join("tests"),                       # Tests fixtures and assertions
    ]

    def test_no_concrete_model_names_in_contracts_and_routing(self) -> None:
        """Verify zero concrete model identifiers in src/core/contracts/ and src/core/routing/."""
        dirs_to_check = [
            os.path.join("src", "core", "contracts"),
            os.path.join("src", "core", "routing"),
            os.path.join("src", "core", "security"),
            os.path.join("src", "core", "context"),
            os.path.join("src", "core", "orchestration"),
            os.path.join("src", "core", "fsm"),
            os.path.join("src", "core", "agents"),
            os.path.join("src", "core", "economy"),
        ]

        compiled_patterns = [re.compile(p, re.IGNORECASE) for p in self.BANNED_MODEL_PATTERNS]
        violations: list[str] = []

        for check_dir in dirs_to_check:
            for root, _, files in os.walk(check_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        for pattern in compiled_patterns:
                            matches = pattern.findall(content)
                            if matches:
                                violations.append(f"{file_path} matches banned model pattern '{matches[0]}'")

        assert not violations, f"INV-001 Violations found:\n" + "\n".join(violations)
