"""ACRA Session State Machine.

Maintains backward compatibility with legacy ACRAStateMachine while
providing cycle guards and transition tracking (ADR-004, INV-008).
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class SystemState(str, Enum):
    """Session lifecycle states."""
    INTAKE = "intake"
    ANALYZING = "analyzing"
    COMPRESSING = "compressing"
    EVALUATING = "evaluating"
    HANDOFF_READY = "handoff_ready"
    DISPATCHED = "dispatched"
    POLICY_REJECTED = "policy_rejected"
    COMPLETED = "completed"
    TERMINATED = "terminated"


class InvalidSessionTransitionError(ValueError):
    """Raised when an invalid session FSM transition is attempted."""
    pass


class SessionStateMachine:
    """Manages high-level conversation session states."""

    VALID_TRANSITIONS: dict[SystemState, set[SystemState]] = {
        SystemState.INTAKE: {SystemState.ANALYZING, SystemState.POLICY_REJECTED, SystemState.TERMINATED},
        SystemState.ANALYZING: {SystemState.COMPRESSING, SystemState.POLICY_REJECTED, SystemState.TERMINATED},
        SystemState.COMPRESSING: {SystemState.EVALUATING, SystemState.POLICY_REJECTED, SystemState.TERMINATED},
        SystemState.EVALUATING: {
            SystemState.HANDOFF_READY,
            SystemState.COMPLETED,
            SystemState.POLICY_REJECTED,
            SystemState.TERMINATED,
        },
        SystemState.HANDOFF_READY: {SystemState.DISPATCHED, SystemState.POLICY_REJECTED, SystemState.TERMINATED},
        SystemState.DISPATCHED: {SystemState.COMPLETED, SystemState.TERMINATED},
        SystemState.POLICY_REJECTED: {SystemState.INTAKE, SystemState.TERMINATED},
        SystemState.COMPLETED: {SystemState.INTAKE, SystemState.TERMINATED},
        SystemState.TERMINATED: set(),
    }

    def __init__(self, session_id: str, max_transitions: int = 100) -> None:
        self.session_id = session_id
        self.state = SystemState.INTAKE
        self.max_transitions = max_transitions
        self.transition_count = 0
        self.history: list[dict[str, Any]] = [
            {"from": None, "to": self.state.value, "reason": "Session initialization"}
        ]

    def transition_to(self, next_state: SystemState, reason: str = "") -> SystemState:
        """Advance session state verifying validity and cycle limits (INV-008)."""
        if self.transition_count >= self.max_transitions:
            raise InvalidSessionTransitionError(
                f"Session '{self.session_id}' exceeded max transitions ({self.max_transitions}) - cycle guard (INV-008)"
            )

        if next_state not in self.VALID_TRANSITIONS.get(self.state, set()):
            raise InvalidSessionTransitionError(
                f"Invalid transition for session '{self.session_id}': cannot move from '{self.state.value}' to '{next_state.value}'"
            )

        prev = self.state
        self.state = next_state
        self.transition_count += 1
        self.history.append({
            "from": prev.value,
            "to": next_state.value,
            "reason": reason,
            "count": self.transition_count,
        })
        return self.state
