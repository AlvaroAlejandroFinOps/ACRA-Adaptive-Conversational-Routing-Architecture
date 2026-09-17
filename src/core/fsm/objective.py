"""ACRA Objective State Machine.

Implements ADR-004: ObjectiveStateMachine governing high-level user goal resolution:
RECEIVED -> PLANNING -> DECOMPOSED -> EXECUTING -> CONSOLIDATING -> VALIDATED -> COMPLETED | FAILED.
Enforces INV-008.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class ObjectiveState(str, Enum):
    """Lifecycle states for a top-level user objective."""
    RECEIVED = "RECEIVED"
    PLANNING = "PLANNING"
    DECOMPOSED = "DECOMPOSED"
    EXECUTING = "EXECUTING"
    CONSOLIDATING = "CONSOLIDATING"
    VALIDATED = "VALIDATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class InvalidObjectiveTransitionError(ValueError):
    """Raised when an invalid objective FSM transition is attempted."""
    pass


class ObjectiveStateMachine:
    """Finite state machine tracking objective decomposition and resolution."""

    VALID_TRANSITIONS: dict[ObjectiveState, set[ObjectiveState]] = {
        ObjectiveState.RECEIVED: {ObjectiveState.PLANNING, ObjectiveState.FAILED},
        ObjectiveState.PLANNING: {ObjectiveState.DECOMPOSED, ObjectiveState.FAILED},
        ObjectiveState.DECOMPOSED: {ObjectiveState.EXECUTING, ObjectiveState.FAILED},
        ObjectiveState.EXECUTING: {ObjectiveState.CONSOLIDATING, ObjectiveState.FAILED, ObjectiveState.PLANNING},
        ObjectiveState.CONSOLIDATING: {ObjectiveState.VALIDATED, ObjectiveState.EXECUTING, ObjectiveState.FAILED},
        ObjectiveState.VALIDATED: {ObjectiveState.COMPLETED, ObjectiveState.FAILED},
        ObjectiveState.COMPLETED: set(),  # Terminal
        ObjectiveState.FAILED: set(),     # Terminal
    }

    def __init__(self, objective_id: str, max_transitions: int = 50) -> None:
        self.objective_id = objective_id
        self.state = ObjectiveState.RECEIVED
        self.max_transitions = max_transitions
        self.transition_count = 0
        self.history: list[dict[str, Any]] = [
            {"from": None, "to": self.state.value, "reason": "Objective submitted"}
        ]

    def transition_to(self, target: ObjectiveState, reason: str = "") -> ObjectiveState:
        """Advance objective state checking validity and cycle limits (INV-008)."""
        if self.transition_count >= self.max_transitions:
            raise InvalidObjectiveTransitionError(
                f"Objective '{self.objective_id}' exceeded max transitions ({self.max_transitions}) - cycle guard (INV-008)"
            )

        if target not in self.VALID_TRANSITIONS.get(self.state, set()):
            raise InvalidObjectiveTransitionError(
                f"Illegal objective transition: cannot move from '{self.state.value}' to '{target.value}'"
            )

        prev = self.state
        self.state = target
        self.transition_count += 1
        self.history.append({
            "from": prev.value,
            "to": target.value,
            "reason": reason,
            "count": self.transition_count,
        })
        return self.state

    def is_terminal(self) -> bool:
        """Check if terminal state has been reached."""
        return self.state in {ObjectiveState.COMPLETED, ObjectiveState.FAILED}
