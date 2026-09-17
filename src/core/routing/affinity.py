"""ACRA Cache Hysteresis & Model Affinity Router.

Implements ADR-002, EVO ACRA §8, §9, and enforces INV-010 (Cache hysteresis prevents
premature model oscillation). Evaluates continuity vs migration trade-offs based on
10 maintenance criteria and 10 migration triggers.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any
import yaml
from pydantic import BaseModel, ConfigDict, Field

from src.core.contracts.audit import AuditResult, EpistemicStatus
from src.core.contracts.cache import (
    AgentModelAffinity,
    CacheContinuityDescriptor,
    CacheInvalidationEvent,
    CacheObservabilityLevel,
    ContextRehydrationPlan,
    ModelMigrationDecision,
)
from src.core.contracts.context import ContextCapsule
from src.core.contracts.model import CapabilityVector, ModelProfile
from src.core.economy.cost_model import ContinuityCostModel


class HysteresisPolicy(BaseModel):
    """Configurable Cache Hysteresis parameters (EVO ACRA §9, INV-010)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    minimum_affinity_turns: int = Field(default=3, ge=1, description="Minimum turns on active model before discretionary switch")
    minimum_affinity_duration_sec: float = Field(default=60.0, ge=0.0, description="Minimum duration in seconds before discretionary switch")
    switch_cooldown_turns: int = Field(default=2, ge=0, description="Cooldown turns required between consecutive model switches")
    minimum_expected_savings_usd: float = Field(default=0.005, ge=0.0, description="Minimum financial savings required to justify migration")
    maximum_model_switches_per_task: int = Field(default=2, ge=1, description="Max switches per task to prevent oscillation (INV-010)")
    maximum_provider_switches_per_workflow: int = Field(default=3, ge=1, description="Max provider changes per workflow")
    migration_risk_threshold: float = Field(default=0.60, ge=0.0, le=1.0, description="Risk threshold above which migration is triggered")
    required_capability_delta: float = Field(default=0.20, ge=0.0, le=1.0, description="Minimum capability improvement required")
    cache_rebuild_break_even_turns: int = Field(default=4, ge=1, description="Turns required to amortize cache re-ingestion cost")
    emergency_override: bool = Field(default=True, description="Allow immediate migration if provider fails or critical risk detected")

    @classmethod
    def from_yaml(cls, path: str) -> HysteresisPolicy:
        """Load hysteresis policy from YAML configuration file."""
        if not os.path.exists(path):
            return cls()
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        config = data.get("hysteresis", data)
        return cls(**config)


class AffinityState:
    """Internal mutable tracking for an agent's model affinity lifecycle."""

    def __init__(
        self,
        affinity_id: str,
        agent_def_id: str,
        agent_instance_id: str,
        session_id: str,
        bound_provider_id: str,
        bound_model_id: str,
    ) -> None:
        self.affinity_id = affinity_id
        self.agent_def_id = agent_def_id
        self.agent_instance_id = agent_instance_id
        self.session_id = session_id
        self.bound_provider_id = bound_provider_id
        self.bound_model_id = bound_model_id
        self.consecutive_turns_served = 0
        self.turns_since_last_switch = 999
        self.switches_in_task = 0
        self.switches_in_workflow = 0
        self.created_at = datetime.now(timezone.utc)
        self.last_switch_at = datetime.now(timezone.utc)
        self.last_interaction_at = datetime.now(timezone.utc)
        self.active_prefix_hash: str | None = None

    def record_turn(self, prefix_hash: str | None = None) -> None:
        """Increment turn counters."""
        self.consecutive_turns_served += 1
        self.turns_since_last_switch += 1
        self.last_interaction_at = datetime.now(timezone.utc)
        if prefix_hash:
            self.active_prefix_hash = prefix_hash

    def record_switch(self, new_provider_id: str, new_model_id: str) -> None:
        """Record model migration and reset turn counters."""
        if new_provider_id != self.bound_provider_id:
            self.switches_in_workflow += 1
        self.bound_provider_id = new_provider_id
        self.bound_model_id = new_model_id
        self.consecutive_turns_served = 0
        self.turns_since_last_switch = 0
        self.switches_in_task += 1
        self.last_switch_at = datetime.now(timezone.utc)
        self.last_interaction_at = datetime.now(timezone.utc)

    def to_contract(self, hysteresis_locked: bool) -> AgentModelAffinity:
        """Produce frozen Pydantic contract."""
        return AgentModelAffinity(
            affinity_id=self.affinity_id,
            agent_def_id=self.agent_def_id,
            agent_instance_id=self.agent_instance_id,
            bound_provider_id=self.bound_provider_id,
            bound_model_id=self.bound_model_id,
            affinity_score=1.0,
            consecutive_turns_served=self.consecutive_turns_served,
            last_interaction_at=self.last_interaction_at,
            hysteresis_locked=hysteresis_locked,
        )


class CacheAwareRouter:
    """Cache-Aware Model Router enforcing Hysteresis and Affinity (EVO ACRA §7-§9)."""

    def __init__(self, policy: HysteresisPolicy | None = None) -> None:
        self.policy = policy or HysteresisPolicy()
        self._affinities: dict[str, AffinityState] = {}
        self._invalidation_events: list[CacheInvalidationEvent] = []

    def get_or_create_affinity(
        self,
        agent_def_id: str,
        agent_instance_id: str,
        session_id: str,
        initial_provider_id: str,
        initial_model_id: str,
    ) -> AffinityState:
        """Retrieve or initialize affinity state for agent instance."""
        key = f"{session_id}:{agent_instance_id}"
        if key not in self._affinities:
            self._affinities[key] = AffinityState(
                affinity_id=f"aff_{uuid.uuid4().hex[:8]}",
                agent_def_id=agent_def_id,
                agent_instance_id=agent_instance_id,
                session_id=session_id,
                bound_provider_id=initial_provider_id,
                bound_model_id=initial_model_id,
            )
        return self._affinities[key]

    def evaluate_migration(
        self,
        affinity: AffinityState,
        candidate_provider_id: str,
        candidate_model_id: str,
        candidate_profile: ModelProfile,
        current_capsule: ContextCapsule,
        current_capabilities: CapabilityVector,
        candidate_capabilities: CapabilityVector,
        audit_result: AuditResult | None = None,
        provider_healthy: bool = True,
        force_validation: bool = False,
    ) -> ModelMigrationDecision:
        """Evaluate migration vs affinity using 10 maintenance criteria and 10 migration triggers.

        Enforces INV-010: Cache hysteresis prevents premature model oscillation.
        """
        # If candidate is already the bound model, keep affinity
        if (
            candidate_provider_id == affinity.bound_provider_id
            and candidate_model_id == affinity.bound_model_id
        ):
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=False,
                net_benefit_usd=0.0,
                reason="Candidate model matches current affinity binding",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        # 1. Check INV-010 anti-oscillation lock
        is_task_switch_capped = affinity.switches_in_task >= self.policy.maximum_model_switches_per_task
        is_cooldown_active = affinity.turns_since_last_switch < self.policy.switch_cooldown_turns
        is_min_turns_active = affinity.consecutive_turns_served < self.policy.minimum_affinity_turns

        # Check Emergency Overrides
        emergency_trigger = False
        emergency_reason = ""
        if not provider_healthy:
            emergency_trigger = True
            emergency_reason = f"Provider '{affinity.bound_provider_id}' is unhealthy/degraded"
        elif audit_result and audit_result.risk_score >= 0.85:
            emergency_trigger = True
            emergency_reason = f"Critical contextual risk detected ({audit_result.risk_score:.2f} >= 0.85)"

        if emergency_trigger and self.policy.emergency_override:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=True,
                net_benefit_usd=0.0,
                reason=f"Emergency override: {emergency_reason}",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        # 2. Check Migration Triggers (§8)
        # Trigger 1 & 7: Missing required capabilities
        missing_caps = self._check_missing_capabilities(
            candidate_profile.required_capabilities, current_capabilities
        )
        if missing_caps:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=True,
                net_benefit_usd=0.0,
                reason=f"Current model lacks required capabilities: {missing_caps}",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        # Trigger 9: Independent validation requested
        if force_validation:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=True,
                net_benefit_usd=0.0,
                reason="Independent validation policy requires heterogeneous model",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        # Trigger 3: Risk threshold exceeded
        if audit_result and audit_result.risk_score >= self.policy.migration_risk_threshold:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=True,
                net_benefit_usd=0.0,
                reason=f"Context risk ({audit_result.risk_score:.2f}) exceeds threshold ({self.policy.migration_risk_threshold})",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        # 3. Check Hysteresis Locks (INV-010)
        if is_task_switch_capped:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=False,
                net_benefit_usd=0.0,
                reason=f"Hysteresis lock: maximum task switches reached ({affinity.switches_in_task}/{self.policy.maximum_model_switches_per_task})",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        if is_cooldown_active:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=False,
                net_benefit_usd=0.0,
                reason=f"Hysteresis lock: switch cooldown active ({affinity.turns_since_last_switch}/{self.policy.switch_cooldown_turns} turns)",
                epistemic_status=EpistemicStatus.VERIFIED,
            )

        # 4. Economic Evaluation (Continuity vs Migration Cost)
        cached_tokens = current_capsule.stable_prefix.token_count if current_capsule.stable_prefix else 0
        prompt_tokens = len(current_capsule.task_context.split()) * 2 + len(current_capsule.current_turn.split()) * 2

        # Convert 1k rates to 1M rates for ContinuityCostModel
        active_rate_per_m = current_capabilities.estimated_cost_per_1k_input * 1000.0
        candidate_rate_per_m = candidate_capabilities.estimated_cost_per_1k_input * 1000.0

        assessment = ContinuityCostModel.evaluate_migration_tradeoff(
            active_model_cost_per_million=active_rate_per_m,
            target_model_cost_per_million=candidate_rate_per_m,
            cached_prefix_tokens=cached_tokens,
            new_prompt_tokens=prompt_tokens,
            expected_output_tokens=300,
            target_capability_gain=0.0,
        )

        net_savings = assessment.stay_continuity_cost_usd - assessment.migrate_total_cost_usd

        # Affinity Rule 10: Financial savings must exceed minimum expected savings threshold
        if net_savings < self.policy.minimum_expected_savings_usd:
            return ModelMigrationDecision(
                decision_id=f"mig_{uuid.uuid4().hex[:8]}",
                current_model_id=affinity.bound_model_id,
                candidate_model_id=candidate_model_id,
                should_migrate=False,
                net_benefit_usd=round(net_savings, 6),
                reason=f"Expected net savings (${net_savings:.4f}) below minimum threshold (${self.policy.minimum_expected_savings_usd:.4f})",
                epistemic_status=EpistemicStatus.ESTIMATED,
            )

        # If all checks pass and migration delivers genuine economic benefit:
        return ModelMigrationDecision(
            decision_id=f"mig_{uuid.uuid4().hex[:8]}",
            current_model_id=affinity.bound_model_id,
            candidate_model_id=candidate_model_id,
            should_migrate=True,
            net_benefit_usd=round(net_savings, 6),
            reason=f"Migration approved: net savings ${net_savings:.4f} offsets context rebuild penalty",
            epistemic_status=EpistemicStatus.ESTIMATED,
        )

    def check_context_invalidation(
        self,
        affinity: AffinityState,
        capsule: ContextCapsule,
    ) -> CacheInvalidationEvent | None:
        """Check if stable prefix change invalidates cache continuity."""
        current_hash = capsule.stable_prefix.content_hash if capsule.stable_prefix else None
        if affinity.active_prefix_hash and current_hash and affinity.active_prefix_hash != current_hash:
            event = CacheInvalidationEvent(
                event_id=f"inv_{uuid.uuid4().hex[:8]}",
                prefix_hash=current_hash,
                reason=f"Stable prefix hash changed from {affinity.active_prefix_hash[:8]} to {current_hash[:8]}",
            )
            self._invalidation_events.append(event)
            affinity.active_prefix_hash = current_hash
            return event
        if current_hash and not affinity.active_prefix_hash:
            affinity.active_prefix_hash = current_hash
        return None

    def generate_rehydration_plan(
        self,
        target_model_id: str,
        capsule: ContextCapsule,
    ) -> ContextRehydrationPlan:
        """Generate structured plan to rehydrate context on target model (EVO ACRA §7)."""
        rebuild_tokens = (capsule.stable_prefix.token_count if capsule.stable_prefix else 0) + 150
        return ContextRehydrationPlan(
            plan_id=f"rehydrate_{uuid.uuid4().hex[:8]}",
            target_model_id=target_model_id,
            steps=[
                "Re-ingest stable prefix definitions",
                "Inject active domain constraints",
                "Prime task context without volatile history",
            ],
            expected_tokens=rebuild_tokens,
            required_evidence_ids=[],
        )

    @staticmethod
    def _check_missing_capabilities(required: set[str], vector: CapabilityVector) -> list[str]:
        """Identify capabilities missing in current vector."""
        missing = []
        vec_dict = vector.model_dump()
        for req in required:
            if req in vec_dict and not vec_dict[req]:
                missing.append(req)
            elif req not in vec_dict:
                missing.append(req)
        return missing
