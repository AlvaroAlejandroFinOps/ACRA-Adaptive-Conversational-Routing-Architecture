"""Unit tests for ACRA Provider Adapters and Cache Hysteresis Routing (Phase 9).

Validates GoogleGenAIAdapter, AnthropicAdapter, OpenAIAdapter, LocalAdapter,
and tests CacheAwareRouter enforcing INV-010 (no model oscillation) and EVO ACRA §8-§9.
"""

import os
import pytest

from src.core.contracts.audit import AuditResult, EpistemicStatus
from src.core.contracts.cache import (
    CacheContinuityDescriptor,
    CacheInvalidationEvent,
    ContextRehydrationPlan,
    ModelMigrationDecision,
)
from src.core.contracts.context import ContextCapsule, StablePrefixDescriptor
from src.core.contracts.model import CapabilityVector, ModelProfile
from src.core.providers import (
    AnthropicAdapter,
    DeterministicStubProvider,
    GoogleGenAIAdapter,
    LocalAdapter,
    OpenAIAdapter,
    ProviderAdapter,
    ProviderResponse,
)
from src.core.routing.affinity import (
    CacheAwareRouter,
    HysteresisPolicy,
)


@pytest.fixture
def test_capsule() -> ContextCapsule:
    """Fixture providing standard ContextCapsule with stable prefix."""
    prefix = StablePrefixDescriptor(
        prefix_id="pfx_123",
        content_hash="hash_stable_prefix_v1",
        system_instruction_hash="sys_inst_v1",
        tool_manifest_hash="tool_manifest_v1",
        token_count=120,
    )
    return ContextCapsule(
        capsule_id="cap_001",
        agent_instance_id="inst_001",
        domain="finance",
        stable_prefix=prefix,
        task_context="Calculate debt-to-equity ratio",
        current_turn="User: Provide ratio for 2025",
    )


class TestProviderAdaptersProtocolAdherence:
    """Verifies all adapters fulfill ProviderAdapter Protocol."""

    def test_google_adapter_protocol(self, test_capsule: ContextCapsule) -> None:
        """Verify GoogleGenAIAdapter complies with protocol and reports capabilities."""
        adapter = GoogleGenAIAdapter(force_simulation=True)
        assert isinstance(adapter, ProviderAdapter)
        assert adapter.get_provider_id() == "google"
        assert adapter.health_check() is True

        caps = adapter.get_capabilities()
        assert isinstance(caps, CapabilityVector)
        assert caps.structured_output is True

        profile = ModelProfile(profile_id="domain_planner")
        response = adapter.generate(test_capsule, profile)
        assert isinstance(response, ProviderResponse)
        assert response.provider_id == "google"
        assert response.prompt_tokens > 0
        assert response.cached_tokens == 120

        descriptor = adapter.get_cache_descriptor("inst_001")
        assert descriptor is not None
        assert descriptor.provider_id == "google"
        assert descriptor.stable_prefix_hash == "hash_stable_prefix_v1"

    def test_anthropic_adapter_protocol(self, test_capsule: ContextCapsule) -> None:
        """Verify AnthropicAdapter complies with protocol and calculates 90% cache discount."""
        adapter = AnthropicAdapter(force_simulation=True)
        assert isinstance(adapter, ProviderAdapter)
        assert adapter.get_provider_id() == "anthropic"

        caps = adapter.get_capabilities()
        assert isinstance(caps, CapabilityVector)

        cost_no_cache = adapter.estimate_cost(input_tokens=1000, output_tokens=200, cached_tokens=0)
        cost_with_cache = adapter.estimate_cost(input_tokens=1000, output_tokens=200, cached_tokens=800)
        assert cost_with_cache < cost_no_cache

        profile = ModelProfile(profile_id="complex_reasoner")
        response = adapter.generate(test_capsule, profile)
        assert response.provider_id == "anthropic"
        assert response.cached_tokens == 120

    def test_openai_adapter_protocol(self, test_capsule: ContextCapsule) -> None:
        """Verify OpenAIAdapter complies with protocol."""
        adapter = OpenAIAdapter(force_simulation=True)
        assert isinstance(adapter, ProviderAdapter)
        assert adapter.get_provider_id() == "openai"

        profile = ModelProfile(profile_id="lightweight_executor")
        response = adapter.generate(test_capsule, profile)
        assert response.provider_id == "openai"
        assert response.cached_tokens == 120

    def test_local_adapter_protocol(self, test_capsule: ContextCapsule) -> None:
        """Verify LocalAdapter reports zero financial cost."""
        adapter = LocalAdapter()
        assert isinstance(adapter, ProviderAdapter)
        assert adapter.get_provider_id() == "local"

        cost = adapter.estimate_cost(input_tokens=5000, output_tokens=1000)
        assert cost == 0.0

        profile = ModelProfile(profile_id="fallback_local")
        response = adapter.generate(test_capsule, profile)
        assert response.cost_usd == 0.0


class TestCacheHysteresisAndAffinity:
    """Verifies CacheAwareRouter and HysteresisPolicy (EVO ACRA §8-§9, INV-010)."""

    @pytest.fixture
    def router(self) -> CacheAwareRouter:
        policy_path = os.path.join("config", "policies", "hysteresis.yaml")
        policy = HysteresisPolicy.from_yaml(policy_path)
        return CacheAwareRouter(policy=policy)

    def test_hysteresis_policy_loaded(self, router: CacheAwareRouter) -> None:
        """Verify 10 parameters loaded from YAML manifest."""
        p = router.policy
        assert p.minimum_affinity_turns == 3
        assert p.minimum_affinity_duration_sec == 60.0
        assert p.switch_cooldown_turns == 2
        assert p.minimum_expected_savings_usd == 0.005
        assert p.maximum_model_switches_per_task == 2
        assert p.maximum_provider_switches_per_workflow == 3
        assert p.migration_risk_threshold == 0.60
        assert p.required_capability_delta == 0.20
        assert p.cache_rebuild_break_even_turns == 4
        assert p.emergency_override is True

    def test_affinity_maintained_when_candidate_matches(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Affinity is maintained when candidate model is identical to bound model."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="gemini-2.5-flash",
        )
        caps = CapabilityVector(structured_output=True)
        decision = router.evaluate_migration(
            affinity=affinity,
            candidate_provider_id="google",
            candidate_model_id="gemini-2.5-flash",
            candidate_profile=ModelProfile(profile_id="lightweight_executor"),
            current_capsule=test_capsule,
            current_capabilities=caps,
            candidate_capabilities=caps,
        )
        assert decision.should_migrate is False
        assert "matches current affinity" in decision.reason

    def test_affinity_maintained_when_savings_below_minimum_threshold(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Affinity rule: do not migrate for negligible savings (< $0.005)."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="model_a",
        )
        # Advance turns to satisfy cooldown
        affinity.consecutive_turns_served = 5
        affinity.turns_since_last_switch = 5

        current_caps = CapabilityVector(estimated_cost_per_1k_input=0.00010)
        candidate_caps = CapabilityVector(estimated_cost_per_1k_input=0.00009)  # Marginal diff

        decision = router.evaluate_migration(
            affinity=affinity,
            candidate_provider_id="google",
            candidate_model_id="model_b",
            candidate_profile=ModelProfile(profile_id="lightweight_executor"),
            current_capsule=test_capsule,
            current_capabilities=current_caps,
            candidate_capabilities=candidate_caps,
        )
        assert decision.should_migrate is False
        assert "below minimum threshold" in decision.reason

    def test_migration_triggered_on_missing_capability(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Migration trigger: current model lacks required reasoning capability."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="model_fast",
        )
        current_caps = CapabilityVector(reasoning=False)
        candidate_caps = CapabilityVector(reasoning=True)
        profile = ModelProfile(
            profile_id="complex_reasoner",
            required_capabilities={"reasoning"},
        )

        decision = router.evaluate_migration(
            affinity=affinity,
            candidate_provider_id="google",
            candidate_model_id="model_reasoner",
            candidate_profile=profile,
            current_capsule=test_capsule,
            current_capabilities=current_caps,
            candidate_capabilities=candidate_caps,
        )
        assert decision.should_migrate is True
        assert "lacks required capabilities" in decision.reason

    def test_migration_triggered_on_high_context_risk(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Migration trigger: context risk exceeds threshold."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="model_fast",
        )
        from src.core.contracts.audit import AuditHookPoint, AuditTriple
        audit = AuditResult(
            audit_id="aud_test_risk",
            hook_point=AuditHookPoint.PRE_INFERENCE,
            triple=AuditTriple(
                risk_score=0.75,  # >= 0.60
                confidence=0.9,
                evidence_coverage=0.85,
            ),
        )
        caps = CapabilityVector()
        decision = router.evaluate_migration(
            affinity=affinity,
            candidate_provider_id="google",
            candidate_model_id="model_pro",
            candidate_profile=ModelProfile(profile_id="validator"),
            current_capsule=test_capsule,
            current_capabilities=caps,
            candidate_capabilities=caps,
            audit_result=audit,
        )
        assert decision.should_migrate is True
        assert "exceeds threshold" in decision.reason

    def test_anti_oscillation_blocks_excessive_switches(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Enforce INV-010: maximum_model_switches_per_task blocks oscillation."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="model_fast",
        )
        affinity.switches_in_task = 2  # Max limit reached
        affinity.turns_since_last_switch = 10

        caps = CapabilityVector()
        decision = router.evaluate_migration(
            affinity=affinity,
            candidate_provider_id="google",
            candidate_model_id="model_pro",
            candidate_profile=ModelProfile(profile_id="validator"),
            current_capsule=test_capsule,
            current_capabilities=caps,
            candidate_capabilities=caps,
        )
        assert decision.should_migrate is False
        assert "maximum task switches reached" in decision.reason

    def test_emergency_override_bypasses_oscillation_lock(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Emergency override triggers when provider is unhealthy despite switch lock."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="model_fast",
        )
        affinity.switches_in_task = 5  # Heavily capped
        caps = CapabilityVector()

        decision = router.evaluate_migration(
            affinity=affinity,
            candidate_provider_id="anthropic",
            candidate_model_id="model_fallback",
            candidate_profile=ModelProfile(profile_id="validator"),
            current_capsule=test_capsule,
            current_capabilities=caps,
            candidate_capabilities=caps,
            provider_healthy=False,  # Outage!
        )
        assert decision.should_migrate is True
        assert "Emergency override" in decision.reason

    def test_cache_invalidation_and_rehydration_plan(
        self, router: CacheAwareRouter, test_capsule: ContextCapsule
    ) -> None:
        """Verify stable prefix changes invalidate cache and generate rehydration plan."""
        affinity = router.get_or_create_affinity(
            agent_def_id="def_1",
            agent_instance_id="inst_001",
            session_id="sess_001",
            initial_provider_id="google",
            initial_model_id="model_fast",
        )
        affinity.active_prefix_hash = "old_prefix_hash"

        event = router.check_context_invalidation(affinity, test_capsule)
        assert isinstance(event, CacheInvalidationEvent)
        assert "changed from old_pref to hash_sta" in event.reason

        plan = router.generate_rehydration_plan(target_model_id="model_pro", capsule=test_capsule)
        assert isinstance(plan, ContextRehydrationPlan)
        assert plan.expected_tokens >= 120
        assert len(plan.steps) == 3
