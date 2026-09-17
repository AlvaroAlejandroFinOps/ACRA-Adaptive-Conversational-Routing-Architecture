"""ACRA Agent Instance State Machine.

Implements ADR-004: AgentInstanceStateMachine tracking the ephemeral lifecycle
from CREATED through ACTIVE to COMPLETED, RETIRED, or REVOKED.
Enforces INV-008 (deterministic transitions, cycle prevention).
"""

from __future__ import annotations

from typing import Any
from src.core.contracts.agent import AgentInstanceState


class InvalidStateTransitionError(ValueError):
    """Raised when an illegal FSM transition is attempted."""
    pass


class AgentInstanceStateMachine:
    """Deterministic finite state machine governing ephemeral AgentInstance lifecycles."""

    VALID_TRANSITIONS: dict[AgentInstanceState, set[AgentInstanceState]] = {
        AgentInstanceState.CREATED: {AgentInstanceState.INITIALIZED, AgentInstanceState.REVOKED},
        AgentInstanceState.INITIALIZED: {AgentInstanceState.ACTIVE, AgentInstanceState.REVOKED},
        AgentInstanceState.ACTIVE: {
            AgentInstanceState.SUSPENDED,
            AgentInstanceState.COMPLETED,
            AgentInstanceState.REVOKED,
        },
        AgentInstanceState.SUSPENDED: {
            AgentInstanceState.ACTIVE,
            AgentInstanceState.REVOKED,
            AgentInstanceState.RETIRED,
        },
        AgentInstanceState.COMPLETED: {AgentInstanceState.RETIRED},
        AgentInstanceState.RETIRED: set(),  # Terminal state
        AgentInstanceState.REVOKED: set(),  # Terminal state
    }

    def __init__(
        self,
        instance_id: str,
        initial_state: AgentInstanceState = AgentInstanceState.CREATED,
        max_transitions: int = 50,
    ) -> None:
        self.instance_id = instance_id
        self.state = initial_state
        self.max_transitions = max_transitions
        self.transition_count = 0
        self.history: list[dict[str, Any]] = [
            {"from": None, "to": initial_state.value, "reason": "Initial instantiation"}
        ]

    def can_transition_to(self, target_state: AgentInstanceState) -> bool:
        """Check if transition from current state to target state is legally allowed."""
        return target_state in self.VALID_TRANSITIONS.get(self.state, set())

    def transition_to(self, target_state: AgentInstanceState, reason: str = "") -> AgentInstanceState:
        """Execute a state transition, updating telemetry and checking cycle guards (INV-008)."""
        if self.transition_count >= self.max_transitions:
            raise InvalidStateTransitionError(
                f"AgentInstance '{self.instance_id}' exceeded max transitions ({self.max_transitions}) - cycle guard (INV-008)"
            )

        if not self.can_transition_to(target_state):
            raise InvalidStateTransitionError(
                f"Illegal state transition for agent '{self.instance_id}': cannot move from '{self.state.value}' to '{target_state.value}'"
            )

        old_state = self.state
        self.state = target_state
        self.transition_count += 1
        self.history.append({
            "from": old_state.value,
            "to": target_state.value,
            "reason": reason,
            "transition_index": self.transition_count,
        })
        return self.state

    def is_terminal(self) -> bool:
        """Check if machine has entered a terminal state."""
        return self.state in {AgentInstanceState.RETIRED, AgentInstanceState.REVOKED}

    def is_active(self) -> bool:
        """Check if instance is currently executing or active."""
        return self.state == AgentInstanceState.ACTIVE
