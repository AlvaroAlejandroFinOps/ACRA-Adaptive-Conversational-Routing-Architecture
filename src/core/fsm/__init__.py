"""ACRA Finite State Machines Package.

Exposes the 5 decomposed state machines (ADR-004):
- SessionStateMachine (session lifecycle)
- ObjectiveStateMachine (goal decomposition)
- AgentInstanceStateMachine (ephemeral agent runtime)
- TaskStateMachine (DAG task execution)
- HandoffStateMachine (audited inter-agent delegation)
"""

from src.core.agents.lifecycle import (
    AgentInstanceStateMachine,
    InvalidStateTransitionError as InvalidAgentTransitionError,
)
from src.core.fsm.handoff_fsm import (
    HandoffStateMachine,
    InvalidHandoffTransitionError,
)
from src.core.fsm.objective import (
    InvalidObjectiveTransitionError,
    ObjectiveState,
    ObjectiveStateMachine,
)
from src.core.fsm.session import (
    InvalidSessionTransitionError,
    SessionStateMachine,
    SystemState,
)
from src.core.fsm.task import (
    InvalidTaskTransitionError,
    TaskStateMachine,
)

__all__ = [
    "SessionStateMachine",
    "SystemState",
    "InvalidSessionTransitionError",
    "ObjectiveStateMachine",
    "ObjectiveState",
    "InvalidObjectiveTransitionError",
    "AgentInstanceStateMachine",
    "InvalidAgentTransitionError",
    "TaskStateMachine",
    "InvalidTaskTransitionError",
    "HandoffStateMachine",
    "InvalidHandoffTransitionError",
]
