"""ACRA Task State Machine.

Implements ADR-004: TaskStateMachine tracking atomic task execution within the Task DAG:
PENDING -> ASSIGNED -> EXECUTING -> VALIDATING -> COMPLETED | FAILED | ESCALATED.
Enforces INV-008.
"""

from __future__ import annotations

from typing import Any
from src.core.contracts.task import TaskState


class InvalidTaskTransitionError(ValueError):
    """Raised when an illegal task transition is attempted."""
    pass


class TaskStateMachine:
    """Finite state machine tracking individual task units in the TaskGraph."""

    VALID_TRANSITIONS: dict[TaskState, set[TaskState]] = {
        TaskState.PENDING: {TaskState.ASSIGNED, TaskState.FAILED},
        TaskState.ASSIGNED: {TaskState.EXECUTING, TaskState.FAILED, TaskState.PENDING},
        TaskState.EXECUTING: {
            TaskState.VALIDATING,
            TaskState.FAILED,
            TaskState.ESCALATED,
        },
        TaskState.VALIDATING: {
            TaskState.COMPLETED,
            TaskState.FAILED,
            TaskState.EXECUTING,  # Retry/remediation
        },
        TaskState.ESCALATED: {TaskState.ASSIGNED, TaskState.FAILED},
        TaskState.COMPLETED: set(),  # Terminal
        TaskState.FAILED: set(),     # Terminal
    }

    def __init__(self, task_id: str, max_transitions: int = 30) -> None:
        self.task_id = task_id
        self.state = TaskState.PENDING
        self.max_transitions = max_transitions
        self.transition_count = 0
        self.history: list[dict[str, Any]] = [
            {"from": None, "to": self.state.value, "reason": "Task initialized"}
        ]

    def transition_to(self, target: TaskState, reason: str = "") -> TaskState:
        """Advance task state, checking transition validity and cycle guards (INV-008)."""
        if self.transition_count >= self.max_transitions:
            raise InvalidTaskTransitionError(
                f"Task '{self.task_id}' exceeded max transitions ({self.max_transitions}) - cycle guard (INV-008)"
            )

        if target not in self.VALID_TRANSITIONS.get(self.state, set()):
            raise InvalidTaskTransitionError(
                f"Illegal task transition: cannot move from '{self.state.value}' to '{target.value}'"
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
        """Check if task reached terminal state."""
        return self.state in {TaskState.COMPLETED, TaskState.FAILED}
