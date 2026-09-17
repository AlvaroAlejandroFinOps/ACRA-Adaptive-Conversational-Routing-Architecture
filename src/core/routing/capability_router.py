"""ACRA Capability and Agent Router.

Routes decomposed tasks to candidate agents and assigns resolved model profiles
based on declared capabilities (R-004, ADR-002).
"""

from __future__ import annotations

from typing import Any
from src.core.agents.registry import AgentRegistry
from src.core.contracts.agent import AgentDefinition
from src.core.contracts.model import ModelSelectionDecision
from src.core.contracts.task import TaskDefinition
from src.core.routing.model_resolver import ModelCapabilityRegistry


class RoutingError(Exception):
    """Raised when no suitable agent or model can be routed."""
    pass


class CapabilityAndAgentRouter:
    """Matches task requirements against AgentRegistry and ModelCapabilityRegistry."""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        model_registry: ModelCapabilityRegistry,
    ) -> None:
        self.agent_registry = agent_registry
        self.model_registry = model_registry

    def select_agent(self, task: TaskDefinition) -> AgentDefinition:
        """Find an AgentDefinition capable of handling the task."""
        candidates = self.agent_registry.list_definitions(domain=task.target_domain)
        if not candidates:
            # Fall back to general domain or first available
            candidates = self.agent_registry.list_definitions(domain="general")
        if not candidates:
            candidates = self.agent_registry.list_definitions()

        if not candidates:
            raise RoutingError(f"No agent registered for domain '{task.target_domain}'")

        # Select agent satisfying the most requested capabilities
        best_agent = candidates[0]
        max_overlap = -1
        req_set = set(task.required_capabilities)

        for agent in candidates:
            agent_caps = {c.name for c in agent.capabilities}
            overlap = len(req_set.intersection(agent_caps))
            if overlap > max_overlap:
                max_overlap = overlap
                best_agent = agent

        return best_agent

    def resolve_model_for_agent(self, agent: AgentDefinition) -> ModelSelectionDecision:
        """Resolve a concrete provider model matching the agent's ModelProfile."""
        return self.model_registry.resolve(agent.model_profile_id)
