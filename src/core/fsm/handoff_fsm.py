"""ACRA Handoff State Machine.

Implements ADR-004: HandoffStateMachine tracking inter-agent handoffs:
PREPARING -> AUDITING -> DISPATCHED -> RECEIVED -> VALIDATED | REJECTED.
Enforces INV-002 (mandatory pre-handoff audit before dispatch).
"""

from __future__ import annotations

from typing import Any
from src.core.contracts.handoff import HandoffEnvelope, HandoffState


class InvalidHandoffTransitionError(ValueError):
    """Raised when an illegal handoff transition is attempted."""
    pass


class HandoffStateMachine:
    """Finite state machine governing inter-agent handoff delegation."""

    VALID_TRANSITIONS: dict[HandoffState, set[HandoffState]] = {
        HandoffState.PREPARING: {HandoffState.AUDITING, HandoffState.REJECTED},
        HandoffState.AUDITING: {HandoffState.DISPATCHED, HandoffState.REJECTED},
        HandoffState.DISPATCHED: {HandoffState.RECEIVED, HandoffState.REJECTED},
        HandoffState.RECEIVED: {HandoffState.VALIDATED, HandoffState.REJECTED},
        HandoffState.VALIDATED: set(),  # Terminal
        HandoffState.REJECTED: set(),   # Terminal
    }

    def __init__(self, envelope_id: str, max_transitions: int = 15) -> None:
        self.envelope_id = envelope_id
        self.state = HandoffState.PREPARING
        self.max_transitions = max_transitions
        self.transition_count = 0
        self.history: list[dict[str, Any]] = [
            {"from": None, "to": self.state.value, "reason": "Handoff prepared"}
        ]

    def transition_to(
        self,
        target: HandoffState,
        envelope: HandoffEnvelope | None = None,
        reason: str = "",
    ) -> HandoffState:
        """Advance handoff state enforcing INV-002 audit check before DISPATCHED."""
        if self.transition_count >= self.max_transitions:
            raise InvalidHandoffTransitionError(
                f"Handoff '{self.envelope_id}' exceeded max transitions ({self.max_transitions}) - cycle guard (INV-008)"
            )

        if target not in self.VALID_TRANSITIONS.get(self.state, set()):
            raise InvalidHandoffTransitionError(
                f"Illegal handoff transition: cannot move from '{self.state.value}' to '{target.value}'"
            )

        # Enforce INV-002: cannot dispatch without passing pre-handoff audit
        if target == HandoffState.DISPATCHED:
            if envelope is None or not envelope.is_dispatchable():
                raise InvalidHandoffTransitionError(
                    f"INV-002 Violation: Handoff '{self.envelope_id}' cannot dispatch without passing pre-handoff audit"
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
        return self.state in {HandoffState.VALIDATED, HandoffState.REJECTED}
