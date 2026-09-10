import pytest
from src.core.orchestrator import ACRAOrchestrator, OrchestratorState
from src.core.models.mock_models import MockProModel


def test_orchestrator_multi_turn_flow():
    orchestrator = ACRAOrchestrator()
    pro_model = MockProModel()
    session_id = "test_user_session_42"

    # Turno 1: Usuario ambiguo -> debe clarificar en Edge
    res1 = orchestrator.process_turn(session_id, "hola me puedes ayudar con código?")
    assert res1.active_state == OrchestratorState.CLARIFYING
    assert res1.clean_payload is None
    assert "EDGE CLUSTER" in res1.response_text

    # Turno 2: Usuario entrega especificación detallada con restricciones
    prompt2 = (
        "Quiero optimizar un algoritmo de ordenamiento concurrente en Python para un pipeline "
        "distribuido con memoria compartida y baja latencia."
    )
    res2 = orchestrator.process_turn(
        session_id,
        prompt2,
        pro_inference_simulator_fn=lambda p: pro_model.generate(p, is_acra_payload=True).content
    )

    assert res2.active_state == OrchestratorState.DISPATCHING_PRO
    assert res2.clean_payload is not None
    assert res2.ccr > 0.0
    assert "MockPro" in res2.response_text
