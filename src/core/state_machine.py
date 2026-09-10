"""
Máquina de estados formal para el ciclo de vida de una sesión ACRA.
Controla las transiciones válidas y bloquea estados corruptos.
"""

from typing import Set, Dict
from enum import Enum


class SystemState(str, Enum):
    IDLE = "IDLE"
    INGESTING = "INGESTING"
    CLARIFYING = "CLARIFYING"
    CONSOLIDATING = "CONSOLIDATING"
    ROUTING_PRO = "ROUTING_PRO"
    EXECUTING_PRO = "EXECUTING_PRO"
    RESPONDING = "RESPONDING"
    TERMINATED = "TERMINATED"


class InvalidTransitionError(Exception):
    pass


class ACRAStateMachine:
    """Validador determinista de transiciones de estado para ACRA."""

    VALID_TRANSITIONS: Dict[SystemState, Set[SystemState]] = {
        SystemState.IDLE: {SystemState.INGESTING},
        SystemState.INGESTING: {SystemState.CLARIFYING, SystemState.CONSOLIDATING},
        SystemState.CLARIFYING: {SystemState.RESPONDING},
        SystemState.CONSOLIDATING: {SystemState.ROUTING_PRO},
        SystemState.ROUTING_PRO: {SystemState.EXECUTING_PRO},
        SystemState.EXECUTING_PRO: {SystemState.RESPONDING},
        SystemState.RESPONDING: {SystemState.IDLE, SystemState.TERMINATED},
        SystemState.TERMINATED: set(),
    }

    def __init__(self, initial_state: SystemState = SystemState.IDLE):
        self._current_state = initial_state

    @property
    def current_state(self) -> SystemState:
        return self._current_state

    def transition_to(self, new_state: SystemState) -> None:
        """Aplica una transición garantizando invariantes formales."""
        allowed = self.VALID_TRANSITIONS.get(self._current_state, set())
        if new_state not in allowed:
            raise InvalidTransitionError(
                f"Transición ilegal detectada: {self._current_state.value} -> {new_state.value}. "
                f"Permitidas: {[s.value for s in allowed]}"
            )
        self._current_state = new_state

    def reset(self) -> None:
        self._current_state = SystemState.IDLE
