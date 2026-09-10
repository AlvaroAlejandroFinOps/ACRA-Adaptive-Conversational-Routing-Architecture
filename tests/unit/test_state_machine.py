import pytest
from src.core.state_machine import ACRAStateMachine, SystemState, InvalidTransitionError


def test_state_machine_valid_lifecycle():
    sm = ACRAStateMachine()
    assert sm.current_state == SystemState.IDLE

    sm.transition_to(SystemState.INGESTING)
    assert sm.current_state == SystemState.INGESTING

    sm.transition_to(SystemState.CONSOLIDATING)
    sm.transition_to(SystemState.ROUTING_PRO)
    sm.transition_to(SystemState.EXECUTING_PRO)
    sm.transition_to(SystemState.RESPONDING)
    sm.transition_to(SystemState.IDLE)
    assert sm.current_state == SystemState.IDLE


def test_state_machine_invalid_transition_raises():
    sm = ACRAStateMachine()
    with pytest.raises(InvalidTransitionError):
        # Salto ilegal directo de IDLE a EXECUTING_PRO
        sm.transition_to(SystemState.EXECUTING_PRO)
