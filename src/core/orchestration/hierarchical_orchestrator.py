"""ACRA Hierarchical Agent Orchestrator.

Implements the top-level hierarchical orchestration pipeline:
Objective -> Intake Triage -> Planner -> Task DAG -> Capability Routing
-> Ephemeral Agent Execution -> Audited Handoffs -> Consolidation.
"""

from __future__ import annotations

import os
import json
import uuid
from typing import Any
from src.core.agents.factory import AgentFactory
from src.core.agents.registry import AgentRegistry
from src.core.audit.deterministic import DeterministicFallbackAuditor
from src.core.audit.policy_modes import GateAction, PolicyModeGate
from src.core.context.prefix import StablePrefixEngine
from src.core.contracts.agent import AgentDefinition, AgentInstanceState
from src.core.contracts.audit import AuditHookPoint, ContextAuditProvider, EpistemicStatus
from src.core.contracts.context import ContextBudget
from src.core.contracts.model import ModelProfile
from src.core.contracts.outcome import AgentOutcome, ConsolidatedOutcome
from src.core.fsm.objective import ObjectiveState
from src.core.orchestration.consolidator import Consolidator
from src.core.orchestration.objective_planner import ObjectivePlanner
from src.core.providers.base import ProviderAdapter
from src.core.providers.stub import DeterministicStubProvider
from src.core.routing.capability_router import CapabilityAndAgentRouter
from src.core.routing.intake_router import IntakeRouter
from src.core.routing.model_resolver import ModelCapabilityRegistry


class HierarchicalAgentOrchestrator:
    """Orchestrates multi-agent, capability-routed, audited workflows."""

    def __init__(
        self,
        agent_registry: AgentRegistry | None = None,
        model_registry: ModelCapabilityRegistry | None = None,
        audit_provider: ContextAuditProvider | None = None,
        provider_adapter: ProviderAdapter | None = None,
        policy_gate: PolicyModeGate | None = None,
    ) -> None:
        self.agent_registry = agent_registry or AgentRegistry()
        self.model_registry = model_registry or ModelCapabilityRegistry()
        self.audit_provider = audit_provider or DeterministicFallbackAuditor()
        self.provider = provider_adapter or DeterministicStubProvider()
        self.policy_gate = policy_gate or PolicyModeGate()

        # Auto-load default profiles and stub configs if available
        profiles_file = os.path.join("config", "profiles", "model_profiles.yaml")
        if os.path.exists(profiles_file) and not self.model_registry.get_profile("frontier_planner"):
            try:
                self.model_registry.load_profiles_from_yaml(profiles_file)
            except Exception:
                pass

        stub_file = os.path.join("config", "providers", "stub.yaml")
        if os.path.exists(stub_file) and isinstance(self.provider, DeterministicStubProvider):
            try:
                self.model_registry.load_provider_config_from_yaml(stub_file, self.provider)
            except Exception:
                pass

        self.intake_router = IntakeRouter()
        self.capability_router = CapabilityAndAgentRouter(
            agent_registry=self.agent_registry,
            model_registry=self.model_registry,
        )
        self.planner = ObjectivePlanner()
        self.agent_factory = AgentFactory()
        self.prefix_engine = StablePrefixEngine()
        self.consolidator = Consolidator(audit_provider=self.audit_provider)

        # Default fallback agent if registry is empty
        if not self.agent_registry.list_definitions():
            default_agent = AgentDefinition(
                agent_def_id="def_general_agent",
                name="General Purpose Agent",
                domain="general",
                description="Default generalist execution agent",
            )
            self.agent_registry.register_definition(default_agent)

    def execute_objective(
        self,
        objective_text: str,
        session_id: str | None = None,
        parent_budget: ContextBudget | None = None,
    ) -> ConsolidatedOutcome:
        """Execute a complete objective through the hierarchical pipeline."""
        obj_id = f"obj_{uuid.uuid4().hex[:8]}"

        # 1. Intake Triage
        classification = self.intake_router.classify(objective_text)

        # 2. Planning & Task DAG Decomposition
        task_graph, obj_fsm = self.planner.plan_and_decompose(
            objective_id=obj_id,
            objective_text=objective_text,
            classification=classification,
        )
        obj_fsm.transition_to(ObjectiveState.EXECUTING, reason="Starting task execution")

        # 3. Execution in Topological Order
        execution_order = task_graph.get_execution_order()
        outcomes: list[AgentOutcome] = []

        # Generate stable prefix for this session
        prefix = self.prefix_engine.build_prefix(
            prefix_id=f"pfx_{session_id or 'global'}",
            system_instruction="You are an autonomous enterprise ACRA agent complying with strict policy gates.",
            tool_manifest=[],
        )

        for task_id in execution_order:
            task = task_graph.tasks[task_id]
            task_fsm = task_graph.fsms[task_id]
            task_fsm.transition_to(task_fsm.VALID_TRANSITIONS[task_fsm.state].copy().pop())

            # A. Select matching Agent
            agent_def = self.capability_router.select_agent(task)

            # B. Create Ephemeral AgentInstance
            agent_instance, agent_fsm = self.agent_factory.create_instance(
                definition=agent_def,
                task_objective=task.description,
                stable_prefix=prefix,
                parent_budget=parent_budget,
            )
            agent_fsm.transition_to(AgentInstanceState.INITIALIZED)
            agent_fsm.transition_to(AgentInstanceState.ACTIVE)

            # C. Pre-inference Audit
            audit_res = self.audit_provider.audit(
                agent_instance.context_capsule,
                hook_point=AuditHookPoint.PRE_INFERENCE,
            )

            # D. Policy Gate Evaluation
            policy_dec = self.policy_gate.evaluate(audit_res, is_destructive=False)
            if policy_dec.action == GateAction.BLOCK:
                agent_fsm.transition_to(AgentInstanceState.REVOKED, reason="Blocked by policy gate")
                outcome = AgentOutcome(
                    outcome_id=f"out_{uuid.uuid4().hex[:8]}",
                    agent_instance_id=agent_instance.instance_id,
                    task_id=task_id,
                    status="FAILED",
                    payload={"error": f"Execution blocked: {policy_dec.reason}"},
                    confidence=0.0,
                    tokens_consumed=0,
                    cost_usd=0.0,
                    latency_ms=0,
                    epistemic_status=EpistemicStatus.VERIFIED,
                )
                outcomes.append(outcome)
                continue

            # E. Resolve Model & Execute Inference
            profile = self.model_registry.get_profile(agent_def.model_profile_id)
            if not profile:
                profile = self.model_registry.get_profile("lightweight_executor")
            if not profile:
                profile = ModelProfile(
                    profile_id="default_executor",
                    required_capabilities=set(),
                )

            provider_response = self.provider.generate(
                capsule=agent_instance.context_capsule,
                profile=profile,
            )

            # Parse content as structured payload
            try:
                payload = json.loads(provider_response.content)
            except Exception:
                payload = {"result": provider_response.content}

            agent_fsm.transition_to(AgentInstanceState.COMPLETED)
            agent_fsm.transition_to(AgentInstanceState.RETIRED)
            task_graph.mark_completed(task_id)

            outcome = AgentOutcome(
                outcome_id=f"out_{uuid.uuid4().hex[:8]}",
                agent_instance_id=agent_instance.instance_id,
                task_id=task_id,
                status="SUCCESS",
                payload=payload,
                confidence=0.95,
                tokens_consumed=provider_response.prompt_tokens + provider_response.completion_tokens,
                cost_usd=provider_response.cost_usd,
                latency_ms=provider_response.latency_ms,
                epistemic_status=EpistemicStatus.VERIFIED,
            )
            outcomes.append(outcome)

        # 4. Consolidate Results without context mixing (INV-003)
        obj_fsm.transition_to(ObjectiveState.CONSOLIDATING, reason="Aggregating agent outcomes")
        consolidated = self.consolidator.consolidate(
            objective_id=obj_id,
            outcomes=outcomes,
        )

        obj_fsm.transition_to(ObjectiveState.VALIDATED)
        obj_fsm.transition_to(ObjectiveState.COMPLETED)

        return consolidated
