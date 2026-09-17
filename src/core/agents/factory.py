"""ACRA Agent Factory.

Implements AgentFactory creating ephemeral AgentInstance runtimes (ADR-003).
Enforces hierarchical budget cascading (INV-005) and isolated ContextCapsules (INV-003).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any
from src.core.agents.lifecycle import AgentInstanceStateMachine
from src.core.context.capsule import ContextCapsuleBuilder
from src.core.contracts.agent import (
    AgentDefinition,
    AgentInstance,
    AgentInstanceState,
)
from src.core.contracts.context import (
    ContextBudget,
    ContextCapsule,
    StablePrefixDescriptor,
)


class AgentFactory:
    """Factory responsible for instantiating ephemeral AgentInstances and their FSMs."""

    def __init__(self, default_ttl_seconds: int = 1800) -> None:
        self.default_ttl_seconds = default_ttl_seconds

    def create_instance(
        self,
        definition: AgentDefinition,
        task_objective: str,
        stable_prefix: StablePrefixDescriptor,
        parent_budget: ContextBudget | None = None,
        allocated_tokens: int | None = None,
        allocated_cost_usd: float | None = None,
        ttl_seconds: int | None = None,
        parent_instance_id: str | None = None,
        domain_context: str | None = None,
    ) -> tuple[AgentInstance, AgentInstanceStateMachine]:
        """Create an ephemeral AgentInstance and its corresponding lifecycle state machine."""
        instance_id = f"inst_{definition.domain}_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        ttl = ttl_seconds or self.default_ttl_seconds
        expires_at = datetime.fromtimestamp(now.timestamp() + ttl, timezone.utc)

        # Cascaded Budget allocation (INV-005)
        if parent_budget:
            token_ceiling = min(
                allocated_tokens or definition.max_context_tokens,
                parent_budget.remaining_tokens(),
            )
            cost_ceiling = min(
                allocated_cost_usd or 0.25,
                parent_budget.remaining_cost_usd(),
            )
        else:
            token_ceiling = allocated_tokens or definition.max_context_tokens
            cost_ceiling = allocated_cost_usd or 0.25

        budget = ContextBudget(
            max_tokens=max(500, token_ceiling),
            max_turns=10,
            max_cost_usd=max(0.01, cost_ceiling),
            consumed_tokens=0,
            consumed_cost_usd=0.0,
        )

        # Isolated ContextCapsule creation (INV-003)
        capsule_builder = ContextCapsuleBuilder(
            agent_instance_id=instance_id,
            domain=definition.domain,
            stable_prefix=stable_prefix,
        )
        capsule_builder.set_task_context(task_objective)
        capsule_builder.set_domain_context(domain_context or definition.description)
        capsule_builder.set_output_contract(definition.output_contract)
        capsule_builder.set_expiration(expires_at)
        if parent_instance_id:
            capsule_builder.set_parent(parent_instance_id)

        capsule = capsule_builder.build_and_seal()

        # Instantiate ephemeral AgentInstance
        instance = AgentInstance(
            instance_id=instance_id,
            definition_id=definition.agent_def_id,
            state=AgentInstanceState.CREATED,
            context_capsule=capsule,
            budget=budget,
            model_affinity_id=None,
            created_at=now,
            expires_at=expires_at,
            parent_instance_id=parent_instance_id,
        )

        # Instantiate deterministic FSM
        fsm = AgentInstanceStateMachine(
            instance_id=instance_id,
            initial_state=AgentInstanceState.CREATED,
        )

        return instance, fsm
